from src.tools.system_ops import set_volume
from src.tools.process_ops import launch_app, close_app
from src.tools.file_ops import safe_delete
from src.tools.chat_ops import chat
from src.tools.os_terminal import run_powershell
from src.core.logger import get_logger
import tkinter.messagebox as messagebox

logger = get_logger(__name__)

class Executor:
    """
    LLM'in verdiği kararları (JSON objesini) okur, 
    içindeki 'action' keyine göre ilgili Python fonksiyonunu bulur ve 
    'params' değeri ile o fonksiyonu koşturur.
    """
    def __init__(self):
        # Yetki (Action) Haritası 
        # LLM'in dizebileceği fonksiyon isimlerini gerçek Python objelerine (referanslarına) bağlar.
        self.action_map = {
            "set_volume": set_volume,
            "launch_app": launch_app,
            "close_app": close_app,
            "safe_delete": safe_delete,
            "chat": chat,
            "run_powershell": run_powershell
        }
        
    def execute(self, plan: dict, auto_approve: bool = False) -> dict:
        """
        Gelen JSON planını yürütür. Arayüzden gelen Otonomi yetkisine bakar.
        Örn: plan = {"action": "set_volume", "params": {"level": 50}}
        """
        action_name = plan.get("action")
        
        # 1. Hata Kontrolü
        if action_name == "error":
            logger.error(f"Executor hataya düştü: {plan.get('message', 'Bilinmeyen Hata')}")
            return plan

        # 2. Yeteneği Anlamama Durumu
        if action_name == "none" or not action_name:
            msg = plan.get("message", "Ajan bu isteği nasıl yerine getireceğini bilemedi.")
            logger.warning(f"Ajan Eylemsiz Kaldı: {msg}")
            return {"status": "info", "message": msg}

        # 3. Yürütme Motoru (Dispatcher)
        if action_name in self.action_map:
            func = self.action_map[action_name]
            params = plan.get("params", {})
            logger.info(f"Komut Yürütülüyor: {action_name} | Parametreler: {params}")
            
            # 4. GÜVENLİK KONTROLÜ (Security Gate)
            if action_name in ["close_app", "safe_delete", "run_powershell"]:
                
                # Otonomi Anahtarı Açık İse Sorgusuz Sualsiz Geç!
                if auto_approve:
                    logger.warning(f"TAM OTONOMİ DEVREDE! Güvenlik kalkanı aşılarak {action_name} doğrudan çalıştırılıyor.")
                else:
                    target = params.get("app_name") or params.get("path") or params.get("command") or "Bilinmeyen Hedef"
                    msg_text = f"Dikkat!\nAjan şu Kritik İşlemi/Komutu çalıştırmak istiyor:\n\n{action_name}\n-> {target}\n\nOnaylıyor musunuz?"
                    
                    # Kullanıcıya Evet/Hayır penceresi aç
                    user_consent = messagebox.askyesno("Kritik İşlem Onayı", msg_text)
                    if not user_consent:
                        logger.warning(f"Kullanıcı eylemi reddetti: {action_name}")
                        return {"status": "info", "message": "İşlem sizin tarafınızdan iptal edildi."}
            
            try:
                # Python dilindeki dinamik argüman çözme (kwargs) yöntemi (**params) kullanılarak 
                # fonksiyon tetiklenir.
                result = func(**params)
                return result
                
            except Exception as e:
                logger.error(f"Fonksiyon '{action_name}' çalıştırılırken hata oluştu: {str(e)}")
                return {"status": "error", "message": f"{action_name} çalışırken çöktü. Hata: {str(e)}"}
        else:
            msg = f"'{action_name}' adında bir araç (tool) bulunamadı veya action_map içine tanımlanmadı."
            logger.error(msg)
            return {"status": "error", "message": msg}
