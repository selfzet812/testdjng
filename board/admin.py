from django.contrib import admin
from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "is_archived", "created_at")
    list_filter = ("color", "is_archived")
    search_fields = ("name", "description")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "tag", "due_date", "estimate_hours", "created_at")
    list_filter = ("status", "priority", "project", "tag")
    search_fields = ("title", "description", "tag")
    list_editable = ("status", "priority")
