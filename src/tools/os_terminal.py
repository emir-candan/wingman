import subprocess
from src.core.logger import get_logger

logger = get_logger(__name__)

def run_powershell(command: str) -> dict:
    """
    Belirtilen powershell komutunu çalıştırır ve terminal çıktısını döner.
    Bu araç ajanın sonsuz yeteneğe sahip olmasını sağlar.
    """
    try:
        logger.info(f"PowerShell Komutu Çalıştırılıyor: {command}")
        
        # subprocess.run ile powershell çalıştır, Windows'a özgü pencere çıkmasını engelle
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30, # En fazla 30 saniye bloklasın (Aksi takdirde UI donar)
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        # Başarılı dönüş kodu 0'dır
        if result.returncode == 0:
            if not output:
                output = "(Komut başarılı ama bir çıktı dönmedi)"
            return {"status": "success", "message": f"Komut başarıyla çalıştı. Terminal Çıktısı:\n{output}"}
        else:
            logger.warning(f"PowerShell Komutu Hata Döndü: {error}")
            return {"status": "error", "message": f"Komut çalıştırıldı ancak işletim sistemi hata verdi:\n{error}\n\nStandart Çıktı:\n{output}"}
            
    except subprocess.TimeoutExpired:
        logger.error(f"Komut zaman aşımına uğradı: {command}")
        return {"status": "error", "message": "Komut 30 saniye içinde bitemedi ve zorla durduruldu."}
    except Exception as e:
        logger.error(f"PowerShell aracı çöktü: {str(e)}")
        return {"status": "error", "message": f"Terminal Başlatılamadı Hatası: {str(e)}"}
