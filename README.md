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

## Запуск через Docker

Все файлы для контейнеризации находятся в директории `docker/` (`compose.yaml`, `Dockerfile`, `.dockerignore`, `generate_ssl.sh`, `nginx/`). Стек поднимает три сервиса: **PostgreSQL 18** (`db`), **Django + Gunicorn** (`webapp`) и **Nginx с HTTPS** (`nginx`).

### 1. Подготовьте `.env` в корне репозитория
Скопируйте шаблон и укажите `POSTGRES_HOST=db` (имя сервиса БД в `docker/compose.yaml`), иначе `webapp` не сможет подключиться к базе:

```bash
cp .env.example .env
```

Проверьте ключевые значения в `.env`:
- `POSTGRES_HOST=db` *(обязательно для Docker)*
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `DJANGO_SECRET_KEY` и `DJANGO_DEBUG=False` (для продакшена)

### 2. Сгенерируйте SSL-сертификат для Nginx
Без сертификатов в `docker/nginx/ssl/` контейнер `nginx` не стартует. Скрипт можно запускать из корня или из папки `docker/`, передав IP/домен сервера (по умолчанию `127.0.0.1`):

```bash
./docker/generate_ssl.sh 127.0.0.1
```

### 3. Соберите и запустите стек
Убедитесь, что на хосте свободны порты **80** и **443**.

Из папки `docker/`:
```bash
cd docker
docker compose up --build -d
```

Или из корня репозитория:
```bash
docker compose -f docker/compose.yaml up --build -d
```

При старте `webapp` автоматически дождётся готовности PostgreSQL, применит миграции (`migrate`) и соберёт статику (`collectstatic`).

### 4. Проверка и управление
- Приложение доступно по `https://<ваш-хост>` (HTTP на 80 порту автоматически редиректит на HTTPS; для самоподписанного сертификата браузер покажет предупреждение).
- Проверить статус и healthcheck'и:
  ```bash
  docker compose -f docker/compose.yaml ps
  ```
- Посмотреть логи:
  ```bash
  docker compose -f docker/compose.yaml logs -f
  ```
- Остановить контейнеры (данные БД сохранятся в volume `postgres_data`):
  ```bash
  docker compose -f docker/compose.yaml down
  ```

### Ручная сборка образа (без Compose)
Контекстом сборки должен оставаться корень проекта:
```bash
# из корня репозитория
docker build -f docker/Dockerfile -t flowboard .

# или из папки docker/
cd docker && docker build -f Dockerfile -t flowboard ..
```
