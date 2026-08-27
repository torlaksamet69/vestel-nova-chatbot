# Vestel Nova Chatbot

> Yapay zekâ destekli, doğal dil üzerinden Vestel ürün yorumlarının analiz edilmesini sağlayan chatbot.

Vestel Nova Chatbot, Vestel ürün yorumları üzerinde doğal dil kullanarak veri analizi yapılmasını sağlayan bir **Proof of Concept (PoC)** projesidir.

Projenin temel amacı, kullanıcıların SQL bilgisine ihtiyaç duymadan ürün yorumları, sentiment sonuçları, ürünler, kategoriler ve müşteri geri bildirimleri hakkında sorular sorabilmesini ve BigQuery üzerinde bulunan veriler üzerinden anlamlı cevaplar alabilmesini sağlamaktır.

---

## 🚀 Proje Özeti

Kullanıcı chatbot'a doğal dil kullanarak bir soru yöneltir.

Örneğin:

> "Ürün yorumları iyi olan televizyon modellerini öner."

Chatbot soruyu analiz eder ve gerekli veriye ulaşmak için uygun fonksiyonları kullanır.

Genel akış:

```text
Kullanıcı
    │
    ▼
Doğal Dil Sorusu
    │
    ▼
Gemini
    │
    │ Function Calling
    ▼
Tool / Function
    │
    ▼
BigQuery
    │
    ▼
Analiz Sonucu
    │
    ▼
Gemini
    │
    ▼
Doğal Dil Cevabı
```

Gemini gerektiğinde birden fazla tool'u art arda çağırabilir. Böylece tek bir sorguyla sınırlı kalmadan sorunun gerektirdiği analiz adımlarını gerçekleştirebilir.

---

## 🎯 Projenin Amacı

Proje aşağıdaki ihtiyaçları karşılamayı hedeflemektedir:

- Ürün yorum verilerine doğal dil üzerinden erişebilmek
- SQL bilgisi gerektirmeden veri analizi yapabilmek
- Ürün ve kategori bazlı yorumları analiz edebilmek
- Sentiment sonuçlarını inceleyebilmek
- Ürünleri müşteri yorumlarına göre karşılaştırabilmek
- BigQuery üzerinde hesaplanabilir analizler gerçekleştirebilmek
- Teknik veri sonuçlarını kullanıcı tarafından anlaşılabilir cevaplara dönüştürmek

Proje şu anda **PoC (Proof of Concept)** aşamasındadır ve Vestel ekiplerinin kullanımına yönelik bir çözüm olarak geliştirilmektedir.

---

# 🧠 Function Calling

Projenin temel bileşenlerinden biri Gemini Function Calling mekanizmasıdır.

Gemini yalnızca cevap üreten bir dil modeli olarak kullanılmaz. Aynı zamanda ihtiyaç duyduğu verilere ulaşmak için kendisine tanımlanan fonksiyonları çağırabilir.

Örneğin kullanıcı:

> "Televizyonlarda en yüksek olumlu yorum oranına sahip modeller hangileri?"

diye sorduğunda sistem şu süreci takip edebilir:

```text
1. Kullanıcı sorusu
        ↓
2. Gemini soruyu analiz eder
        ↓
3. Gerekli tool'u belirler
        ↓
4. Tool BigQuery üzerinde çalışır
        ↓
5. Sonuç Gemini'ye gönderilir
        ↓
6. Gemini sonucu yorumlar
        ↓
7. Kullanıcıya doğal dilde cevap verilir
```

Gerektiğinde Gemini birden fazla fonksiyonu arka arkaya kullanabilir.

Bu sayede chatbot, yalnızca statik cevaplar veren bir sistem yerine gerçek veri üzerinde analiz gerçekleştirebilen bir yapıya dönüşür.

---

# 🛠️ Kullanılan Teknolojiler

| Teknoloji | Kullanım Amacı |
|---|---|
| Python | Backend ve chatbot mantığı |
| Google Gemini | Doğal dil işleme ve Function Calling |
| Google BigQuery | Ürün yorum verilerinin sorgulanması |
| FastAPI | Backend REST API |
| Uvicorn | ASGI server |
| Pydantic | API request validation |
| python-dotenv | Environment variable yönetimi |
| Git / GitHub | Versiyon kontrolü ve kaynak kod yönetimi |

