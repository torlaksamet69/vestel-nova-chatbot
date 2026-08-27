from gemini_client import ask_gemini_with_function_calling


def main():
    print("=" * 50)
    print("          VESTEL YORUM ASİSTANI")
    print("=" * 50)
    print("Çıkmak için 'q' yazabilirsiniz.")
    print()

    while True:
        question = input("Sorunuz: ").strip()

        # Boş soru kontrolü
        if not question:
            print("Lütfen bir soru yazın.\n")
            continue

        # Çıkış kontrolü
        if question.lower() == "q":
            print("Chatbot kapatılıyor...")
            break

        try:
            # Soruyu Gemini'ye gönderiyoruz.
            #
            # Gemini:
            # - Önceki konuşmayı hatırlar.
            # - Gerekirse Function Calling kullanır.
            # - BigQuery'den gerçek yorumları getirir.
            # - Sonucu doğal Türkçe olarak verir.
            answer = ask_gemini_with_function_calling(question)

            print("\nChatbot:")
            print(answer)
            print()

        except Exception as e:
            print("\nBir hata oluştu:")
            print(e)
            print()


if __name__ == "__main__":
    main()