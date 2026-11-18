from django.urls import path
from . import views

app_name = "board"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("health/", views.health_check, name="health_check"),
    path("projects/create/", views.create_project, name="create_project"),
    path("tasks/create/", views.create_task, name="create_task"),
    path("tasks/<int:task_id>/status/", views.update_task_status, name="update_task_status"),
    path("tasks/<int:task_id>/delete/", views.delete_task, name="delete_task"),
    path("seed/", views.seed_demo_data, name="seed_demo_data"),
]
