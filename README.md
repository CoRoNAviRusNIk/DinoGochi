# DinoGochi - telegram.bot на python
Телеграмм бот по типу тамагочи, только с динозаврами!
Игровой бот где вы должны ухаживать за своим динозавров, но тут присутствуют нотки рпг.

 > Ссылки:
 > - Бот: https://t.me/DinoGochi_bot
 > - Создатель: https://t.me/AS1AW

### 🦕 | О боте

- В боте вы должны заботится о своём динозавре. Развлекайте его, кормите и тд.
![Профиль](images/preview/profile_i.png)

- Путешествуйте вместе с динозавром в лучших идеях Fallout 86.
![Профиль](images/preview/journey_i.png)

- Занимайтесь крафтом, творите!
![Крафт](images/preview/craft_i.png)

- Покоряйте подземелья, сражайтесь с злыми тварями!
![Подземелья](images/preview/dungeons_i.png)

- Скорее присоединяйтесь в этот рпг мир динозавров!

### 🛠 | Для запуска бота
- Установите 3-ю версию пайтона (рекомендуемая 3.10.4 / 3.9.6)
- Далее, установите все библиотеки из файла requirements.txt
>
    # Windows
    pip install requirements.txt

>
    # Linux
    pip install -r requirements.txt

Если вы используете **онлайн базу**, то следуйте этим 4-ём пунктам:

- Далее зайдите на https://account.mongodb.com/account/login
- Зарегестрируйте аккаунт и получите бесплатный кластер m0 / m1
- В файле config.py замените CLUSTER_CLIENT на >

  > CLUSTER_CLIENT = pymongo.MongoClient("mongodb+srv://bot:PASSWORD@cluster0.CLUSTER_TOKEN.mongodb.net/<dbname>?retryWrites=true&w=majority")

- Далее создайте базу с именем **bot** и коллекциями в ней:

 > bot:
 > - users
 > - dungeons
 > - management

- В коллекцие **management** создайте документ:

 > - _id: "market"
 > - products: Object

 > - _id: "referal_system"
 > - codes: Array

- В файле **config.py** добавьте токен и имя бота

> - BOT_TOKEN = "Токен бота из BotFather"
> - BOT_NAME = 'Имя бота' #Да это важно!

- Запустите файл main.py

### 📜 | Последнее

Время потраченое с начала разработки 1.0.2 > <a href="https://wakatime.com/badge/github/Rimuwu/DinoGochi"><img src="https://wakatime.com/badge/github/Rimuwu/DinoGochi.svg" alt="wakatime"></a>

- 1.0.4v - 🌭 | Новая еда и различные улучшения.
- 1.0.3v - 📜 | Квесты.
- 1.0.2v - 🗻 | Обновление подземелий.
