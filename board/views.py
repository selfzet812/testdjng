from datetime import date, timedelta
from django.contrib import messages
from django.db import connection
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import Project, Task


@require_GET
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({"status": "ok"}, status=200)
    except Exception:
        return JsonResponse({"status": "error"}, status=503)


def dashboard(request):
    selected_project_id = request.GET.get("project")
    selected_priority = request.GET.get("priority")
    search_query = request.GET.get("q", "").strip()

    projects = Project.objects.filter(is_archived=False).annotate(
        total_tasks=Count("tasks"),
        done_tasks=Count("tasks", filter=Q(tasks__status=Task.Status.DONE)),
    )

    tasks_qs = Task.objects.select_related("project").all()

    selected_project = None
    if selected_project_id:
        selected_project = Project.objects.filter(id=selected_project_id).first()
        if selected_project:
            tasks_qs = tasks_qs.filter(project=selected_project)

    if selected_priority in dict(Task.Priority.choices):
        tasks_qs = tasks_qs.filter(priority=selected_priority)

    if search_query:
        tasks_qs = tasks_qs.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(tag__icontains=search_query)
        )

    columns = [
        {
            "key": Task.Status.TODO,
            "label": "К выполнению",
            "accent": "slate",
            "dot": "bg-slate-400",
            "tasks": [t for t in tasks_qs if t.status == Task.Status.TODO],
        },
        {
            "key": Task.Status.IN_PROGRESS,
            "label": "В работе",
            "accent": "indigo",
            "dot": "bg-indigo-400",
            "tasks": [t for t in tasks_qs if t.status == Task.Status.IN_PROGRESS],
        },
        {
            "key": Task.Status.REVIEW,
            "label": "На проверке",
            "accent": "amber",
            "dot": "bg-amber-400",
            "tasks": [t for t in tasks_qs if t.status == Task.Status.REVIEW],
        },
        {
            "key": Task.Status.DONE,
            "label": "Готово",
            "accent": "emerald",
            "dot": "bg-emerald-400",
            "tasks": [t for t in tasks_qs if t.status == Task.Status.DONE],
        },
    ]

    all_tasks = Task.objects.all()
    total_count = all_tasks.count()
    done_count = all_tasks.filter(status=Task.Status.DONE).count()
    in_progress_count = all_tasks.filter(status=Task.Status.IN_PROGRESS).count()
    critical_count = all_tasks.filter(priority=Task.Priority.CRITICAL).exclude(status=Task.Status.DONE).count()
    total_hours = all_tasks.aggregate(total=Sum("estimate_hours"))["total"] or 0
    completion_rate = int((done_count / total_count) * 100) if total_count else 0

    context = {
        "projects": projects,
        "selected_project": selected_project,
        "selected_priority": selected_priority or "",
        "search_query": search_query,
        "columns": columns,
        "status_choices": Task.Status.choices,
        "priority_choices": Task.Priority.choices,
        "color_choices": Project.COLOR_CHOICES,
        "stats": {
            "total": total_count,
            "done": done_count,
            "in_progress": in_progress_count,
            "critical": critical_count,
            "total_hours": total_hours,
            "completion_rate": completion_rate,
        },
    }
    return render(request, "board/dashboard.html", context)


@require_POST
def create_project(request):
    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()
    color = request.POST.get("color", "indigo")

    if not name:
        messages.error(request, "Укажите название проекта.")
        return redirect("board:dashboard")

    project = Project.objects.create(
        name=name,
        description=description,
        color=color if color in dict(Project.COLOR_CHOICES) else "indigo",
    )
    messages.success(request, f"Проект «{project.name}» создан.")
    return redirect(f"/?project={project.id}")


