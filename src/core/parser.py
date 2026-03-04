import json
import re
from src.core.logger import get_logger

logger = get_logger(__name__)

def extract_json(llm_response: str) -> dict:
    """
    LLM'den dönen karmaşık metin bloğunun içinden (Markdown kod bloğu vs.) 
    sadece çalıştırılabilir JSON objesini çıkarıp Python dict formatına çevirir.
    
    Args:
        llm_response (str): Ollama/OpenAI'den gelen RAW metin.
        
    Returns:
        dict: Başarılı çıkarılmış JSON nesnesi. (Başarısızlık durumunda bir hata dict döner)
    """
    try:
        # Eğer response doğrudan temiz bir JSON ise (süsleme yoksa) hemen dene.
        llm_response = llm_response.strip()
        if llm_response.startswith("{") and llm_response.endswith("}"):
            return json.loads(llm_response)
        
        # Eğer bir ```json ... ``` markdown kod bloğu içine hapsolmuşsa Regex ile onu yakala:
        match = re.search(r'```json\n(.*?)\n```', llm_response, re.DOTALL)
        if match:
            extracted_text = match.group(1).strip()
            return json.loads(extracted_text)
            
        # Sadece ``` kullanılma ihtimaline karşı genel yakalama:
        match_general = re.search(r'```(.*?)```', llm_response, re.DOTALL)
        if match_general:
            extracted_text = match_general.group(1).strip()
            # Bazen başında 'json' kelimesi kalabilir
            if extracted_text.startswith("json"):
                extracted_text = extracted_text[4:].strip()
            return json.loads(extracted_text)
            
        # 4. JSON Objelerini kaba kuvvetle (Brute-Force Regex) arama
        # Metin içinde { ile başlayıp } ile biten en büyük JSON bloğunu yakala
        match_braces = re.search(r'\{.*\}', llm_response, re.DOTALL)
        if match_braces:
            try:
                candidate = match_braces.group(0)
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass # Yakalanan blok JSON değilse sonrakine devam et

        # Hiçbirine uymuyorsa hata fırlat
        logger.error(f"Geçerli bir JSON formatı bulunamadı. Gelen Metin: {llm_response[:100]}...")
        
        # Son Kurtarma Operasyonu (Fault Tolerance): LLM bazen sadece JSON döner ama sonuna '}' koymayı unutabilir.
        if llm_response.strip().startswith("{") and not llm_response.strip().endswith("}"):
            try:
                forced_json = llm_response.strip() + "}"
                return json.loads(forced_json)
            except json.JSONDecodeError:
                pass

        return {"action": "error", "message": "Ajanın yanıtı JSON formatında değildi veya ayıklanamadı."}

    except json.JSONDecodeError as decode_error:
        logger.error(f"JSON Çözümleme Hatası tespit edildi: {str(decode_error)}")
        return {"action": "error", "message": "Ajan yapısal olarak bozuk bir JSON döndü."}
    except Exception as e:
        logger.error(f"Parser tarafında bilinmeyen bir hata oluştu: {str(e)}")
        return {"action": "error", "message": f"Parser iç Hatası: {str(e)}"}
