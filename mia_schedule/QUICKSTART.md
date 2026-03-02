# SUTE Schedule - Инструкции по запуску

## 🚀 Быстрый старт (5 минут)

### Шаг 1: Клонирование и переход в папку

```bash
cd /home/nakata/MIA/mia_schedule
```

### Шаг 2: Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate.fish  # Для Fish shell
# ИЛИ
source venv/bin/activate  # Для Bash/Zsh
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Запуск приложения

```bash
python app.py
```

**Результат**: Приложение запустится на `http://127.0.0.1:5000`

Откройте браузер и перейдите на `http://127.0.0.1:5000`

---

## 📋 Детальные инструкции

### Для Linux/Mac (Fish shell):

```bash
cd /home/nakata/MIA/mia_schedule
python3 -m venv venv
source venv/bin/activate.fish
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### Для Linux/Mac (Bash/Zsh):

```bash
cd /home/nakata/MIA/mia_schedule
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### Для Windows (PowerShell):

```powershell
cd \path\to\mia_schedule
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### Для Windows (CMD):

```cmd
cd \path\to\mia_schedule
python -m venv venv
venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

---

## 🎯 Что происходит при запуске

1. Flask сервер стартует на `http://127.0.0.1:5000`
2. Логирование выводится в консоль
3. Приложение готово к использованию

```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

---

## 🌐 Использование приложения

### В браузере:

1. Откройте `http://127.0.0.1:5000`
2. Выберите факультет → курс → группу
3. Кликните "Продовжити" (или "Continue")
4. Смотрите расписание на этой неделе

### Функции:

- **Переключение недель**: Текущая, следующая, предыдущая неделя
- **Смена языка**: Верхний правый угол (UK/EN)
- **Обновление расписания**: При смене курса автоматически обновляется

---

## 🔧 Конфигурация

### Переменные окружения (.env файл):

Создайте файл `.env` в корне проекта:

```bash
DEBUG=False
HOST=127.0.0.1
PORT=5000
USE_CACHE=True
CACHE_LIFETIME_HOURS=24
```

---

## 🧪 Тестирование Backend

```bash
python tests/test_backend.py
```

---

## 📊 Проверка установки

Убедитесь что все установилось:

```bash
python -c "import flask; import pydantic; import requests; print('✅ All dependencies installed')"
```

---

## ⚠️ Если есть ошибки

### Ошибка: "No module named 'flask'"

```bash
pip install -r requirements.txt
```

### Ошибка: "Address already in use"

Порт 5000 занят. Используйте другой порт:

```bash
DEBUG=True PORT=8000 python app.py
```

### Ошибка при запуске на Windows

Убедитесь что используете Python 3.8+:

```bash
python --version
```

---

## 🎯 Структура проекта

```
mia_schedule/
├── app.py                  # Главное приложение Flask
├── requirements.txt        # Зависимости
├── .gitignore
├── README.md
│
├── backend/
│   ├── schedule_service.py # Основной сервис
│   ├── fetcher/           # Загрузка расписания
│   ├── parser/            # Парсинг HTML
│   ├── storage/           # Сохранение данных
│   └── models/            # Pydantic модели
│
├── frontend/
│   ├── templates/         # HTML файлы
│   │   ├── index.html
│   │   └── base.html
│   └── static/            # CSS, JS
│       ├── css/
│       ├── js/
│       └── images/
│
├── config/
│   ├── settings.py        # Конфигурация
│   └── i18n.py           # Переводы (UK/EN)
│
├── data/                   # Кэш расписания
│   └── schedules/
│
└── tests/
    └── test_backend.py    # Тесты
```

---

## 🚀 Production запуск

Для более надежного запуска используйте Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

---

## 📞 Автор

[@nakata27](https://github.com/nakata27)

## 📄 Лицензия

MIT License

