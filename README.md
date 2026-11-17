# FlowBoard — Django 5 + PostgreSQL

Современное веб-приложение для управления проектами и спринт-задачами (Канбан-доска + Bento-аналитика), построенное на **Django 5** и **PostgreSQL**.

## Стек и особенности
- **Backend**: Django 5.2, `psycopg[binary]` (PostgreSQL драйвер v3).
- **Конфигурация через ENV**: Все параметры подключения к PostgreSQL и настройки Django берутся из переменных окружения (или `.env` файла) без хардкода.
- **UI/UX**: Тёмный интерфейс в стиле современных продуктовых дашбордов (Tailwind CSS, шрифты Inter + JetBrains Mono), фильтрация по проектам и приоритетам, поиск, быстрые переходы статусов и генерация демо-данных в 1 клик.
- **Готовность к миграциям**: Начальная схема (`Project`, `Task`) зафиксирована в `board/migrations/0001_initial.py`.

## Переменные окружения

Скопируйте `.env.example` в `.env` или передайте переменные напрямую в окружение:

```bash
cp .env.example .env
```

Поддерживаются стандартные переменные PostgreSQL:
- `POSTGRES_DB` (или `DB_NAME`, по умолчанию `flowboard`)
- `POSTGRES_USER` (или `DB_USER`, по умолчанию `postgres`)
- `POSTGRES_PASSWORD` (или `DB_PASSWORD`, по умолчанию `postgres`)
- `POSTGRES_HOST` (или `DB_HOST`, по умолчанию `localhost`)
- `POSTGRES_PORT` (или `DB_PORT`, по умолчанию `5432`)
- Либо единая строка подключения `DATABASE_URL=postgres://user:password@host:5432/dbname`

## Запуск проекта

1. Активируйте виртуальное окружение (уже создано в `.venv`):
   ```bash
   source .venv/bin/activate
   ```
2. Примените миграции к вашей базе PostgreSQL:
   ```bash
   python manage.py migrate
   ```
3. Запустите сервер разработки:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
