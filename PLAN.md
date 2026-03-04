# 🦅 Wingman Projesi 10 Adımlık Detaylı Geliştirme Planı

Bu belge, Wingman OS Agent projesini baştan sona tamamlamak için izleyeceğimiz rotayı belirler.

- [x] **Adım 1: Temel Ortam Kurulumu ve Konfigürasyon**
  - **`requirements.txt`**: Projenin çalışması için gereken Python kütüphaneleri eklenecek.
  - **`.env`**: Yerel LLM ayarları (Ollama) ve API anahtarları tanımlanacak.

- [x] **Adım 2: Loglama ve Alt Yapı Ayarları**
  - **`logs/`**: Sistem loglarını tutacak mekanizma yapılandırılacak.
  - **`src/__init__.py`** dosyaları modüllerin birbirini görmesi için ayarlanacak.

- [x] **Adım 3: Kas Katmanı (Tool Registry)**
  - **`src/tools/registry.py`**: Ajanın yetenek havuzunu (hangi fonksiyonları çalıştırabileceğini) LLM'in anlayacağı "JSON Schema" sözlüğünde (`TOOLS_SCHEMA`) tanımlayacağız.

- [x] **Adım 4: Kas Katmanı (System Operations & Ses Kontrolü)**
  - **`src/tools/system_ops.py`**: İlk fiziksel eylemimiz olan sesi ayarlama (`set_volume`) fonksiyonu yazılacak.

- [x] **Adım 5: Beyin Katmanı (LLM İletişimi)**
  - **`src/core/llm_router.py`**: Ollama API ve OpenAI ile asenkron bir şekilde iletişim kuracak Python sınıfı yazılacak.

- [x] **Adım 6: Beyin Katmanı (Yanıt Çözümleme - Parser)**
  - **`src/core/parser.py`**: LLM'in döneceği muhtemel JSON cevabını, metin bloğu içinden güvenli bir şekilde alacak fonksiyonlar yazılacak.

- [x] **Adım 7: Beyin Katmanı (Yürütücü - Executor)**
  - **`src/core/executor.py`**: Parser'dan gelen JSON verisini okuyup doğru aracı (Tool) çalıştıran yapıyı geliştireceğiz.

- [x] **Adım 8: Arayüz Katmanı (CustomTkinter UI)**
  - **`src/ui/app_window.py`**: CustomTkinter kullanarak sohbet arayüzünü (Chat UI) inşa edeceğiz.

- [x] **Adım 9: Ana Giriş (Main Loop) ve Entegrasyon**
  - **`main.pyw`**: Uygulamayı başlatacak olan dosya hazırlanacak. UI ve arka plan sistemleri bağlanacak.

- [x] **Adım 10: Ek Araçlar ve Güvenlik**
  - **`src/tools/process_ops.py` & `src/tools/file_ops.py`**: Uygulama açma, kapatma ve güvenli dosya silme işlemleri eklenecek. Kritik işlemler için onay (MessageBox) mekanizması kurulacak.
