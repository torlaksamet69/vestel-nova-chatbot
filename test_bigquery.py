from google.cloud import bigquery

client = bigquery.Client(project="vestel-nova")

query = """
SELECT
    app_name,
    content,
    category,
    sentiment
FROM `vestel-nova.product_comments.playstore_reviews`
WHERE content IS NOT NULL
LIMIT 5
"""

results = client.query(query).result()

for row in results:
    print("-" * 50)
    print("Uygulama:", row.app_name)
    print("Yorum:", row.content)
    print("Kategori:", row.category)
    print("Sentiment:", row.sentiment)

print("\nBigQuery bağlantısı başarılı!")