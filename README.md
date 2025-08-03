# IELTS Listening Practice Web Application

Bu uygulama, IELTS Listening sınavı için pratik yapmanıza yardımcı olan bir web uygulamasıdır.

## Özellikler

- **AI Destekli İçerik Üretimi**: Gemini AI kullanarak IELTS Listening Part 1 tarzında diyaloglar oluşturur
- **Text-to-Speech**: Google Cloud TTS ile diyalogları ses dosyasına çevirir
- **Çoktan Seçmeli Sorular**: Her diyalog için 4 seçenekli sorular üretir
- **Anında Geri Bildirim**: Cevabınızı kontrol edebilirsiniz

## Kurulum

1. Gerekli Python paketlerini yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. Google Cloud Text-to-Speech için kimlik doğrulama ayarlayın (opsiyonel)

## Kullanım

1. Uygulamayı başlatın:
   ```bash
   python app.py
   ```

2. Web tarayıcınızda şu adresi açın:
   ```
   http://localhost:5000
   ```

3. "Generate New Listening" butonuna tıklayarak yeni bir listening örneği oluşturun

4. Ses dosyasını dinleyin ve soruyu cevaplayın

5. Cevabınızı kontrol edin

## Dosya Yapısı

- `app.py` - Flask web sunucusu
- `config.py` - Gemini API anahtarı
- `listening_generator.py` - AI ile listening içeriği üretimi
- `google_tts_service.py` - Text-to-Speech servisi
- `templates/frontend.html` - Web arayüzü
- `static/audio/` - Ses dosyaları

## API Endpoints

- `GET /` - Ana sayfa
- `GET /generate-listening` - Yeni listening örneği oluşturur

## Teknolojiler

- **Backend**: Flask (Python)
- **AI**: Google Gemini API
- **Text-to-Speech**: Google Cloud TTS
- **Frontend**: HTML, CSS, JavaScript 