---

# 🏗️ Proje Mimarisi

Projenin temel backend mimarisi:

```text
                  ┌──────────────────┐
                  │     Frontend     │
                  │   / API Client   │
                  └────────┬─────────┘
                           │
                           │ HTTP POST
                           ▼
                  ┌──────────────────┐
                  │     FastAPI      │
                  │       API        │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │   Gemini Client  │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │     Gemini       │
                  │ Function Calling │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │      Tools       │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │     BigQuery     │
                  └──────────────────┘
```

---

# 📁 Proje Yapısı

```text
vestel-nova-chatbot/
│
├── .gitignore
├── README.md
├── api.py
├── bigquery_client.py
├── chatbot.py
├── gemini_client.py
├── requirements.txt
└── test_bigquery.py
```

> `.env` dosyası local ortamda bulunur ancak `.gitignore` tarafından Git repository'sine dahil edilmez.

---

## `api.py`

FastAPI backend katmanını içerir.

API'nin oluşturulmasını, CORS yapılandırmasını ve HTTP endpoint'lerini yönetir.

Mevcut endpoint'ler:

```text
GET  /
POST /chat
```

`/chat` endpoint'i kullanıcıdan gelen mesajı alarak Gemini tabanlı chatbot fonksiyonuna iletir.

---

## `chatbot.py`

Chatbot'un temel iş mantığını içerir.

Gemini interaction sürecini ve Function Calling döngüsünü yönetir.

Tool çağrıları sonucunda elde edilen verilerin Gemini'ye tekrar gönderilmesini ve nihai cevabın oluşturulmasını sağlar.

---

## `gemini_client.py`

Gemini client yapılandırmasını ve Gemini API ile ilgili işlemleri içerir.

API key environment variable üzerinden alınır.

Ayrıca Gemini'nin Function Calling mekanizmasının chatbot içerisinde kullanılmasını sağlar.

---

## `bigquery_client.py`

BigQuery bağlantısı ve veri sorgulama işlemlerini içerir.

Ürün yorumları ve analiz sonuçları bu katman üzerinden sorgulanır.

---

## `test_bigquery.py`

BigQuery bağlantısı ve sorgularını test etmek amacıyla kullanılan test dosyasıdır.

---

# 🗄️ Veri Kaynağı

Projenin ürün yorumları tarafında kullandığı temel BigQuery tablosu:

```text
vestel-nova.product_comments.website_sentiment_results
```

Tabloda kullanılan başlıca alanlar:

- `create_time`
- `comment_id`
- `product_id`
- `product_display_name`
- `product_category_name`
- `message_body`
- `sync_time`
- `sentiment_analysis`
- `attribute_sentiment_analysis`
- `dynamic_attributes`
- `static_attributes`
- `store_id`

Sentiment analizinde kullanılan değerler arasında:

```text
Pozitif
Negatif
Karışık
Nötr
```

bulunmaktadır.

> Chatbot yalnızca kendisine tanımlanan veri kaynakları ve araçlar üzerinden analiz gerçekleştirecek şekilde tasarlanmıştır.

---

# 🔍 Örnek Kullanım

### Kullanıcı

```text
Ürün yorumları iyi olan televizyon modeli öner.
```

### Sistem

Gemini soruyu analiz eder ve televizyon kategorisindeki ürünlerin sentiment sonuçlarını incelemek için gerekli tool'ları çağırır.

Örneğin ürün bazında:

```text
Toplam yorum sayısı
Pozitif yorum sayısı
Negatif yorum sayısı
Pozitif yorum oranı
```

gibi metrikler hesaplanabilir.

### Chatbot

Sonuçları teknik SQL çıktısı olarak göstermek yerine kullanıcıya doğal dilde özetler.

Örneğin:

```text
Müşteri yorumlarına göre öne çıkan televizyon modelleri arasında
yüksek pozitif yorum oranına sahip modeller bulunmaktadır.
```

---

# 🔌 API

## GET `/`

Backend'in çalışıp çalışmadığını kontrol etmek için kullanılır.

Örnek response:

