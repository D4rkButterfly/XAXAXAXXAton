import sys
from src.pipeline import VoicePipeline

def main():
    pipeline = VoicePipeline()
    
    print("Выберите режим работы:")
    print("1. Начать живую транскрибацию (Микрофон / Телефония)")
    print("2. Обработать аудиофайл (Мессенджеры: mp3, m4a, ogg, wav)")
    
    choice = input("Введите номер (1 или 2): ").strip()
    
    if choice == "1":
        pipeline.process_live()
    elif choice == "2":
        file_path = input("Введите путь к файлу (например, voice.ogg): ").strip()
        pipeline.process_file(file_path)
    else:
        print("Неверный выбор. Выход.")

if __name__ == "__main__":
    main()
