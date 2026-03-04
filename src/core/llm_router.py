import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from src.core.logger import get_logger

logger = get_logger(__name__)

# dotenv'i yükle (.env dosyasını oku)
load_dotenv()

# Ayarları çek
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "True").lower() == "true"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Sistemin ana beynini yönetecek olan kural seti
def get_dynamic_system_prompt() -> str:
    """Çalışma anında sistemdeki ortam değişkenlerini alarak prompt'u oluşturur."""
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    onedrive_desktop = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop')
    if os.path.exists(onedrive_desktop):
        desktop_path = onedrive_desktop
        
    return f"""Sen 'Wingman' adında OTONOM bir bilgisayar asistanısın.
GÖREVİN: Kullanıcının niyetini anla, elindeki ARAÇLARDAN (TOOLS) en uygun olanı seçerek SADECE JSON dön.

--- SİSTEM BİLGİSİ (ÇOK ÖNEMLİ) ---
İşletim Sistemi: Windows
Kullanıcı Dizini: {os.environ.get('USERPROFILE')}
Masaüstü Dizini: {desktop_path} (Aramalarını ve dosya operasyonlarını bu tam yolda yapmalısın)

ANA KURALLAR (KESİNLİKLE UYULACAK):
1. YALNIZCA SANA BİLDİRİLEN ARAÇLARI KULLANABİLİRSİN. Listede olmayan hiçbir aracı (action) uydurma.
2. SOHBET / EKSİK BİLGİ: Kullanıcı eksik bilgi verdiyse ("kapat" ama neyi?) veya sohbet ediyorsa, "chat" aracıyla yanıt ver.
3. KÖR OTONOMİ YASAKTIR: Eğer run_powershell ile KÖRLEMESİNE BİR DOSYA/KLASÖR SİLMEN veya DEĞİŞTİRMEN İSTENİYORSA (Örn: Remove-Item), BUNU İLK ADIMDA ASLA YAPMA.
   - ÖNCE "run_powershell" aracı ile Get-ChildItem (ls) veya Test-Path kullanarak hedefin orada olduğundan dizini okuyarak EMİN OL. (Örn: `Get-ChildItem '{desktop_path}' -Filter ...`)
   - Ancak sen okumayı bitirip kullanıcı sana "Evet sil" derse silme komutunu gönder. İkinci bir emre kadar ASLA Remove-Item/del komutu BİRLEŞTİREREK kullanma.
4. Yanıtın SADECE ve SADECE geçerli bir JSON objesi olmalıdır. Asla Markdown (```) kullanma, fazladan düz metin ekleme.
5. JSON Formatı: {{"action": "arac_ismi", "params": {{"parametre_adi": "deger"}} }}
"""

class LLMRouter:
    def __init__(self):
        # Eğer yerel LLM (Ollama) kullanılacaksa, base_url değiştirilir ve dummy api key verilir.
        if USE_LOCAL_LLM:
            self.client = AsyncOpenAI(
                base_url=OLLAMA_HOST,
                api_key="ollama"  # Ollama API key istemediğinden dummy koyduk.
            )
            self.model = OLLAMA_MODEL
        else:
            self.client = AsyncOpenAI(
                api_key=OPENAI_API_KEY,
                base_url="https://api.groq.com/openai/v1" # Groq API Uç Noktası
            )
            self.model = "openai/gpt-oss-120b" # Groq için istenen model
            
        # Bağlam kopukluğunu engellemek için ajana verilen Kısa Süreli Bellek (Memory)
        self.history = []
            
    async def get_action_plan(self, user_message: str, tools_schema: list) -> str:
        """
        Kullanıcının mesajını ve tool'ları LLM'e yollayıp JSON string olarak yanıt alır.
        
        Args:
            user_message (str): Kullanıcının yazdığı metin.
            tools_schema (list): Kayıtlı fonksiyonların JSON şeması listesi.
            
        Returns:
            str: Modelden gelen RAW yanıt (ideal olarak içinde JSON barındırır).
        """
        # Sistemin o an bildiği tüm araçlar prompta enjekte ediliyor.
        schema_text = str(tools_schema)
        
        dynamic_system_prompt = get_dynamic_system_prompt()
        full_prompt = f"{dynamic_system_prompt}\n\nKullanılabilir Araçlar (Araç seçtiğinde 'action' için adını kullan):\n{schema_text}"
        
        # 1- Sistem emri
        messages = [{"role": "system", "content": full_prompt}]
        
        # 2- Eski konuşma hatırlatmaları (Context)
        messages.extend(self.history)
        
        # 3- Yeni sorulan soru
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1 # Daha deterministik (kesin/kararlı) çıktılar için düşük ısı.
            )
            raw_response = response.choices[0].message.content
            
            # İşlem bittikten sonra ajanın ve kullanıcının dediklerini hafızaya yaz
            self.history.append({"role": "user", "content": user_message})
            self.history.append({"role": "assistant", "content": raw_response})
            
            # Token patlaması olmaması için eski mesajları sil (Son 10 mesaj = 5 konuşma döngüsü kalır)
            if len(self.history) > 10:
                self.history = self.history[-10:]
                
            return raw_response
        except Exception as e:
            logger.error(f"LLM Bağlantı Hatası: {str(e)}")
            return f'{{"action": "error", "message": "LLM bağlantı hatası: {str(e)}"}}'
