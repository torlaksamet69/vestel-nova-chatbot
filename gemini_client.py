import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from bigquery_client import (
    analyze_reviews,
    run_bigquery_query,
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY bulunamadı. "
        ".env dosyasını kontrol et."
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# SYSTEM INSTRUCTION
# =========================================================

SYSTEM_INSTRUCTION = """
Sen Vestel kullanıcı yorumlarını analiz eden
profesyonel bir veri analiz asistanısın.

Cevaplarını Türkçe ver.

Veri kaynağın:

vestel-nova.product_comments.playstore_reviews


=========================================================
TABLO ALANLARI
=========================================================

reviewId
app_name
package_name
score
content
language
review_date
thumbs_up_count
reply_content
reply_date
app_version
ingestion_date
category
sentiment
llm_processed


=========================================================
ANA KURAL
=========================================================

Kullanıcı gerçek veriye dayalı bir soru soruyorsa
tahmin yapma.

Önce uygun function call yap.

Ana tool:

analyze_reviews


Çok özel veya analyze_reviews ile doğrudan
karşılanamayacak bir analiz gerekiyorsa:

run_bigquery_query


kullanabilirsin.


=========================================================
SORU TÜRÜNÜ ANLAMA
=========================================================

Kullanıcı aynı şeyi farklı şekillerde sorabilir.

Örneğin:

"Kaç yorum var?"
"Toplam yorum sayısı nedir?"
"Kaç tane değerlendirme yapılmış?"

hepsi COUNT analizidir.


"Ortalama puan nedir?"
"Yorumların puan ortalaması kaç?"
"Genel skor kaç?"

hepsi AVG(score) analizidir.


"En yüksek puanlı uygulama hangisi?"
"Hangi uygulama daha iyi?"
"En yüksek ortalama hangi uygulamada?"

uygulama bazında average karşılaştırmasıdır.


"En kötü versiyon hangisi?"
"En düşük ortalama puan hangi versiyonda?"
"En düşük puanlı uygulama versiyonu?"

app_version bazında average karşılaştırmasıdır.


=========================================================
KÜÇÜK ÖRNEKLEM
=========================================================

Versiyon, uygulama veya başka grupları
ortalama puan açısından karşılaştırırken
çok az yorumlu grupları doğrudan karşılaştırma.

Varsayılan:

min_group_count = 3


Örneğin:

"En düşük ortalama puana sahip uygulama versiyonu?"

şeklindeki soruda:

analysis_type = "lowest_average_version"

veya uygun group_average yapısı kullan.

app_version bazında karşılaştır.

En az 3 yorum şartını uygula.


=========================================================
PUAN
=========================================================

"1 puan alan kaç yorum var?"

min_score = 1
max_score = 1


"3 puan ve altı"

max_score = 3


"4 puan ve üzeri"

min_score = 4


"2 ile 4 puan arası"

min_score = 2
max_score = 4


Puan sorularında kullanıcı sayı verdiğinde
gereksiz yere kullanıcıdan ayrıca puan isteme.


=========================================================
TARİH
=========================================================

"2025 yılında"

start_date = "2025-01-01"
end_date = "2025-12-31"


"2024 yılında"

start_date = "2024-01-01"
end_date = "2024-12-31"


Tarih + puan + uygulama + sentiment gibi
birden fazla koşul varsa hepsini aynı tool
çağrısında kullan.


=========================================================
UYGULAMA
=========================================================

Uygulama karşılaştırmalarında:

group_by = "app_name"


=========================================================
VERSİYON
=========================================================

Versiyon karşılaştırmalarında:

group_by = "app_version"


=========================================================
KATEGORİ
=========================================================

Kategori sayımı:

group_by = "category"


Fakat kullanıcı:

"Kullanıcıların en çok beğendiği konular neler?"

dediğinde sadece category isimlerini
"konu" olarak kabul etme.

Bu soru içerik analizi gerektiriyorsa
pozitif yorumları al ve content alanındaki
gerçek kullanıcı yorumlarını incele.

Aynı şekilde:

"Kullanıcılar en çok neden şikayet ediyor?"

sorusunda sadece:

functionality_issue

gibi teknik kategori isimlerini cevap olarak
verme.

Negatif yorumların content alanını analiz et.


=========================================================
SENTIMENT
=========================================================

"pozitif yorumlar":

sentiment = "positive"


"negatif yorumlar":

sentiment = "negative"


Ancak veritabanında gerçek değerleri esas al.


=========================================================
THUMBS UP
=========================================================

"En çok beğenilen yorumlar"

thumbs_up_count alanını kullan.

En yüksek değerleri getir.


=========================================================
İÇERİK
=========================================================

"Wi-Fi hakkında ne düşünüyorlar?"

content alanını kullan.

"Klima ile ilgili en çok hangi sorun var?"

content alanını analiz et.

Kullanıcı yorumlarından gerçek ortak konuları
çıkar.


=========================================================
ÇOK ADIMLI SORULAR
=========================================================

Kullanıcı:

"En kötü versiyon hangisi ve o versiyonda
en çok hangi konuda şikayet edilmiş?"

derse birden fazla tool çağrısı yapabilirsin.

1. En düşük ortalama puanlı versiyonu bul.
2. O versiyona filtre uygula.
3. Negatif yorumları analiz et.
4. Content alanından ortak problemleri çıkar.
5. Sonucu birleştir.


=========================================================
KONUŞMA GEÇMİŞİ
=========================================================

Önceki kullanıcı mesajlarını ve cevaplarını
dikkate al.

Kullanıcı takip sorusu sorabilir.

Örneğin:

Kullanıcı:
En düşük ortalama puanlı versiyon hangisi?

Bot:
7.0055.39

Kullanıcı:
Kaç yorumu var?

Buradaki "kaç yorumu var?" sorusunun
7.0055.39 versiyonunu kastettiğini anla.

Başka örnek:

Kullanıcı:
En yüksek ortalama puanlı uygulama hangisi?

Bot:
Vestel Akıllı Yaşam.

Kullanıcı:
Peki onun kaç yorumu var?

"onun" ifadesinin önceki sonuçtaki uygulamaya
ait olduğunu anla.


=========================================================
ÖNCEKİ SONUCU KÖRÜ KÖRÜNE KULLANMA
=========================================================

Konuşma geçmişini bağlamı anlamak için kullan.

Ancak kullanıcı yeni bir veri sorusu soruyorsa
gerekiyorsa yeni function call yap.

Örneğin:

Önceki soru:
Toplam yorum sayısı kaç?

Sonuç:
6054

Sonraki soru:
2025 yılında kaç yorum var?

Burada 6054 sayısını tekrar kullanma.

Yeni BigQuery sorgusu yap.


=========================================================
FUNCTION CALL SONUCU
=========================================================

Function sonucunu gördükten sonra
sonucu dikkatlice yorumla.

Veride olmayan bilgiyi uydurma.

Sonuç boşsa:

"Bu koşullara uyan veri bulunamadı."

de.


=========================================================
CEVAP TARZI
=========================================================

Kullanıcı basit sayı soruyorsa kısa cevap ver.

Karşılaştırma sorularında:

- sonuç
- ilgili değer
- yorum sayısı

gibi önemli bilgileri ver.

Analiz sorularında maddeler kullanabilirsin.

Kullanıcı istemediği sürece SQL gösterme.

Function calling'den bahsetme.

Teknik hata mesajını kullanıcıya aynen gösterme.


=========================================================
ÇOK ÖNEMLİ
=========================================================

Her yeni soru için Python koduna yeni
if/else ekleme.

Soruyu anlamaya çalış.

Tablodaki alanları uygun şekilde kullan.

Gerekiyorsa function call yap.

Önceki konuşma bağlamını koru.
"""


# =========================================================
# FUNCTION DECLARATION
# =========================================================

ANALYZE_REVIEWS_DECLARATION = types.FunctionDeclaration(

    name="analyze_reviews",

    description="""
Vestel kullanıcı yorumları üzerinde veri analizi yapar.

Sayım, ortalama puan, gruplama, karşılaştırma,
puan filtreleme, tarih filtreleme, uygulama,
versiyon, kategori, sentiment, dil, yorum,
beğeni ve benzeri analizleri gerçekleştirir.

Kullanıcının gerçek veri gerektiren sorularında
bu fonksiyonu kullan.
""",

    parameters=types.Schema(

        type=types.Type.OBJECT,

        properties={

            "analysis_type": types.Schema(
                type=types.Type.STRING,
                description=(
                    "count, average_score, average, "
                    "group_count, group_average, "
                    "highest_average_version, "
                    "lowest_average_version, "
                    "most_liked, reviews, top_category, "
                    "top_sentiment vb."
                ),
            ),

            "keyword": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description=(
                    "Yorum içeriğinde aranacak kelime veya ifade."
                ),
            ),

            "sentiment": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description=(
                    "positive veya negative gibi sentiment değeri."
                ),
            ),

            "category": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description="Kategori filtresi.",
            ),

            "app_version": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description="Uygulama versiyonu filtresi.",
            ),

            "app_name": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description="Uygulama adı filtresi.",
            ),

            "language": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description="Dil filtresi.",
            ),

            "package_name": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description="Paket adı filtresi.",
            ),

            "llm_processed": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description="LLM işlenme durumu filtresi.",
            ),

            "min_score": types.Schema(
                type=types.Type.NUMBER,
                nullable=True,
                description="Minimum puan.",
            ),

            "max_score": types.Schema(
                type=types.Type.NUMBER,
                nullable=True,
                description="Maksimum puan.",
            ),

            "start_date": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description="Başlangıç tarihi YYYY-MM-DD.",
            ),

            "end_date": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description="Bitiş tarihi YYYY-MM-DD.",
            ),

            "group_by": types.Schema(
                type=types.Type.STRING,
                nullable=True,
                description=(
                    "Gruplama alanı: app_name, app_version, "
                    "category, sentiment, language vb."
                ),
            ),

            "metric": types.Schema(
                type=types.Type.STRING,
                description=(
                    "count, average, sum, min veya max."
                ),
            ),

            "order": types.Schema(
                type=types.Type.STRING,
                description="asc veya desc.",
            ),

            "min_group_count": types.Schema(
                type=types.Type.INTEGER,
                description=(
                    "Grupların karşılaştırmaya girebilmesi "
                    "için minimum yorum sayısı."
                ),
            ),

            "limit": types.Schema(
                type=types.Type.INTEGER,
                description="Döndürülecek maksimum sonuç.",
            ),

            "offset": types.Schema(
                type=types.Type.INTEGER,
                description="Sayfalama başlangıcı.",
            ),
        },
    ),
)


