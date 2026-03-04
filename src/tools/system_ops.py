# src/tools/system_ops.py
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
import comtypes
from comtypes import CLSCTX_ALL
from src.core.logger import get_logger

logger = get_logger(__name__)

def set_volume(level: int) -> dict:
    """
    Windows sistem sesini belirtilen yüzdeye (0-100) ayarlar.
    
    Args:
        level (int): 0 ile 100 arasında hedef ses yüzdesi.
        
    Returns:
        dict: İşlem sonucunu içeren JSON (dictionary) nesnesi.
    """
    try:
        level = int(level) # LLM string dönebilme ihtimaline karşı cast
        if not (0 <= level <= 100):
            return {"status": "error", "message": "Ses seviyesi 0 ile 100 arasında olmalıdır."}

        # Arka plan Thread'lerinde pycaw çağrıldığında COM objeleri baştan ilklendirilmelidir.
        comtypes.CoInitialize()

        # Pycaw endpoint ayarları (Hoparlör referansı)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        # Pycaw sesi decibel scalar mantığında (0.0 ile 1.0) alır. 
        # Matematiksel çevirim (yüzdeden scala'ya)
        scalar_level = float(level) / 100.0
        volume.SetMasterVolumeLevelScalar(scalar_level, None)
        
        logger.info(f"Sistem sesi başarıyla %{level} olarak ayarlandı.")
        return {"status": "success", "message": f"Sistem sesi %{level} yapıldı."}

    except Exception as e:
        logger.error(f"Ses ayarlanırken hata oluştu: {str(e)}")
        return {"status": "error", "message": f"Ses değiştirilirken işletim sistemi hatası bağıntısı koptu: {str(e)}"}