```json
{
  "status": "ok",
  "message": "Vestel Yorum Asistanı API çalışıyor."
}
```

---

## POST `/chat`

Kullanıcı mesajını chatbot'a gönderir.

Request:

```json
{
  "message": "Ürün yorumları iyi olan televizyon modellerini öner."
}
```

Response:

```json
{
  "reply": "....",
  "queries": [],
  "thread_id": null
}
```

---

# 🔄 API Akışı

Backend'e gelen bir chat isteği genel olarak şu şekilde işlenir:

```text
POST /chat
     │
     ▼
  FastAPI
     │
     ▼
Gemini Client
     │
     ▼
  Gemini
     │
     ├── Tool çağrısı gerekli mi?
     │          │
     │          ├── Hayır ──────► Cevap
     │          │
     │          └── Evet
     │                 │
     │                 ▼
     │              BigQuery
     │                 │
     │                 ▼
     │            Tool sonucu
     │                 │
     │                 ▼
     │              Gemini
     │                 │
     └─────────────────┘
```

---

# 📊 Yapılabilecek Analizler

Mevcut yapı aşağıdaki türde kullanım senaryolarını destekleyecek şekilde tasarlanmıştır:

- Ürün arama
- Kategori bazlı analiz
- Sentiment analizi
- Ürün karşılaştırması
- Pozitif / negatif yorum oranlarının hesaplanması
- Ürün bazlı yorum yoğunluğu
- Yorumlardan ürün içgörülerinin çıkarılması
- Zaman içerisindeki değişimlerin incelenmesi
- Ürün özellikleriyle ilgili yorumların analiz edilmesi

Analiz kapsamı kullanılan veri ve tanımlanan tool'lara bağlıdır.

---

# 🔐 Environment Variables

API anahtarları kaynak kod içerisinde tutulmamaktadır.

Projenin ana dizininde `.env` dosyası bulunmalıdır:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Python tarafında environment variable:

