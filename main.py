import requests
from bs4 import BeautifulSoup
import json
import datetime
import pytz

# --- НАСТРОЙКИ ---
# Вставь сюда нужную ссылку на веб-версию канала (обязательно с /s/ в адресе)
CHANNEL_URL = "https://t.me/s/zhest_belgorod" 

# Маскируемся под обычный браузер
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_ro_status():
    try:
        response = requests.get(CHANNEL_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        if not messages:
            return {"status": "error", "text": "Канал недоступен или пуст"}
            
        # Убираем ограничение [-5:]. Теперь парсим ВСЮ доступную историю страницы снизу вверх.
        for msg in reversed(messages):
            text = msg.get_text().lower()
            
            # Как только находим первый (самый свежий) триггер — сразу отдаем статус и прекращаем поиск
            if "ракетная опасность" in text and "отбой" not in text:
                return {"status": "danger", "text": "🔴 РАКЕТНАЯ ОПАСНОСТЬ"}
            elif "отбой" in text:
                return {"status": "safe", "text": "🟢 Отбой РО"}
                
        # Если за последние ~20 постов вообще не было упоминаний РО
        return {"status": "info", "text": "⚪ Спокойно (Триггеров не найдено)"}
        
    except Exception as e:
        return {"status": "error", "text": "Сбой парсинга"}

def main():
    tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.datetime.now(tz).strftime("%H:%M")
    
    data = get_ro_status()
    data["time"] = current_time
    data["vpn_status"] = "VLESS: Не проверен" # Заглушка до следующего этапа
    
    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        
    print(f"Скрипт отработал. Статус: {data['text']} в {data['time']}")

if __name__ == "__main__":
    main()
