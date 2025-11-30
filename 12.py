import json
import os
from random import randrange
from urllib.request import Request, urlopen

import vk_api
from dotenv import load_dotenv
from vk_api.longpoll import VkEventType, VkLongPoll


# Загружаем токен из файла .env

load_dotenv()
TOKEN = os.getenv('TOKEN')

# Подключаемся к VK

vk_session = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()


# Мини-словарь русских пород → английские названия

RU_TO_EN = {
    "лабрадор": "labrador retriever",
    "овчарка": "german shepherd",
    "немецкая овчарка": "german shepherd",
    "хаски": "siberian husky",
    "мопс": "pug",
    "бульдог": "bulldog",
    "такса": "dachshund",
    "корги": "pembroke welsh corgi"
}


# Функция для получения списка всех собак с сайта

def get_dogs():
    req = Request(
        "https://api.thedogapi.com/v1/breeds",
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    response = urlopen(req)
    dogs = json.loads(response.read())
    return dogs


# Функция поиска информации о породе

def find_dog(name, dogs):
    name = name.lower()

    # Если порода указана на русском — переводим на английский (РАБОТАЕТ ТОЛЬКО ДЛЯ ПОРОД ИЗ СЛОВАРЯ)
    if name in RU_TO_EN:
        name = RU_TO_EN[name]

    for dog in dogs:
        if dog["name"].lower() == name:
            message = (
                f"Порода: {dog['name']}\n"
                f"Назначение: {dog.get('bred_for', 'Не указано')}\n"
                f"Продолжительность жизни: {dog.get('life_span', 'Не указано')}\n"
                f"Характер: {dog.get('temperament', 'Нет данных')}"
            )
            return message
    return None


# Функция для генерации ссылки на Rutube

def rutube_link(query):
    query = event.text.replace(' ', '+')
    return f"https://rutube.ru/search/?query={query}"


# Получаем список всех пород собак при старте бота

dogs = get_dogs()


# Основной цикл прослушивания сообщений

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        if event.from_user:

            parts = event.text.split()  # делим сообщение по пробелам
            command = parts[0].lower()  # первая часть — команда

            
            # Команда dog — поиск породы
            
            if command == "dog": 
                if len(parts) > 1:
                    name = " ".join(parts[1:])
                    info = find_dog(name, dogs)
                    if info:
                        vk.messages.send(
                            user_id=event.user_id,
                            message=info,
                            random_id=randrange(1, 100000)
                        )
                    else:
                        vk.messages.send( 
                            user_id=event.user_id,
                            message="Порода не найдена. Попробуйте написать на русском или английском.",
                            random_id=randrange(1, 100000)
                        )
                else:
                    vk.messages.send(
                        user_id=event.user_id,
                        message="Формат: dog <название породы>",
                        random_id=randrange(1, 100000)
                    )

            
            # Команда video — ссылка на Rutube
            
            elif command == "video":  
                if len(parts) > 1:
                    query = " ".join(parts[1:])
                    link = rutube_link(query)
                    vk.messages.send(
                        user_id=event.user_id,
                        message=link,
                        random_id=randrange(1, 100000)
                    )
                else:
                    vk.messages.send(
                        user_id=event.user_id,
                        message="Формат: video <запрос для поиска видео>",
                        random_id=randrange(1, 100000)
                    )

            
            # Любая другая команда
            
            else:
                vk.messages.send(
                    user_id=event.user_id,
                    message="Команды: dog <порода> или video <запрос>",
                    random_id=randrange(1, 100000)
                )