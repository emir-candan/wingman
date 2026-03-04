import customtkinter as ctk
import threading
import asyncio
from src.core.llm_router import LLMRouter
from src.core.parser import extract_json
from src.core.executor import Executor
from src.tools.registry import get_tools_schema
from src.core.logger import get_logger

logger = get_logger(__name__)

# Görsel tema ayarları
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Temel Pencere Ayarları
        self.title("Wingman 🦅")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Sistemi yönetecek çekirdek modüller ayağa kalkıyor
        self.router = LLMRouter()
        self.executor = Executor()
        self.schema = get_tools_schema()
        
        # Uygulamanın asenkron işlemleri (Ollama'ya gidiş) arka planda yapabilmesi için
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_loop, daemon=True).start()

        self._build_ui()
        logger.info("Wingman Kullanıcı Arayüzü başlatıldı.")

    def start_loop(self):
        """Asenkron döngüyü arka plan thread'de sonsuza dek çalıştırır."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _build_ui(self):
        """Arayüz bileşenlerini konumlandırır."""
        # Üst Panel: Otonomi Anahtarı
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.switch_autonomy = ctk.CTkSwitch(
            top_frame, 
            text="Tam Otonomi Modu (İzin İsteme)",
            onvalue=True,
            offvalue=False
        )
        self.switch_autonomy.pack(side="right")
        
        # Orta Panel: Sekmeler (Sohbet / Terminal)
        self.tabview = ctk.CTkTabview(self, width=380, height=360)
        self.tabview.pack(pady=(5, 5), padx=10)
        
        self.tabview.add("Sohbet")
        self.tabview.add("Terminal Log")
        
        # 1. Sohbet Sekmesi
        self.txt_log = ctk.CTkTextbox(self.tabview.tab("Sohbet"), width=360, height=300, state="disabled")
        self.txt_log.pack(pady=5, padx=5)
        
        # 2. Terminal Log Sekmesi
        self.txt_cmd_log = ctk.CTkTextbox(self.tabview.tab("Terminal Log"), width=360, height=300, state="disabled", text_color="#00FF00", font=("Consolas", 12))
        self.txt_cmd_log.pack(pady=5, padx=5)
        self.txt_cmd_log.insert("end", "> Terminal izleme başlatıldı...\n")
        
        # Alt Panel: Giriş Kutusu Çerçevesi
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Input Kutusu
        self.entry_msg = ctk.CTkEntry(input_frame, placeholder_text="Komut girin...", width=290)
        self.entry_msg.pack(side="left", padx=(0, 5))
        self.entry_msg.bind("<Return>", lambda event: self.send_message()) # Enter tuşunu bağla
        
        # Gönder Butonu
        self.btn_send = ctk.CTkButton(input_frame, text="Gönder", width=85, command=self.send_message)
        self.btn_send.pack(side="left")

    def append_log(self, text: str, sender: str = "Ajan"):
        """Sohbet alanına yazılan yazıları ekler."""
        self.txt_log.configure(state="normal")
        if sender:
            self.txt_log.insert("end", f"[{sender}] {text}\n\n")
        else:
            self.txt_log.insert("end", f"{text}\n\n")
        
        self.txt_log.see("end") # Ekranı hep en alta (yeni mesaja) kaydır
        self.txt_log.configure(state="disabled")
        
    def append_cmd_log(self, command: str, output: str):
        """Arka plan Terminal sekmesine komut çıktılarını ekler."""
        self.txt_cmd_log.configure(state="normal")
        self.txt_cmd_log.insert("end", f"\n> {command}\n{output}\n")
        self.txt_cmd_log.see("end")
        self.txt_cmd_log.configure(state="disabled")

    def send_message(self):
        """Gönder butonuna (veya Enter'a) basıldığında tetiklenir."""
        user_text = self.entry_msg.get().strip()
        if not user_text:
            return
            
        self.entry_msg.delete(0, "end") # inputu temizle
        self.btn_send.configure(state="disabled") # spam engelle
        self.append_log(user_text, "Siz")
        
        self.append_log("Düşünüyor...", "Sistem")
        
        # İşi ana Thread'den devredip asenkron task havuzuna yolluyoruz. 
        # Böylece UI donmuyor. Bekleme ekranı kalmıyor.
        asyncio.run_coroutine_threadsafe(self._process_message(user_text), self.loop)

    async def _process_message(self, text: str, is_system_feedback: bool = False):
        """Modelden asenkron olarak sonuç bekler ve işler."""
        try:
            # 1. Beyni Tetikle
            raw_response = await self.router.get_action_plan(text, self.schema)
            logger.info(f"LLM Ham Yanıt: {raw_response}")
            
            # 2. JSON Çıkar
            plan_obj = extract_json(raw_response)
            logger.info(f"Ayrıştırılan Plan: {plan_obj}")
            
            # Switch açıldıysa auto_approve True olarak executor'a yollanır
            auto_approve = bool(self.switch_autonomy.get())
            
            # 3. Yürütücüye Gönder
            result = self.executor.execute(plan_obj, auto_approve=auto_approve)
            
            action_name = plan_obj.get("action", "none")
            
            # Eğer powershell kullanıldıysa Terminal sekmesini besle
            if action_name == "run_powershell":
                self.after(0, self.append_cmd_log, plan_obj.get("params", {}).get("command", ""), result.get("message", ""))
                
            # 4. Arayüze Yansıtma ve Otonomi Döngüsü (Re-Act / Chain of Thought)
            if action_name in ["chat", "none", "error"]:
                # İşlem bir eylem gerektirmeyen (son) noktaya ulaştı. Döngüyü kır ve kullanıcıya dön.
                self.after(0, self._update_ui_after_process, result.get("message", "İşlem Tamamlandı."))
            else:
                # Otonomi: Bir OS eylemi (powershell, app_open vs) yapıldıysa, sonucu Ajanın kendisine rapor et
                # Ve sıradaki hamleyi yapmasını bekle (UI kilitli kalmaya devam eder, süreç bitene kadar).
                system_feedback = f"[SİSTEM ÇIKTISI]: '{action_name}' eylemi '{result.get('status')}' olarak sonuçlandı.\nÇıktı Detayı: {result.get('message')}\n\n-> Görev tamamlandıysa 'chat' aracı ile bana bilgi ver. Eğer hata aldıysan veya işlemi sürdürmen gerekiyorsa yeni bir 'action' yolla."
                
                logger.info(f"Otonomi Zinciri Tetiklendi. Ajan Sonucu Değerlendiriyor...")
                asyncio.run_coroutine_threadsafe(self._process_message(system_feedback, is_system_feedback=True), self.loop)
                
        except Exception as e:
            logger.error(f"Mesaj işleme hatası: {str(e)}")
            self.after(0, self._update_ui_after_process, f"Zihinsel Hata: {str(e)}")

    def _update_ui_after_process(self, message: str):
        """İşlem bittikten sonra butonu açar ve sonucu ekrana yazar."""
        # Düşünüyor... yazısını değiştirmek yerine yeni girdi ekliyoruz
        self.append_log(message, "Ajan")
        self.btn_send.configure(state="normal")
