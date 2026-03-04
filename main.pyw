import sys
import os

# Sisteme src klasörünü tanıtıyoruz ki modülleri sorunsuz bulabilsin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.app_window import AppWindow
from src.core.logger import get_logger

logger = get_logger("main")

def main():
    try:
        logger.info("Wingman başlatılıyor...")
        app = AppWindow()
        
        # Tray Icon (Sistem Tepsisi) Özelliği - Opsiyonel Eklenti
        # app.protocol('WM_DELETE_WINDOW', lambda: app.withdraw()) # X'e basınca gizle
        
        # Arayüz döngüsünü başlat
        app.mainloop()
    except Exception as e:
        logger.error(f"Uygulama başlatılırken kritik hata: {str(e)}")

if __name__ == "__main__":
    main()
