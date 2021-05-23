from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_todo, name='create_todo'),
    path('todo/<id>', views.todo_detail, name='todo_detail'),
    path('todo-delete/<id>', views.todo_delete, name='todo-delete'),
    path('edit-todo/<id>', views.todo_edit, name='edit-todo'),
]
