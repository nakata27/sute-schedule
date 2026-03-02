#!/bin/bash
# MIA Schedule App - Инструкция по первому запуску

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║      🎉 MIA SCHEDULE APP - ПЕРВЫЙ ЗАПУСК 🎉               ║"
echo "║                  Инструкция за 5 минут                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Проверка текущей директории
echo "1️⃣  Проверка директории..."
if [ ! -f "app.py" ]; then
    echo "❌ ОШИБКА: Вы не в директории mia_schedule!"
    echo "   Выполните: cd ~/MIA/mia_schedule"
    exit 1
fi
echo "   ✅ Правильная директория"
echo ""

# Проверка виртуального окружения
echo "2️⃣  Проверка виртуального окружения..."
if [ ! -d "venv" ]; then
    echo "   ⚙️  Создание виртуального окружения..."
    python3 -m venv venv
    echo "   ✅ Виртуальное окружение создано"
else
    echo "   ✅ Виртуальное окружение уже существует"
fi
echo ""

# Активация окружения
echo "3️⃣  Активация виртуального окружения..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "   ✅ Окружение активировано"
else
    echo "   ⚠️  Fish shell обнаружен"
    source venv/bin/activate.fish
    echo "   ✅ Окружение активировано"
fi
echo ""

# Проверка зависимостей
echo "4️⃣  Проверка и установка зависимостей..."
if [ ! -f "venv/lib/python*/site-packages/pydantic" ]; then
    echo "   📦 Установка зависимостей..."
    pip install -r requirements.txt > /dev/null 2>&1
    echo "   ✅ Зависимости установлены"
else
    echo "   ✅ Зависимости уже установлены"
fi
echo ""

# Запуск тестов (опционально)
echo "5️⃣  Желаете ли вы запустить тесты? (y/n)"
read -t 5 -n 1 answer || answer="n"
echo ""

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo "🧪 Запуск тестов backend..."
    python tests/test_backend.py
    echo ""
fi

# Запуск приложения
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           ✅ ВСЕ ГОТОВО К ЗАПУСКУ! 🚀                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Запуск приложения на http://127.0.0.1:5000"
echo ""
echo "Нажмите Ctrl+C для остановки сервера"
echo ""
echo "🌐 Откройте браузер и перейдите на:"
echo "   http://127.0.0.1:5000"
echo ""

# Запуск приложения
python app.py

