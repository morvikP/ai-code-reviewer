# AI Code Reviewer

Минималистичный CLI-инструмент для автоматического код-ревью через DeepSeek API. Написан с нуля на Python — никаких фреймворков и обёрток, только чистые HTTP-запросы.

## Возможности

- ✅ Ревью отдельных файлов (`.js`, `.py`, `.html`, `.css` и других)
- ✅ Выбор модели: `deepseek-chat` (по умолчанию) или `deepseek-reasoner`
- ✅ Фокус-темы: `security`, `performance`, `readability`, `bugs`
- ✅ Сохранение ревью в Markdown-файл
- ✅ Рекурсивное ревью всей папки
- ✅ Дифф-режим — сравнение двух версий файла
- ✅ Цветной вывод в терминале
- ✅ Понятные сообщения об ошибках (без Python traceback'ов)

## Установка

```bash
# Клонируй репозиторий
git clone https://github.com/morvikP/ai-code-reviewer.git
cd ai-code-reviewer

# Никаких зависимостей — только стандартная библиотека Python!
```

## Настройка

1. Получи API-ключ DeepSeek на [platform.deepseek.com](https://platform.deepseek.com/api_keys)
2. Создай файл `.env` в папке проекта:

```bash
cp .env.example .env
```

3. Открой `.env` и вставь свой ключ:

```
DEEPSEEK_API_KEY=sk-твой-ключ-здесь
```

Или установи переменную окружения:

```bash
# Windows (cmd)
set DEEPSEEK_API_KEY=sk-твой-ключ-здесь

# Windows (PowerShell)
$env:DEEPSEEK_API_KEY="sk-твой-ключ-здесь"

# Linux/Mac
export DEEPSEEK_API_KEY=sk-твой-ключ-здесь
```

## Использование

### Базовое ревью

```bash
python review.py путь/к/файлу.py
```

### Выбор модели

```bash
python review.py file.js --model deepseek-reasoner
```

### Фокус на конкретную тему

```bash
python review.py file.py --focus security     # Безопасность
python review.py file.py --focus performance  # Производительность
python review.py file.py --focus readability  # Читаемость
python review.py file.py --focus bugs         # Поиск багов
```

### Сохранение ревью в файл

```bash
python review.py file.html --output review.md
```

### Ревью всей папки

```bash
python review.py ./my-project --recursive
```

### Дифф-режим (сравнение двух версий)

```bash
python review.py old.py new.py --diff
```

## Скриншот

![AI Code Reviewer в работе](screenshot.png)

## Как это работает

1. Программа читает исходный файл
2. Формирует структурированный промпт для код-ревью
3. Отправляет HTTP POST запрос на `https://api.deepseek.com/v1/chat/completions`
4. Парсит JSON-ответ от модели
5. Выводит ревью в красивом форматированном виде

## Структура проекта

```
ai-code-reviewer/
├── review.py          # Главная CLI-программа
├── .env.example       # Шаблон для API-ключа
├── .gitignore         # Защищает .env от коммита
└── README.md          # Этот файл
```

## Что я узнал

- Как делать "ручные" HTTP-запросы к LLM API
- Почему API-ключи нельзя хранить в коде
- Как работают Cline, Aider и OpenCode под капотом
- Парсинг JSON и обработка ошибок в сетевых приложениях

## Лицензия

MIT
