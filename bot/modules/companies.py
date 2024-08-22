"""

Размещение рекламных сообщений партнёров

"""


from datetime import datetime, timezone
import json
import random
from time import time
from typing import Union
from bson import ObjectId
from bot.config import mongo_client
from bot.exec import bot
from telebot.types import InlineKeyboardMarkup

from bot.modules.data_format import list_to_inline
from bot.modules.localization import get_lang, t
from bot.modules.overwriting.DataCalsses import DBconstructor
companies = DBconstructor(mongo_client.other.companies)
message_log = DBconstructor(mongo_client.other.message_log)


async def create_company(owner: int, message: dict, time_end: int, 
                        count: int, coin_price: int, priority: bool, 
                        one_message: bool, pin_message: bool, min_timeout: int,
                        delete_after: bool, ignore_system_timeout: bool):
    """
    owner: int

    message: {
        "ru": {
            "text": str,
            "markup": [{"name": "url"}],
            "parse_mode": str, # Mardown | HTML
            "image": str (url отправленного файла)
        }
    }

    time_end: int секунд | 'inf' Время завершения компании

    max_count: int | 'inf' Количество показов

    show_chount: int Показано раз

    priority: bool Имеет ли компания приоритетный над gramads

    one_message: bool Отправить одно сообщение одному юзеру

    pin_message: bool Закреплять ли сообщение

    coin_price: int Определяет награду за просмотр рекламы, если 0 - не отправлять сообщение

    min_timeout: int Минимальное время между показами для 1 пользователя

    delete_after: bool Удаление ли всех сообщений после завершения компании

    status: bool Статус активности компании

    ignore_system_timeout: bool Игнорировать ли таймаут пользователя

    """

    data = {
        'owner': owner,
        'message': message,

        'langs': [list(message.keys())],

        'time_end': time_end + int(time()),
        'time_start': int(time()),

        'max_count': count, 'show_chount': 0,
        'coin_price': coin_price,

        'priority': priority,
        'one_message': one_message,
        'pin_message': pin_message,
        'delete_after': delete_after,
        'ignore_system_timeout': ignore_system_timeout,

        'min_timeout': min_timeout,

        'status': False
    }

    await companies.insert_one(data)

async def save_message(advert_id: ObjectId, userid: int, 
                     message_id: int):

    """
    advert_id: ObjectId - id Companie
    userid: int - id пользователя
    message_id - id сообщения 

    """

    data = {
        'advert_id': advert_id,
        'userid': userid,
        'message_id': message_id
    }

    await message_log.insert_one(data)

async def end_company(advert_id: ObjectId):
    companie = await companies.find_one({'_id': advert_id})

    if companie:
        if companie['delete_after']:
            messages = await message_log.find({'advert_id': advert_id})

            for mes in messages:
                if companie['pin_message']:
                    try:
                        await bot.unpin_chat_message(mes['userid'],
                                                     mes['message_id'])
                    except:
                        pass

                try:
                    await bot.delete_message(mes['userid'],
                                             mes['message_id'])
                except:
                    pass

                await message_log.delete_one({'_id': mes['_id']})

        else:
            await message_log.delete_one({'advert_id': advert_id})

        lang = await get_lang(companie['owner'])
        await bot.send_message(companie['owner'],
            t('companies.end_company', lang)
        )

async def generate_message(userid: int, company_id: ObjectId, lang = None):
    """ Собирает сообщение и публикует его у пользователя

        message: {
            "ru": {
                "text": str,
                "markup": [{"name": "url"}],
                "parse_mode": str, # Mardown | HTML
                "image": str (url отправленного файла)
            }
        }

    """
    if not lang: lang = await get_lang(userid)

    companie = await companies.find_one({'_id': company_id})
    if companie and lang in companie['message'].keys():
        message = companie['message'][lang]

        text = message['text']
        parse_mode = message['parse_mode']
        image = message['image']

        b_dct = {}
        for key, value in message['markup'].items():
            b_dct[key] =  {'url': value}
        inline = InlineKeyboardMarkup(b_dct)

        if image:
            m = await bot.send_photo(userid, image, text, parse_mode, 
                                     reply_markup=inline)
        else:
            m = await bot.send_message(userid, text, 
                                       parse_mode=parse_mode, reply_markup=inline)
        return m.id
    return None

async def nextinqueue(userid: int, lang = None) -> Union[ObjectId, None]:
    """ Создаёт словарь с количеством показов каждой компании, после выбирает первую компанию какую компанию активировать
    """
    if not lang: lang = await get_lang(userid)

    count_dct, permissions = {}, {}
    # Смотрим на сообщения по этой компании уже отправленные пользователю
    messages = await message_log.find({'userid': userid})
    # Получаем активные компании
    comps = await companies.find(
        {'status': True, 'langs': {'$in': [lang]} }, 
        {'_id': 1, 'one_message': 1, 'min_timeout': 1})

    # Создаём структуру 
    for i in comps: 
        count_dct[i['_id']] = 0
        permissions[i['_id']] = {'one_message': i['one_message'],
                                 'min_timeout': i['min_timeout'],
                                 'last_send': -1
                                 }

    # Проверяем, есть ли активные компании
    if count_dct:
        # Считаем сколько показов было для человека по этой рекламе
        for mes in messages:
            # Проверка на включена ли компания
            if mes['advert_id'] in count_dct:
                count_dct[mes['advert_id']] += 1

                send_time = mes['_id'].generation_time
                now = datetime.now(timezone.utc)
                delta = now - send_time # Сколько секунд назад было отправлено сообщение

                # Сохраняем время последней отправки (последнее = наименьшее)
                if delta.seconds < permissions[mes['advert_id']]['last_send'] or \
                    permissions[mes['advert_id']]['last_send'] == -1:
                    permissions[mes['advert_id']]['last_send'] = delta.seconds

        result_dct = count_dct.copy()
        for key, value in count_dct.items():
            if value > 0:
                # Если уже отправлено 1 сообщение по этой рассылке, то не выдаём его в очереди
                if permissions[key]['one_message']: del result_dct[key]
                # Если компания ещё не отдохнула от прошлого оповещения, то удаляем
                if permissions[mes['advert_id']]['last_send'] < permissions[key]['min_timeout']:
                    del result_dct[key]

        if result_dct.values():
            # Показы распределяются равномерно 
            min_value = min(count_dct.values())
            min_keys = list(filter(lambda k: count_dct[k] == min_value, count_dct))
            r_key = random.choice(min_keys)

            return r_key
    return None
