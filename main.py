import sqlite3
import requests
from requests.exceptions import ConnectionError

name = "Не выбран"
token = ""
secret = ""
url_api = ""
lang = "ru"
conn = sqlite3.connect('sqlite_dadata.db')
cursor = conn.cursor()


def db_create():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
   ID INTEGER PRIMARY KEY,
   name TEXT,
   token TEXT UNIQUE,
   secret TEXT UNIQUE,
   url_api TEXT);
""")
    conn.commit()
    cursor.execute("SELECT COUNT (*) from users")
    count = cursor.fetchone()
    if count[0] == 0:
        print("БД пуста, необходимо добавить пользователя")
        db_user_add()


def db_user_add():
    name = input('Введите имя пользователя: ')
    token = input('Введите токен API: ')
    secret = input('Введите секретный ключ: ')
    url_api = input('Введите базовый URL сервиса (по умолчанию установлен "dadata.ru/"): ')
    if url_api == "":
        url_api = "dadata.ru/"
    cursor.execute("INSERT INTO users (name, token, secret, url_api) VALUES (?,?,?,?)", (name, token, secret, url_api))
    conn.commit()
    menu_user()


def menu():
    print("Текущий пользователь: ", name, ", язык вывода результата: ", lang)
    print("Выберите пункт меню:")
    print("1 - Поиск по адресу")
    print("2 - Меню пользователя")
    print("0 - Выход из программы")
    main_menu = int(input())
    if main_menu == 1:
        search_api()
    elif main_menu == 2:
        menu_user()
    elif main_menu == 0:
        close()


def menu_user():
    global lang
    print("Текущий пользователь: ", name, ", язык вывода результата: ", lang)
    if name != "Не выбран":
        print("Token: ", token)
        print("Secret_KEY: ", secret)
        print("URL: ", url_api)
    print("1 - Выбор/Смена пользователя")
    print("2 - Выбор языка ответа (En/Ru)")
    print("3 - Добавить пользователя")
    if name != "Не выбран":
        print("4 - Возврат к предыдущему меню")
    print("0 - Выход из программы")
    menu_user = int(input())
    if menu_user == 3:
        db_user_add()
    if menu_user == 4:
        menu()
    if menu_user == 2:
        print("Выберите язык ответа:")
        print("1 - En")
        print("2 - Ru")
        lang = int(input())
        if lang == 2:
            lang = "ru"
        else:
            lang = "en"
        menu()
    if menu_user == 1:
        db_user_all()
        menu()
    if menu_user == 0:
        close()


def db_user_all():
    global name
    global token
    global secret
    global url_api
    print("Выберите пользователя: ")
    cursor.execute("SELECT id, name FROM users;")
    for row in cursor.fetchall():
        id_user = row[0]
        name_user = row[1]
        print(id_user, name_user)
    number = int(input())
    [user] = cursor.execute(f"SELECT token, secret, url_api, name FROM users WHERE ID = ?", [number])
    token = user[0]
    secret = user[1]
    url_api = user[2]
    name = user[3]


def close():
    if conn:
        conn.close()
    exit()


def search_api():
    try:
        url = 'https://suggestions.' + url_api + 'suggestions/api/4_1/rs/suggest/address'
        query_user = input('Введите адрес: ')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': "\'Token " + token + "\'",
            'X-Secret': secret,
        }
        json_data = {'query': query_user, 'count': 20, "language": lang}
        response = requests.post(url, headers=headers, json=json_data).json()
        json_data = response['suggestions']
        i = 1
        for x in json_data:
            print(i, x.get('value'))
            i += 1
        number = int(input("Введите правильный адрес: "))
        query_user = response['suggestions'][number]['value']
        json_data = [query_user, ]
        url = 'https://cleaner.' + url_api + 'api/v1/clean/address'
        response = requests.post(url, headers=headers, json=json_data).json()
        print("----------------------------------------------------------------------------------")
        print("Выбранный адрес: ", response[0]['source'])
        print("Долгота: ", response[0]['geo_lat'], "Широта: ", response[0]['geo_lon'])
        print("----------------------------------------------------------------------------------")
    except ConnectionError:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Не верные данные пользователя, проверьте пользователя")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        menu()


db_create()
menu_user()
