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
SYSTEM_PROMPT = """Sen 'Wingman' adında OTONOM bir bilgisayar asistanısın.
GÖREVİN: Kullanıcının niyetini anla, elindeki ARAÇLARDAN (TOOLS) en uygun olanı seçerek SADECE JSON dön.

ANA KURALLAR (KESİNLİKLE UYULACAK):
1. YALNIZCA SANA BİLDİRİLEN ARAÇLARI KULLANABİLİRSİN. Listede olmayan hiçbir aracı (action) uydurma.
2. SOHBET VE EKSİK BİLGİ: Eğer kullanıcı sohbet ediyorsa, eksik bilgi veriyorsa (örn: "kapat" ama neyi?) veya sorusu mevcut OS araçlarıyla yapılamıyorsa, KESİNLİKLE "chat" aracını kullanarak Türkçe yanıt dön veya ondan detay iste.
3. OTONOMİ VE POWERSHELL: Elinde özel bir araç yoksa ancak kullanıcı sistemde bir eylem istiyorsa (Örn: "Şu hatayı analiz et", "Kayıt defterine bak", "IP adresimi bul"), "run_powershell" aracını kullanarak kendi komutunu yaz ve sistemde çalıştırıp öğren.
4. Yanıtın SADECE ve SADECE geçerli bir JSON objesi olmalıdır. Asla Markdown (```) kullanma, fazladan düz metin ekleme.
5. JSON Formatı: {"action": "arac_ismi", "params": {"parametre_adi": "deger"}}
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
            self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            self.model = "gpt-4o-mini" # Standart OpenAI Modeli
            
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
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nKullanılabilir Araçlar (Araç seçtiğinde 'action' için adını kullan):\n{schema_text}"
        
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
