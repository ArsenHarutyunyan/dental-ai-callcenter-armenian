def text_to_speech(text: str, output_file: str):
    with open("response_text.txt", "w", encoding="utf-8") as file:
        file.write(text)

    print("TTS skipped. Response saved to response_text.txt")