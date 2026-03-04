# src/tools/registry.py

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Bilgisayarın ses seviyesini ayarlar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {
                        "type": "integer",
                        "description": "0 ile 100 arasında bir ses yüzdesi. Örn: 50"
                    }
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "launch_app",
            "description": "Bilgisayarda yüklü olan bir uygulamayı, oyunu veya programı başlatır/açar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Açılacak uygulamanın adı (Örn: 'Project Zomboid', 'Google Chrome', 'Spotify')"
                    }
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_app",
            "description": "Açık olan bir uygulamayı veya programı zorla kapatır.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Kapatılacak uygulamanın adı (Örn: 'chrome', 'spotify', 'zomboid')"
                    }
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "safe_delete",
            "description": "Bir dosyayı Çöp Kutusuna göndererek güvenli bir şekilde siler. Kalıcı silmez.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Silinecek dosyanın tam adresi (Örn: 'C:\\Users\\Desktop\\test.txt')"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "chat",
            "description": "Kullanıcıya doğrudan Türkçe bir yanıt (mesaj) vermek veya soru sormak için kullanılır. Herhangi bir eylem yapılmayıp sadece sohbet edilecekse veya ek bilgi (örneğin 'Hangi uygulamayı kapatmak istiyorsunuz?') istendiğinde bu seçilmeli.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Kullanıcıya gösterilecek olan Türkçe metin tabanlı yanıt veya soru."
                    }
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_powershell",
            "description": "Windows PowerShell komutlarını çalıştırır. Sınırsız yetki sunar. Kayıt defterini okumak, dosyalara erişmek, bilgi almak, ayarları incelemek ve Windows yapısında arıza tespiti yapmak için terminali komut satırı ile yönetebilirsin.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Çalıştırılacak tek satırlık powershell kodu. (Örn: 'Get-Process | Where-Object Name -match \"chrome\"' veya 'cat C:\\Windows\\log.txt')"
                    }
                },
                "required": ["command"]
            }
        }
    }
]

def get_tools_schema() -> list:
    """LLM'e gönderilmek üzere tüm araçların şemasını döner."""
    return TOOLS_SCHEMA