# =========================================================
# TOOL OBJECT
# =========================================================

ANALYZE_REVIEWS_TOOL = types.Tool(
    function_declarations=[
        ANALYZE_REVIEWS_DECLARATION
    ]
)


# =========================================================
# GENEL SQL TOOL
# =========================================================

RUN_SQL_DECLARATION = types.FunctionDeclaration(

    name="run_bigquery_query",

    description="""
Analyze_reviews ile karşılanamayan çok özel veri
sorularında güvenli SELECT/WITH BigQuery sorgusu çalıştırır.

Yalnızca Vestel yorum tablosunda SELECT/WITH
sorguları kullanılabilir.

Bu tool'u genel veri analizi için gerektiğinde kullan.
""",

    parameters=types.Schema(

        type=types.Type.OBJECT,

        properties={

            "sql": types.Schema(
                type=types.Type.STRING,
                description=(
                    "Çalıştırılacak tek SELECT veya WITH SQL sorgusu."
                ),
            )

        },

        required=["sql"],
    ),
)


RUN_SQL_TOOL = types.Tool(
    function_declarations=[
        RUN_SQL_DECLARATION
    ]
)


# =========================================================
# GEMINI CONFIG
# =========================================================

config = types.GenerateContentConfig(

    system_instruction=SYSTEM_INSTRUCTION,

    tools=[
        ANALYZE_REVIEWS_TOOL,
        RUN_SQL_TOOL,
    ],

    temperature=0.1,
)