@require_POST
def create_task(request):
    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    project_id = request.POST.get("project")
    status = request.POST.get("status", Task.Status.TODO)
    priority = request.POST.get("priority", Task.Priority.MEDIUM)
    tag = request.POST.get("tag", "Feature").strip() or "Feature"
    due_date_raw = request.POST.get("due_date", "").strip()
    estimate_raw = request.POST.get("estimate_hours", "2").strip()

    if not title:
        messages.error(request, "Название задачи не может быть пустым.")
        return redirect("board:dashboard")

    project = Project.objects.filter(id=project_id).first() if project_id else None

    try:
        estimate_hours = max(1, min(200, int(estimate_raw)))
    except ValueError:
        estimate_hours = 2

    due_date = None
    if due_date_raw:
        try:
            due_date = date.fromisoformat(due_date_raw)
        except ValueError:
            due_date = None

    Task.objects.create(
        title=title,
        description=description,
        project=project,
        status=status if status in dict(Task.Status.choices) else Task.Status.TODO,
        priority=priority if priority in dict(Task.Priority.choices) else Task.Priority.MEDIUM,
        tag=tag[:50],
        due_date=due_date,
        estimate_hours=estimate_hours,
    )
    messages.success(request, f"Задача «{title}» добавлена.")
    redirect_url = f"/?project={project.id}" if project else "/"
    return redirect(redirect_url)


@require_POST
def update_task_status(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    new_status = request.POST.get("status")
    if new_status in dict(Task.Status.choices):
        task.status = new_status
        task.save(update_fields=["status", "updated_at"])
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    return redirect(next_url)


@require_POST
def delete_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    title = task.title
    task.delete()
    messages.info(request, f"Задача «{title}» удалена.")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    return redirect(next_url)


@require_POST
def seed_demo_data(request):
    if Project.objects.exists() or Task.objects.exists():
        messages.info(request, "Демо-данные уже существуют или база не пуста.")
        return redirect("board:dashboard")

    today = date.today()

    p_backend = Project.objects.create(
        name="Platform Core API",
        description="Микросервисы, PostgreSQL схема и аутентификация",
        color="indigo",
    )
    p_design = Project.objects.create(
        name="UI Design System 2.0",
        description="Новые компоненты дашборда и тёмная тема",
        color="emerald",
    )
    p_growth = Project.objects.create(
        name="AI Analytics Module",
        description="Предиктивная аналитика и отчёты в реальном времени",
        color="violet",
    )

    demo_tasks = [
        Task(
            project=p_backend,
            title="Настроить подключение к PostgreSQL через ENV",
            description="Поддержка DATABASE_URL и POSTGRES_* переменных окружения без хардкода.",
            status=Task.Status.DONE,
            priority=Task.Priority.HIGH,
            tag="Database",
            due_date=today,
            estimate_hours=3,
        ),
        Task(
            project=p_backend,
            title="Добавить индекс и оптимизировать выборку задач",
            description="Использовать select_related и агрегацию на уровне базы данных.",
            status=Task.Status.IN_PROGRESS,
            priority=Task.Priority.CRITICAL,
            tag="Backend",
            due_date=today + timedelta(days=2),
            estimate_hours=5,
        ),
        Task(
            project=p_design,
            title="Сверстать Bento-карточки метрик и Канбан-доску",
            description="Современный минималистичный интерфейс в тёмных тонах с акцентами.",
            status=Task.Status.DONE,
            priority=Task.Priority.MEDIUM,
            tag="UI/UX",
            due_date=today,
            estimate_hours=4,
        ),
        Task(
            project=p_design,
            title="Адаптивные модальные окна создания проектов и задач",
            description="Быстрое добавление сущностей без перезагрузки контекста.",
            status=Task.Status.REVIEW,
            priority=Task.Priority.MEDIUM,
            tag="Frontend",
            due_date=today + timedelta(days=3),
            estimate_hours=3,
        ),
        Task(
            project=p_growth,
            title="Спроектировать модель комментариев и логов активности",
            description="Следующий шаг для расширения проекта новыми Django миграциями.",
            status=Task.Status.TODO,
            priority=Task.Priority.HIGH,
            tag="Architecture",
            due_date=today + timedelta(days=5),
            estimate_hours=6,
        ),
        Task(
            project=p_growth,
            title="Экспорт отчетов по спринтам в CSV / JSON",
            description="Генерация сводной статистики по закрытым часам.",
            status=Task.Status.TODO,
            priority=Task.Priority.LOW,
            tag="Feature",
            due_date=today + timedelta(days=7),
            estimate_hours=4,
        ),
    ]
    Task.objects.bulk_create(demo_tasks)
    messages.success(request, "Демо-проекты и задачи успешно загружены!")
    return redirect("board:dashboard")