```python
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

şeklinde okunmaktadır.

### ⚠️ Güvenlik

`.env` dosyası `.gitignore` içerisinde tutulmalıdır.

API key veya Google Cloud credential dosyaları **GitHub repository'sine gönderilmemelidir.**

---

# ⚙️ Kurulum

## 1. Repository'yi klonla

```bash
git clone https://github.com/torlaksamet69/vestel-nova-chatbot.git
```

```bash
cd vestel-nova-chatbot
```

---

## 2. Virtual Environment oluştur

Windows:

```bash
python -m venv .venv
```

Aktifleştirmek için:

```bash
.venv\Scripts\activate
```

---

## 3. Gerekli paketleri yükle

```bash
pip install -r requirements.txt
```

---

## 4. Environment variable'ları tanımla

`.env` dosyası oluştur:

```env
GEMINI_API_KEY=your_gemini_api_key
```

---

## 5. Google Cloud / BigQuery erişimini yapılandır

BigQuery'ye erişebilmek için Google Cloud authentication yapılandırılmalıdır.

Yerel geliştirme ortamında Google Cloud SDK / Application Default Credentials kullanılabilir.

Örneğin:

```bash
gcloud auth application-default login
```

> Kullanılan authentication yöntemi çalıştırma ortamına göre değişebilir.

---

# ▶️ Uygulamayı Çalıştırma

Backend'i Uvicorn ile çalıştırmak için:

```bash
uvicorn api:app --reload
```

Backend varsayılan olarak:

```text
http://127.0.0.1:8000
```

adresinde çalışır.

FastAPI tarafından otomatik oluşturulan API dokümantasyonuna:

```text
http://127.0.0.1:8000/docs
```

adresinden erişilebilir.

Alternatif olarak ReDoc:

```text
http://127.0.0.1:8000/redoc
```

adresinden kullanılabilir.

---

# 🌐 Frontend Entegrasyonu

Backend, frontend uygulamalarının HTTP üzerinden `/chat` endpoint'ine istek gönderebilmesi için REST API olarak tasarlanmıştır.

Frontend'den örnek istek:

```javascript
fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        message: "Televizyonlarda en yüksek olumlu yorum oranına sahip modeller hangileri?"
    })
});
```

Backend tarafında CORS yapılandırması ile aşağıdaki local frontend origin'lerine izin verilmektedir:

```text
http://localhost:5173
http://127.0.0.1:5173
```

---

# 🧪 PoC Durumu

Bu repository, projenin **Proof of Concept (PoC)** aşamasındaki halini içermektedir.

Mevcut PoC ile:

- Gemini entegrasyonu
- Function Calling
- BigQuery veri erişimi
- Doğal dil ile veri sorgulama
- FastAPI REST API
- Tool calling loop
- Frontend / backend iletişimi
- CORS yapılandırması

gibi temel bileşenler çalışır durumdadır.

---

# 🚧 Gelecek Geliştirmeler

Projenin ilerleyen aşamalarında aşağıdaki geliştirmeler değerlendirilebilir.

## Veri Analizi

- Daha gelişmiş ürün karşılaştırmaları
- Attribute-level sentiment analizi
- Zaman serisi analizleri
- Daha gelişmiş trend analizi
- Otomatik insight üretimi

## AI Katmanı

- Daha gelişmiş tool orchestration
- Tool sonuçlarının daha kontrollü işlenmesi
- Cevap doğrulama mekanizmaları
- Daha kapsamlı conversation memory
- Daha gelişmiş kullanıcı bağlamı yönetimi

## Backend

- Authentication / authorization
- API rate limiting
- Logging ve monitoring
- Production ASGI server yapılandırması
- Hata yönetiminin geliştirilmesi
- Unit ve integration testlerinin artırılması

## Frontend

- Gelişmiş chat deneyimi
- Streaming cevaplar
- Tool işlem durumlarının kullanıcıya gösterilmesi
- Analiz sonuçları için grafik ve tablo bileşenleri

## Production

- Cloud ortamına deployment
- Secret management
- CI/CD
- Test coverage
- Production monitoring
- Ölçeklenebilir backend mimarisi

---

# 👥 Hedef Kullanım

Projenin hedef kullanım alanı Vestel ekiplerinin ürün yorumlarından daha hızlı içgörü elde edebilmesidir.

Özellikle teknik olmayan kullanıcıların:

> "Bu kategoride müşteriler en çok hangi konudan şikayet ediyor?"

veya:

> "Hangi televizyon modelleri daha olumlu yorumlara sahip?"

gibi soruları SQL yazmadan sorabilmesi hedeflenmektedir.

---

# 💡 Örnek Kullanım Senaryoları

### Ürün Önerisi

```text
Ürün yorumları iyi olan televizyon modeli öner.
```

### Kategori Analizi

```text
Buzdolaplarında müşterilerin en çok şikayet ettiği konular neler?
```

### Sentiment Analizi

```text
Televizyon kategorisindeki yorumların sentiment dağılımı nedir?
```

### Ürün Karşılaştırması

```text
55UV9750 ile 55UG9750 modellerinin müşteri yorumlarını karşılaştır.
```

### Zaman Bazlı Analiz

```text
Son dönemde televizyon yorumlarında olumlu veya olumsuz bir değişim var mı?
```

Bu soruların cevapları BigQuery'deki gerçek veriler üzerinden gerçekleştirilen analizlere dayanır.

---

# 📌 Proje Durumu

| Alan | Durum |
|---|---|
| Proje tipi | Proof of Concept |
| Backend | FastAPI |
| ASGI Server | Uvicorn |
| LLM | Google Gemini |
| Veri kaynağı | Google BigQuery |
| API | REST |
| Function Calling | Aktif |
| CORS | Yapılandırılmış |
| Environment | Local Development |
| Kaynak kod | GitHub |

---

# 🔒 Güvenlik Notu

Repository içerisinde aşağıdaki hassas bilgilerin bulunmaması gerekir:

- Gemini API key
- Google Cloud service account credentials
- `.env` dosyası
- Kullanıcıya özel erişim bilgileri
- Gizli kurum bilgileri

Bu bilgiler environment variable veya uygun secret management çözümleri üzerinden sağlanmalıdır.

---

# 📄 License

Bu proje Vestel Geleceğe Bi' Adım Staj Programı kapsamında geliştirilmiş bir PoC çalışmasıdır.

Kaynak kodun kullanım ve paylaşım koşulları proje sahibi / ilgili kurum politikalarına tabidir.