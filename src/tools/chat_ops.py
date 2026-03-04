from src.core.logger import get_logger

logger = get_logger(__name__)

def chat(message: str) -> dict:
    """
    Ajanın sadece sohbet etmek veya ek soru sormak istediği anlarda tetiklenir.
    Sisteme dokunan herhangi bir fiziksel eylem yapmaz, sadece UI'a mesaj döner.
    """
    logger.info(f"Sohbet Mesajı Gönderiliyor: {message}")
    # Arayüzdeki txt_log'a eklenecek olan message dictionary halinde dönülüyor
    return {"status": "success", "message": message}