# =========================================================
# FUNCTION CALL LOG
# =========================================================

def _print_function_call(name, args):

    print("\n")
    print("=" * 70)
    print("GEMINI FUNCTION CALL")
    print("=" * 70)

    print("Fonksiyon:", name)

    print("\nParametreler:")

    try:

        print(
            json.dumps(
                args,
                ensure_ascii=False,
                indent=4,
            )
        )

    except Exception:

        print(args)

    print("=" * 70)


# =========================================================
# FUNCTION SONUCUNU GÜVENLİ STRING'E ÇEVİR
# =========================================================

def _serialize_result(result):

    try:

        return json.dumps(
            result,
            ensure_ascii=False,
            default=str,
        )

    except Exception:

        return str(result)


# =========================================================
# FUNCTION ÇALIŞTIR
# =========================================================

def _execute_function(function_name, args):

    if function_name == "analyze_reviews":

        return analyze_reviews(**args)

    if function_name == "run_bigquery_query":

        sql = args.get("sql")

        return run_bigquery_query(sql)

    raise ValueError(
        f"Bilinmeyen function: {function_name}"
    )


# =========================================================
# GEMINI CHAT
#
# Chat nesnesi konuşma geçmişini korur.
# =========================================================

_chat = client.chats.create(

    model="gemini-2.5-flash",

    config=config,
)


