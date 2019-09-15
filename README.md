
# Магазин  для  Telegram

## Пример работы:


![Screenshot](examination_vk.gif)

![Screenshot](examination_tg.gif) 

## Перед первым запуском необходимо выполнить ряд обязательных условий :



<b>1) Зарегистрируетесь на Heroku и создайте приложение (app) </b>

https://id.heroku.com/login


Привяжите GitHub и залейте код.
Это  можно осуществить на вкладке Deploy. После подключения выполните Deploy Branch.

В разделе Settings приложения необходимо создать переменные с названиями:
MOLTIN_CLIENT_ID, MOLTIN_CLIENT_SECRET, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT и TELEGRAM_BOT_TOKEN .Значения для них получим на следующих шагах. 

<b>2) Зарегистрировать бота Telegram  и получить API ключ </b>

Написать Отцу ботов
/start
/newbot

Передать значение токена TELEGRAM_BOT_TOKEN  соответсвенно, в разделе Settings приложения на Heroku


<b>3)Зарегистрируйтесь в Moltin и создайте свой Магазин</b>

https://www.moltin.com/

в разделе Home будет теблица Your API keys
передайте соответвующие значение переменным MOLTIN_CLIENT_ID и MOLTIN_CLIENT_SECRET

в разделе Catalogue - создайте товары 




<b>4)Зарегистрируйтесь в redislabs</b>

Для хранения сервисной информации приложение использует NoSQL базу данных Redis.
Поэтому необходимо зарегистрироваться на сайте и создать базу данных:

https://redislabs.com/

Создать базу данных можно по ссылке:

https://app.redislabs.com/#/subscriptions

В созданной БД во вкладке "Configuration"  из строки 'Endpoint' скопировать данные и передать значения переменной  DATABASE_HOST и DATABASE_PORT,а
из 'Access Control & Security' переменной DATABASE_PASSWORD

## Установка  и запуск на локальной машине
Запуск бота также возможен  на локальной машине ,для этого в каталоге с модулем необходимо создать файл .env  в нем объявить переменные MOLTIN_CLIENT_ID, MOLTIN_CLIENT_SECRET, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT и TELEGRAM_BOT_TOKEN   и передать им  значения полученные в предыдущих шагах.

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей: 

```
pip3 install -r requirements.txt

```


```

$python3 telegram_shop_bot.py

```




## Запуск
Перейдите Heroku в раздел Resources и передвинув ползунки ботов вправо (через редактирование) разрешить запуск приложений.




## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков dvmn.org.

2019 Dark_Dmake