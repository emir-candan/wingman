from AppOpener import open as app_open, close as app_close
from src.core.logger import get_logger

logger = get_logger(__name__)

def launch_app(app_name: str) -> dict:
    """Windows'ta yüklü olan belirtilen uygulamayı açar."""
    try:
        app_open(app_name, match_closest=True, throw_error=True)
        logger.info(f"Uygulama BAŞLATILDI: {app_name}")
        return {"status": "success", "message": f"{app_name} uygulaması başlatıldı."}
    except Exception as e:
        logger.error(f"Uygulama açılamadı: {app_name} | Hata: {str(e)}")
        return {"status": "error", "message": f"'{app_name}' bulunamadı veya açılamadı."}

def close_app(app_name: str) -> dict:
    """Belirtilen uygulamanın sürecini (process) sonlandırır."""
    try:
        app_close(app_name, match_closest=True, throw_error=True)
        logger.info(f"Uygulama KAPATILDI: {app_name}")
        return {"status": "success", "message": f"{app_name} uygulaması kapatıldı."}
    except Exception as e:
        logger.error(f"Uygulama kapatılamadı: {app_name} | Hata: {str(e)}")
        return {"status": "error", "message": f"'{app_name}' kapatılamadı. Belki zaten kapalıdır."}
