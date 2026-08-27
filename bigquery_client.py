import re
from typing import Any

from google.cloud import bigquery


# =========================================================
# BIGQUERY AYARLARI
# =========================================================

PROJECT_ID = "vestel-nova"

TABLE = "vestel-nova.product_comments.playstore_reviews"

client = bigquery.Client(project=PROJECT_ID)


# =========================================================
# TABLO ŞEMASI
# =========================================================

TABLE_SCHEMA = """
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
"""


# =========================================================
# GEMINI'NİN KULLANABİLECEĞİ ALANLAR
# =========================================================

ALLOWED_FIELDS = {
    "reviewId": "reviewId",
    "review_id": "reviewId",

    "app_name": "app_name",
    "uygulama": "app_name",

    "package_name": "package_name",
    "paket": "package_name",

    "score": "score",
    "puan": "score",

    "content": "content",
    "yorum": "content",
    "yorum_icerigi": "content",

    "language": "language",
    "dil": "language",

    "review_date": "review_date",
    "yorum_tarihi": "review_date",
    "tarih": "review_date",

    "thumbs_up_count": "thumbs_up_count",
    "begeni": "thumbs_up_count",

    "reply_content": "reply_content",
    "cevap": "reply_content",

    "reply_date": "reply_date",
    "cevap_tarihi": "reply_date",

    "app_version": "app_version",
    "versiyon": "app_version",

    "ingestion_date": "ingestion_date",
    "yukleme_tarihi": "ingestion_date",

    "category": "category",
    "kategori": "category",

    "sentiment": "sentiment",
    "duygu": "sentiment",

    "llm_processed": "llm_processed",
}


# =========================================================
# SQL GÜVENLİĞİ
# =========================================================

FORBIDDEN_SQL = [
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "MERGE ",
    "DROP ",
    "ALTER ",
    "TRUNCATE ",
    "CREATE ",
    "REPLACE ",
    "GRANT ",
    "REVOKE ",
    "EXPORT ",
    "LOAD ",
]


def validate_sql(sql: str) -> str:

    if not sql:
        raise ValueError("SQL sorgusu boş olamaz.")

    sql = sql.strip()

    sql = re.sub(
        r"^```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = re.sub(
        r"^```\s*",
        "",
        sql,
    )

    sql = re.sub(
        r"\s*```$",
        "",
        sql,
    )

    sql = sql.strip()

    if ";" in sql.rstrip(";"):
        raise ValueError(
            "Birden fazla SQL statement çalıştırılamaz."
        )

    if not re.match(
        r"^(SELECT|WITH)\b",
        sql,
        flags=re.IGNORECASE,
    ):
        raise ValueError(
            "Sadece SELECT veya WITH sorgularına izin verilir."
        )

    upper_sql = sql.upper()

    for forbidden in FORBIDDEN_SQL:

        if forbidden in upper_sql:
            raise ValueError(
                "Güvenli olmayan SQL komutu tespit edildi."
            )

    normalized_sql = (
        sql
        .replace("`", "")
        .replace(" ", "")
        .lower()
    )

    normalized_table = (
        TABLE
        .replace(" ", "")
        .lower()
    )

    if normalized_table not in normalized_sql:

        raise ValueError(
            "Sorgu izin verilen BigQuery tablosunu "
            "kullanmalıdır."
        )

    return sql


# =========================================================
# SONUÇLARI PYTHON DICT'E ÇEVİR
# =========================================================

def rows_to_dicts(rows):

    result = []

    for row in rows:

        item = {}

        for key, value in row.items():

            if hasattr(value, "isoformat"):

                try:
                    value = value.isoformat()

                except Exception:
                    pass

            item[key] = value

        result.append(item)

    return result


# =========================================================
# GENEL SQL ÇALIŞTIRICI
# =========================================================

def run_bigquery_query(sql: str) -> list:

    sql = validate_sql(sql)

    print("\n")
    print("=" * 70)
    print("BIGQUERY SORGUSU")
    print("=" * 70)
    print(sql)
    print("=" * 70)

    try:

        job_config = bigquery.QueryJobConfig(
            use_query_cache=True
        )

        rows = client.query(
            sql,
            job_config=job_config,
        ).result()

        result = rows_to_dicts(rows)

        print("\nBIGQUERY SONUCU")
        print("=" * 70)
        print(result)
        print("=" * 70)

        return result

    except Exception as e:

        print("\nBIGQUERY HATASI")
        print("=" * 70)
        print(str(e))
        print("=" * 70)

        raise


# =========================================================
# YARDIMCI
# =========================================================

