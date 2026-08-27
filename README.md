# Vestel Nova Chatbot

> AI-powered chatbot for querying and analyzing Vestel product review data using natural language.

Vestel Nova Chatbot, Vestel ürün yorumları üzerinde doğal dil ile veri analizi yapılmasını sağlayan bir Proof of Concept (PoC) projesidir.

Projenin temel amacı, kullanıcıların SQL bilgisine ihtiyaç duymadan ürün yorumları, sentiment sonuçları, ürünler ve kategoriler hakkında sorular sorabilmesini ve BigQuery üzerinde bulunan gerçek veriler üzerinden anlamlı cevaplar alabilmesini sağlamaktır.

---

## 🚀 Proje Özeti

Kullanıcı, chatbot'a doğal dil kullanarak bir soru yöneltir.

Örneğin:

> "Ürün yorumları iyi olan televizyon modellerini öner."

Chatbot soruyu analiz eder ve gerekli veriye ulaşmak için uygun araçları kullanır.

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

# 🛠️ Teknolojiler

| Teknoloji | Kullanım Amacı |
|---|---|
| Python | Backend ve chatbot mantığı |
| Google Gemini | Doğal dil işleme ve Function Calling |
| Google BigQuery | Ürün yorum verilerinin sorgulanması |
| Flask | Backend REST API |
| python-dotenv | Environment variable yönetimi |
| Git / GitHub | Versiyon kontrolü ve kaynak kod yönetimi |

---

# 🏗️ Proje Mimarisi

Projenin backend tarafındaki temel yapı aşağıdaki bileşenlerden oluşmaktadır:

```text
                 ┌─────────────────┐
                 │     Client      │
                 │   / Frontend    │
                 └────────┬────────┘
                          │
                          │ HTTP POST
                          ▼
                 ┌─────────────────┐
                 │      Flask      │
                 │       API       │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  VestelChatbot  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     Gemini      │
                 │  Function Call  │
                 └────────┬────────┘
                          │
                 ┌────────┴────────┐
                 │                 │
                 ▼                 ▼
          ┌─────────────┐   ┌─────────────┐
          │    Tools    │   │    Tools    │
          └──────┬──────┘   └──────┬──────┘
                 │                 │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │    BigQuery     │
                 └─────────────────┘
```

---

# 📁 Proje Yapısı

```text
vestel-nova-chatbot/
│
├── api.py
├── chatbot.py
├── gemini_client.py
├── bigquery_client.py
├── test_bigquery.py
├── .gitignore
├── .env
└── README.md
```

> `.env` dosyası örnek yapı içerisinde gösterilmiş olsa da `.gitignore` tarafından Git repository'sine dahil edilmemektedir.

### `api.py`

Flask API katmanını içerir.

Chatbot'a HTTP üzerinden istek gönderilmesini sağlar.

Örneğin:

```text
POST /chat
```

endpoint'i üzerinden kullanıcı mesajı backend'e iletilebilir.

---

### `chatbot.py`

Chatbot'un temel iş mantığını içerir.

Gemini interaction sürecini ve Function Calling döngüsünü yönetir.

Tool çağrıları sonucunda elde edilen verilerin Gemini'ye tekrar gönderilmesini ve nihai cevabın oluşturulmasını sağlar.

---

### `gemini_client.py`

Gemini client yapılandırmasını ve Gemini API ile ilgili işlemleri içerir.

API key environment variable üzerinden alınır.

---

### `bigquery_client.py`

BigQuery bağlantısı ve veri sorgulama işlemlerini içerir.

Ürün yorumları ve analiz sonuçları bu katman üzerinden sorgulanır.

---

### `test_bigquery.py`

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

---

# 🔐 Environment Variables

API anahtarları kaynak kod içerisinde tutulmamaktadır.

Projenin ana dizininde `.env` dosyası oluşturulmalıdır:

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

> `requirements.txt` dosyası repository'de henüz bulunmuyorsa oluşturulmalıdır.

---

## 4. Environment variable'ları tanımla

`.env` dosyası:

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

Flask backend'i çalıştırmak için:

```bash
python api.py
```

Backend varsayılan olarak:

```text
http://127.0.0.1:5000
```

adresinde çalışabilir.

Chat endpoint'i:

```text
POST /chat
```

şeklindedir.

Örnek istek:

```json
{
  "message": "Ürün yorumları iyi olan televizyon modellerini öner."
}
```

---

# 🔄 API Akışı

Backend'e gelen bir chat isteği genel olarak şu şekilde işlenir:

```text
POST /chat
     │
     ▼
Flask
     │
     ▼
VestelChatbot.ask()
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
     │           Tool sonucu
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

# 🧪 PoC Durumu

Bu repository, projenin **Proof of Concept (PoC)** aşamasındaki halini içermektedir.

Mevcut PoC ile:

- Gemini entegrasyonu
- Function Calling
- BigQuery veri erişimi
- Doğal dil ile veri sorgulama
- Flask API
- Tool calling loop
- Frontend/backend iletişimi

gibi temel bileşenler çalışır durumdadır.

---

# 🚧 Gelecek Geliştirmeler

Projenin ilerleyen aşamalarında aşağıdaki geliştirmeler değerlendirilebilir:

### Veri Analizi

- Daha gelişmiş ürün karşılaştırmaları
- Attribute-level sentiment analizi
- Zaman serisi analizleri
- Daha gelişmiş trend analizi
- Otomatik insight üretimi

### AI Katmanı

- Daha gelişmiş tool orchestration
- Tool sonuçlarının daha kontrollü işlenmesi
- Cevap doğrulama mekanizmaları
- Daha kapsamlı conversation memory

### Backend

- Authentication / authorization
- API rate limiting
- Logging ve monitoring
- Production WSGI server
- Hata yönetiminin geliştirilmesi

### Frontend

- Gelişmiş chat deneyimi
- Streaming cevaplar
- Tool işlem durumlarının kullanıcıya gösterilmesi
- Analiz sonuçları için grafik ve tablo bileşenleri

### Production

- Cloud ortamına deployment
- Secret management
- CI/CD
- Test coverage
- Production monitoring

---

# 👥 Hedef Kullanım

Projenin hedef kullanım alanı Vestel ekiplerinin ürün yorumlarından daha hızlı içgörü elde edebilmesidir.

Özellikle teknik olmayan kullanıcıların:

> "Bu kategoride müşteriler en çok hangi konudan şikayet ediyor?"

veya

> "Hangi televizyon modelleri daha olumlu yorumlara sahip?"

gibi soruları SQL yazmadan sorabilmesi hedeflenmektedir.

---

# 📌 Proje Durumu

**Status:** Proof of Concept (PoC)

**Environment:** Local Development

**Backend:** Flask

**LLM:** Google Gemini

**Data Warehouse:** Google BigQuery

**Interface:** REST API

---

## 📄 License

Bu proje Vestel Geleceğe Bi' Adım Staj Programı kapsamında geliştirilmiş bir PoC çalışmasıdır.

Kaynak kodun kullanım ve paylaşım koşulları proje sahibi / ilgili kurum politikalarına tabidir.