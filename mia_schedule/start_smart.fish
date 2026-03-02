#!/usr/bin/env fish

# MIA Schedule - Smart Start Script
# Автоматически находит свободный порт и запускает приложение

set -l DEFAULT_PORT 5000
set -l MAX_ATTEMPTS 10

echo "🚀 Запуск MIA Schedule App..."
echo ""

# Проверяем наличие виртуального окружения
if not test -d venv
    echo "⚠️  Виртуальное окружение не найдено. Создаём..."
    python -m venv venv
    source venv/bin/activate.fish
    echo "📦 Устанавливаем зависимости..."
    pip install -r requirements.txt
else
    source venv/bin/activate.fish
end

# Функция проверки доступности порта
function port_is_free
    set -l port $argv[1]
    not lsof -i:$port >/dev/null 2>&1
end

# Ищем свободный порт
set -l port $DEFAULT_PORT
set -l attempts 0

while test $attempts -lt $MAX_ATTEMPTS
    if port_is_free $port
        break
    end

    echo "⚠️  Порт $port занят, пробуем $port+1..."
    set port (math $port + 1)
    set attempts (math $attempts + 1)
end

if test $attempts -eq $MAX_ATTEMPTS
    echo "❌ Не удалось найти свободный порт после $MAX_ATTEMPTS попыток"
    exit 1
end

# Запускаем приложение
echo ""
echo "✅ Запуск на порту $port"
echo "🌐 Откройте в браузере: http://127.0.0.1:$port"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

set -x PORT $port
python app.py

