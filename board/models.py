from typing import ClassVar

from django.db import models


class Project(models.Model):
    COLOR_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("indigo", "Indigo"),
        ("emerald", "Emerald"),
        ("amber", "Amber"),
        ("rose", "Rose"),
        ("sky", "Sky"),
        ("violet", "Violet"),
    ]

    name = models.CharField("Название проекта", max_length=120)
    description = models.TextField("Описание", blank=True)
    color = models.CharField("Цвет", max_length=20, choices=COLOR_CHOICES, default="indigo")
    is_archived = models.BooleanField("В архиве", default=False)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["-created_at"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self) -> str:
        return self.name

    @property
    def progress_percent(self) -> int:
        total = self.tasks.count()
        if total == 0:
            return 0
        done = self.tasks.filter(status=Task.Status.DONE).count()
        return int((done / total) * 100)


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "К выполнению"
        IN_PROGRESS = "in_progress", "В работе"
        REVIEW = "review", "На проверке"
        DONE = "done", "Готово"

    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"
        CRITICAL = "critical", "Критичный"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Проект",
        null=True,
        blank=True,
    )
    title = models.CharField("Заголовок", max_length=200)
    description = models.TextField("Описание", blank=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        db_index=True,
    )
    priority = models.CharField(
        "Приоритет",
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
    )
    tag = models.CharField("Тег / Категория", max_length=50, blank=True, default="Feature")
    due_date = models.DateField("Дедлайн", null=True, blank=True)
    estimate_hours = models.PositiveSmallIntegerField("Оценка (ч)", default=2)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering: ClassVar[list] = [
            models.Case(
                models.When(priority="critical", then=0),
                models.When(priority="high", then=1),
                models.When(priority="medium", then=2),
                models.When(priority="low", then=3),
                default=4,
                output_field=models.IntegerField(),
            ),
            "-created_at",
        ]
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self) -> str:
        return self.title
