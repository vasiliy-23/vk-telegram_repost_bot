import urllib.request
from re import findall, split
from aiogram import Bot, types, Dispatcher
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from itertools import count
from random import random, randint, randrange
from dotenv import load_dotenv, find_dotenv
from auth_data import USER_ID, CHANNEL_ID, token, LOGIN, PASSWORD, VK_USER_ID, VK_TOKEN 
import aiogram.utils.markdown as fmt
import os, sys, vk_api, json, string, time, random, urllib, threading, nltk, re, aioschedule, asyncio, schedule

load_dotenv(find_dotenv())

USER_ID = USER_ID
CHANNEL_ID = CHANNEL_ID
bot = Bot(token = token)
dp = Dispatcher(bot)


LOGIN = LOGIN
PASSWORD = PASSWORD
VK_USER_ID = VK_USER_ID
VK_TOKEN = VK_TOKEN



def captcha_handler(captcha):
    
    key = input("Совершено большое количество запросов, перейдите по ссылке и ввидите капчу с картинки {0}: ".format(captcha.get_url())).strip()

    return captcha.try_again(key)


async def on_startup1():
     
    # ======= Открываем сессию  с VK =======
    vk_session = vk_api.VkApi(LOGIN, PASSWORD, captcha_handler=captcha_handler)
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk = vk_session.get_api()
    
    
    # ======= считываем список пользователей =======
    file_id = open(os.path.join(sys.path[0],'id_users.txt'), 'r')
    data_list = file_id.readlines()
    id_list = []
    for line in data_list:
        id_list.append(line.strip())

    int_cicle = 0
       
    # ======= начинаем перебирать каждого пользователя =======
    for id_user in id_list:
        
        # создаем директорию с именем пользователя, если нет
        newpath = os.path.join(sys.path[0], id_user)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        
        # посылаем запрос к VK API, count свой, но не более 200
        response = vk.photos.get(album_id = 'wall', owner_id = int(id_user), count = 6, rev = 1)
        
        # работаем с каждой полученной фотографией
        for i in range(len(response["items"])):
           if int_cicle >=6:
            int_cicle = 1
           else:
            int_cicle +=1

           print(int_cicle)

           with open("url_photo.txt", "a+") as file:
            # берём ссылку на максимальный размер фотографии
            photo_url = str(response["items"][i]["sizes"][len(response["items"][i]["sizes"])-1]["url"])
            
            # собираем имена постов и определяет количество слов
            posts = vk.wall.get(owner_id= int(id_user), offset = int_cicle, count=1)['items']
            posts_strings = str([post['text'] for post in posts])
            wcount = len(findall(r'[^\s\d]+', str(posts_strings)))
            print('количество слов в посте:', wcount)
            print('текст в посте:', posts_strings)

            
            # скачиваем фото в папку с ID пользователя
            #urllib.request.urlretrieve(photo_url, newpath + '/' + str(response["items"][i]['id']) + '.jpg')
            
            ignore = photo_url
            global triger
            triger = posts_strings


            def check():
                with open('url_photo.txt') as f:
                    datafile = f.readlines()
                for line in datafile:
                    if ignore in line:
                        return True
                return False

            if check():
                print("новых постов нет")
                
            else:
                if wcount >=3:

                    print('скорее всего реклама, пропускаем...')

                    def check_triger_name():
                        global triger
                        with open('triger_name.txt') as f:
                            datafile = f.readlines()
                        for line in datafile:
                            if triger in line:
                                return True
                        return False

                    if check_triger_name():

                        with open("url_photo.txt", "a") as file:
                            file.write(photo_url + '\n')
                            await bot.send_photo(CHANNEL_ID, photo = photo_url)

                    else:
                        print("тригер не был обнаржуен в файле")

                else:

                    with open("url_photo.txt", "a") as file:
                        file.write(photo_url + '\n')
                        await bot.send_photo(CHANNEL_ID, photo = photo_url)

            
async def scheduler():
    aioschedule.every().day.at("22:30").do(on_startup1)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())

 


                        

if __name__ == "__main__":
 executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
 
 
    
