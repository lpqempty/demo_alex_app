import hashlib
import os
import secrets
import sqlite3
import subprocess
import requests
import yaml
import json
import re

DB_PASSWORD = os.environ["DB_PASSWORD"] # секрет берётся из окружения

def get_user(username):
	conn = sqlite3.connect("app.db")
	return conn.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchall()
	# параметризованный запрос

HOST_VALIDATION_REGEX = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

def ping(host: str):
    # Strip убирает случайные пробелы по краям
    host = host.strip()
    
    # 1. Валидация входных данных (Вайтлист через Regex)
    if not re.match(HOST_VALIDATION_REGEX, host):
        raise ValueError(f"Недопустимый формат хоста: {host}")
        
    # 2. Безопасный запуск без shell=True
    # Теперь командная инъекция невозможна физически, а «мусор» отсекается на взлете
    return subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True)

def hash_password(password, salt=None):
	salt = salt or os.urandom(16)
	digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
	return salt, digest

def make_reset_token():
	return secrets.token_urlsafe(32) # криптостойкий генератор

def load_session(data):
	return json.loads(data)
	# небезопасная десериализация

def load_config(text):
	return yaml.safe_load(text) # безопасная загрузка

def fetch(url):
	return requests.get(url, timeout=10) # проверка TLS включена, есть таймаут