# =========================================================
# ANA FUNCTION CALLING DÖNGÜSÜ
# =========================================================

def ask_gemini_with_function_calling(
    prompt: str,
) -> str:

    try:

        # =================================================
        # İLK MESAJ
        # =================================================

        response = _chat.send_message(
            prompt
        )

        # =================================================
        # FUNCTION CALL DÖNGÜSÜ
        # Gemini birden fazla function call yapabilir.
        # =================================================

        max_function_rounds = 5

        for _ in range(max_function_rounds):

            function_calls = []

            if response.candidates:

                for candidate in response.candidates:

                    if not candidate.content:
                        continue

                    for part in candidate.content.parts:

                        if getattr(
                            part,
                            "function_call",
                            None,
                        ):

                            function_calls.append(
                                part.function_call
                            )

            # ---------------------------------------------
            # FUNCTION CALL YOKSA FİNAL CEVAP
            # ---------------------------------------------

            if not function_calls:

                text = response.text

                if text:

                    return text.strip()

                return (
                    "Sonuç üretilemedi."
                )

            # ---------------------------------------------
            # FUNCTION RESPONSE'ları hazırla
            # ---------------------------------------------

            function_response_parts = []

            for function_call in function_calls:

                function_name = (
                    function_call.name
                )

                args = dict(
                    function_call.args or {}
                )

                _print_function_call(
                    function_name,
                    args,
                )

                try:

                    result = _execute_function(
                        function_name,
                        args,
                    )

                    serialized = _serialize_result(
                        result
                    )

                except Exception as e:

                    print("\nFUNCTION HATASI")
                    print("=" * 70)
                    print(str(e))
                    print("=" * 70)

                    serialized = json.dumps(
                        {
                            "error": str(e)
                        },
                        ensure_ascii=False,
                    )

                # -----------------------------------------
                # Gemini'ye function sonucu gönder
                # -----------------------------------------

                function_response_parts.append(

                    types.Part(
                        function_response=
                        types.FunctionResponse(
                            name=function_name,
                            response={
                                "result": serialized
                            },
                        )
                    )
                )

            # ---------------------------------------------
            # FUNCTION RESULT → GEMINI
            # ---------------------------------------------

            response = _chat.send_message(

                function_response_parts
            )

        return (
            "Analiz için çok fazla işlem gerekti. "
            "Lütfen soruyu biraz daha daraltarak tekrar deneyin."
        )

    except Exception as e:

        print("\nGEMINI HATASI")
        print("=" * 70)
        print(str(e))
        print("=" * 70)

        return (
            "Soruyu işlerken teknik bir hata oluştu. "
            "Lütfen tekrar deneyin."
        )


# =========================================================
# NORMAL ASK_GEMINI
# =========================================================

def ask_gemini(prompt: str) -> str:

    return ask_gemini_with_function_calling(
        prompt
    )


# =========================================================
# YENİ KONUŞMA BAŞLAT
#
# İstersen chatbot.py içinde kullanılabilir.
# =========================================================

def reset_chat():

    global _chat

    _chat = client.chats.create(

        model="gemini-2.5-flash",

        config=config,
    )

    print("\nKonuşma geçmişi temizlendi.")
    