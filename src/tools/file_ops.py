from send2trash import send2trash
import os
from src.core.logger import get_logger

logger = get_logger(__name__)

def safe_delete(path: str) -> dict:
    """Belirtilen dosyayı kalıcı silmek yerine Çöp Kutusuna gönderir."""
    try:
        if not os.path.exists(path):
            return {"status": "error", "message": f"Belirtilen yol bulunamadı: {path}"}
            
        # Güvenlik Kontrolleri
        abs_path = os.path.abspath(path).lower()
        if "c:\\windows" in abs_path or "c:\\program files" in abs_path:
            logger.warning(f"Kritik dizinde silme engellendi: {path}")
            return {"status": "error", "message": "Güvenlik kuralı: Sistem klasörlerinden dosya silinemez!"}

        send2trash(path)
        logger.info(f"Dosya çöp kutusuna taşındı: {path}")
        return {"status": "success", "message": f"{path} çöp kutusuna gönderildi."}
        
    except Exception as e:
        logger.error(f"Dosya silinemedi: {path} | Hata: {str(e)}")
        return {"status": "error", "message": f"Dosya silinirken hata: {str(e)}"}