def _safe_int(value, default):

    if value is None:
        return default

    try:
        return int(value)

    except Exception:
        return default


def _safe_float(value):

    if value is None:
        return None

    try:
        return float(value)

    except Exception:
        return None


def _normalize_order(order):

    if str(order).lower() == "asc":
        return "ASC"

    return "DESC"


def _field(field_name):

    if not field_name:
        return None

    key = str(field_name).strip()

    if key not in ALLOWED_FIELDS:
        return None

    return ALLOWED_FIELDS[key]


# =========================================================
# ANA ANALİZ FONKSİYONU
#
# Gemini'nin asıl kullanacağı tool budur.
# =========================================================

def query_reviews(
    analysis_type: str = "count",

    keyword: str | None = None,

    sentiment: str | None = None,

    category: str | None = None,

    app_version: str | None = None,

    app_name: str | None = None,

    language: str | None = None,

    package_name: str | None = None,

    llm_processed: str | None = None,

    min_score: float | None = None,

    max_score: float | None = None,

    start_date: str | None = None,

    end_date: str | None = None,

    group_by: str | None = None,

    metric: str = "count",

    order: str = "desc",

    min_group_count: int = 1,

    limit: int = 10,

    offset: int = 0,
):

    analysis_type = (
        str(analysis_type or "count")
        .strip()
        .lower()
    )

    metric = (
        str(metric or "count")
        .strip()
        .lower()
    )

    order_sql = _normalize_order(order)

    limit = max(1, min(_safe_int(limit, 10), 100))

    offset = max(0, _safe_int(offset, 0))

    min_group_count = max(
        1,
        _safe_int(min_group_count, 1),
    )

    conditions = [
        "1 = 1"
    ]

    query_parameters = []

    # =====================================================
    # FİLTRELER
    # =====================================================

    if keyword:

        conditions.append(
            """
            LOWER(CAST(content AS STRING))
            LIKE LOWER(@keyword)
            """
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "keyword",
                "STRING",
                f"%{keyword}%",
            )
        )

    if sentiment:

        conditions.append(
            "LOWER(CAST(sentiment AS STRING)) = LOWER(@sentiment)"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "sentiment",
                "STRING",
                sentiment,
            )
        )

    if category:

        conditions.append(
            "LOWER(CAST(category AS STRING)) = LOWER(@category)"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "category",
                "STRING",
                category,
            )
        )

    if app_version:

        conditions.append(
            "CAST(app_version AS STRING) = @app_version"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "app_version",
                "STRING",
                app_version,
            )
        )

    if app_name:

        conditions.append(
            "LOWER(CAST(app_name AS STRING)) = LOWER(@app_name)"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "app_name",
                "STRING",
                app_name,
            )
        )

    if language:

        conditions.append(
            "LOWER(CAST(language AS STRING)) = LOWER(@language)"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "language",
                "STRING",
                language,
            )
        )

    if package_name:

        conditions.append(
            "LOWER(CAST(package_name AS STRING)) = LOWER(@package_name)"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "package_name",
                "STRING",
                package_name,
            )
        )

    if llm_processed is not None:

        conditions.append(
            "CAST(llm_processed AS STRING) = @llm_processed"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "llm_processed",
                "STRING",
                str(llm_processed),
            )
        )

    # =====================================================
    # PUAN
    # =====================================================

    min_score_value = _safe_float(min_score)
    max_score_value = _safe_float(max_score)

    if min_score_value is not None:

        conditions.append(
            "SAFE_CAST(score AS FLOAT64) >= @min_score"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "min_score",
                "FLOAT64",
                min_score_value,
            )
        )

    if max_score_value is not None:

        conditions.append(
            "SAFE_CAST(score AS FLOAT64) <= @max_score"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "max_score",
                "FLOAT64",
                max_score_value,
            )
        )

    # =====================================================
    # TARİH
    #
    # End date kullanıcı tarafından 2025-12-31 verilirse
    # o günün tamamını dahil etmek için < 2026-01-01
    # şeklinde kullanıyoruz.
    # =====================================================

    if start_date:

        conditions.append(
            "DATE(review_date) >= @start_date"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "start_date",
                "DATE",
                start_date,
            )
        )

    if end_date:

        conditions.append(
            "DATE(review_date) <= @end_date"
        )

        query_parameters.append(
            bigquery.ScalarQueryParameter(
                "end_date",
                "DATE",
                end_date,
            )
        )

    where_sql = "\nAND ".join(conditions)

    # =====================================================
    # GROUP BY ALANI
    # =====================================================

    group_field = _field(group_by)

    # =====================================================
    # ANALİZ TİPİ NORMALİZASYONU
    # =====================================================

    if analysis_type in (
        "highest_average",
        "highest_average_version",
    ):

        group_field = group_field or "app_version"

        analysis_type = "group_average"

        order_sql = "DESC"

        min_group_count = max(
            min_group_count,
            3,
        )

        limit = 1

    elif analysis_type in (
        "lowest_average",
        "lowest_average_version",
    ):

        group_field = group_field or "app_version"

        analysis_type = "group_average"

        order_sql = "ASC"

        min_group_count = max(
            min_group_count,
            3,
        )

        limit = 1

    # =====================================================
    # COUNT
    # =====================================================

    if analysis_type == "count":

        query = f"""
        SELECT
            COUNT(*) AS review_count
        FROM `{TABLE}`
        WHERE {where_sql}
        """

    # =====================================================
    # DISTINCT COUNT
    # =====================================================

    elif analysis_type in (
        "distinct_count",
        "unique_count",
    ):

        field = _field(group_by) or "reviewId"

        query = f"""
        SELECT
            COUNT(DISTINCT {field}) AS unique_count
        FROM `{TABLE}`
        WHERE {where_sql}
        """

    # =====================================================
    # AVERAGE
    # =====================================================

    elif analysis_type in (
        "average",
        "average_score",
    ):

        if group_field:

            query = f"""
            SELECT
                {group_field} AS group_value,
                AVG(SAFE_CAST(score AS FLOAT64))
                    AS average_score,
                COUNT(*) AS review_count
            FROM `{TABLE}`
            WHERE {where_sql}
              AND score IS NOT NULL
              AND {group_field} IS NOT NULL
            GROUP BY {group_field}
            HAVING COUNT(*) >= {min_group_count}
            ORDER BY average_score {order_sql}
            LIMIT {limit}
            OFFSET {offset}
            """

        else:

            query = f"""
            SELECT
                AVG(SAFE_CAST(score AS FLOAT64))
                    AS average_score,
                COUNT(*) AS review_count
            FROM `{TABLE}`
            WHERE {where_sql}
              AND score IS NOT NULL
            """

    # =====================================================
    # GROUP AVERAGE
    # =====================================================

    elif analysis_type == "group_average":

        if not group_field:

            raise ValueError(
                "group_average için group_by gereklidir."
            )

        query = f"""
        SELECT
            {group_field} AS group_value,
            AVG(SAFE_CAST(score AS FLOAT64))
                AS average_score,
            COUNT(*) AS review_count,
            MIN(SAFE_CAST(score AS FLOAT64))
                AS min_score,
            MAX(SAFE_CAST(score AS FLOAT64))
                AS max_score
        FROM `{TABLE}`
        WHERE {where_sql}
          AND score IS NOT NULL
          AND {group_field} IS NOT NULL
        GROUP BY {group_field}
        HAVING COUNT(*) >= {min_group_count}
        ORDER BY average_score {order_sql}
        LIMIT {limit}
        OFFSET {offset}
        """

    # =====================================================
    # GROUP COUNT
    # =====================================================

    elif analysis_type in (
        "group_count",
        "group",
        "distribution",
    ):

        if not group_field:

            raise ValueError(
                "group_count için group_by gereklidir."
            )

        query = f"""
        SELECT
            {group_field} AS group_value,
            COUNT(*) AS review_count
        FROM `{TABLE}`
        WHERE {where_sql}
          AND {group_field} IS NOT NULL
        GROUP BY {group_field}
        HAVING COUNT(*) >= {min_group_count}
        ORDER BY review_count {order_sql}
        LIMIT {limit}
        OFFSET {offset}
        """

    # =====================================================
    # SUM
    # =====================================================

    elif analysis_type == "sum":

        field = _field(group_by)

        if field:

            query = f"""
            SELECT
                SUM(SAFE_CAST({field} AS FLOAT64))
                    AS total_value
            FROM `{TABLE}`
            WHERE {where_sql}
            """

        else:

            raise ValueError(
                "SUM analizi için group_by ile toplanacak "
                "bir alan belirtilmelidir."
            )

    # =====================================================
    # MIN
    # =====================================================

    elif analysis_type == "min":

        field = _field(group_by) or "score"

        query = f"""
        SELECT
            MIN(SAFE_CAST({field} AS FLOAT64))
                AS min_value
        FROM `{TABLE}`
        WHERE {where_sql}
        """

    # =====================================================
    # MAX
    # =====================================================

    elif analysis_type == "max":

        field = _field(group_by) or "score"

        query = f"""
        SELECT
            MAX(SAFE_CAST({field} AS FLOAT64))
                AS max_value
        FROM `{TABLE}`
        WHERE {where_sql}
        """

    # =====================================================
    # THUMBS UP
    # =====================================================

    elif analysis_type in (
        "most_liked",
        "top_liked",
    ):

        query = f"""
        SELECT
            reviewId,
            app_name,
            app_version,
            score,
            content,
            thumbs_up_count,
            review_date
        FROM `{TABLE}`
        WHERE {where_sql}
          AND thumbs_up_count IS NOT NULL
        ORDER BY thumbs_up_count {order_sql}
        LIMIT {limit}
        OFFSET {offset}
        """

    # =====================================================
    # REVIEWS / CONTENT
    # =====================================================

    elif analysis_type in (
        "reviews",
        "comments",
        "list_reviews",
        "search_reviews",
    ):

        query = f"""
        SELECT
            reviewId,
            app_name,
            app_version,
            score,
            content,
            category,
            sentiment,
            language,
            thumbs_up_count,
            review_date,
            reply_content,
            reply_date
        FROM `{TABLE}`
        WHERE {where_sql}
        ORDER BY review_date DESC
        LIMIT {limit}
        OFFSET {offset}
        """

    # =====================================================
    # TOP CATEGORY
    # =====================================================

    elif analysis_type == "top_category":

        query = f"""
        SELECT
            category AS group_value,
            COUNT(*) AS review_count
        FROM `{TABLE}`
        WHERE {where_sql}
          AND category IS NOT NULL
        GROUP BY category
        HAVING COUNT(*) >= {min_group_count}
        ORDER BY review_count DESC
        LIMIT {limit}
        """

    # =====================================================
    # TOP SENTIMENT
    # =====================================================

    elif analysis_type == "top_sentiment":

        query = f"""
        SELECT
            sentiment AS group_value,
            COUNT(*) AS review_count
        FROM `{TABLE}`
        WHERE {where_sql}
          AND sentiment IS NOT NULL
        GROUP BY sentiment
        ORDER BY review_count DESC
        LIMIT {limit}
        """

    # =====================================================
    # RAW / ÖZEL ANALİZ
    #
    # Gemini çok özel bir analiz istediğinde
    # run_bigquery_query kullanması tercih edilir.
    # =====================================================

    else:

        raise ValueError(
            f"Desteklenmeyen analysis_type: {analysis_type}"
        )

    # =====================================================
    # ÇALIŞTIR
    # =====================================================

    print("\n")
    print("=" * 70)
    print("ANALYZE_REVIEWS")
    print("=" * 70)
    print("analysis_type:", analysis_type)
    print("group_by:", group_by)
    print("metric:", metric)
    print("order:", order)
    print("limit:", limit)
    print("min_group_count:", min_group_count)
    print("=" * 70)

    print("\nBIGQUERY SORGUSU")
    print("=" * 70)
    print(query)
    print("=" * 70)

    try:

        job_config = bigquery.QueryJobConfig(
            query_parameters=query_parameters,
            use_query_cache=True,
        )

        rows = client.query(
            query,
            job_config=job_config,
        ).result()

        result = rows_to_dicts(rows)

        print("\nBIGQUERY SONUCU")
        print("=" * 70)
        print(result)
        print("=" * 70)

        return result

    except Exception as e:

        print("\nBIGQUERY HATASI")
        print("=" * 70)
        print(str(e))
        print("=" * 70)

        raise


# =========================================================
# GEMINI'NİN ÇAĞIRACAĞI ANA TOOL
# =========================================================

def analyze_reviews(
    analysis_type: str = "count",

    keyword: str | None = None,

    sentiment: str | None = None,

    category: str | None = None,

    app_version: str | None = None,

    app_name: str | None = None,

    language: str | None = None,

    package_name: str | None = None,

    llm_processed: str | None = None,

    min_score: float | None = None,

    max_score: float | None = None,

    start_date: str | None = None,

    end_date: str | None = None,

    group_by: str | None = None,

    metric: str = "count",

    order: str = "desc",

    min_group_count: int = 1,

    limit: int = 10,

    offset: int = 0,
):

    return query_reviews(
        analysis_type=analysis_type,

        keyword=keyword,

        sentiment=sentiment,

        category=category,

        app_version=app_version,

        app_name=app_name,

        language=language,

        package_name=package_name,

        llm_processed=llm_processed,

        min_score=min_score,

        max_score=max_score,

        start_date=start_date,

        end_date=end_date,

        group_by=group_by,

        metric=metric,

        order=order,

        min_group_count=min_group_count,

        limit=limit,

        offset=offset,
    )