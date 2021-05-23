from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import TodoForm
from .models import Todo

# Create your views here.


def get_showing_todos(request, todos):
    if request.GET and request.GET.get('filter'):
        if request.GET.get('filter') == 'complete':
            return todos.filter(is_completed=True)
        if request.GET.get('filter') == 'incomplete':
            return todos.filter(is_completed=False)
    return todos


def index(request):
    todos = Todo.objects.all()
    completed_count = todos.filter(is_completed=True).count()
    incomplete_count = todos.filter(is_completed=False).count()
    all_count = todos.count()
    context = {
        'todos': get_showing_todos(request, todos),
        'completed_count': completed_count,
        'incomplete_count': incomplete_count,
        'all_count': all_count,
    }
    return render(request, 'index.html', context)


def create_todo(request):
    form = TodoForm()
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        is_completed = request.POST.get('is_completed', False)
        print(is_completed)

        todo = Todo()
        todo.title = title
        todo.description = description
        todo.is_completed = True if is_completed == 'on' else False

        todo.save()

        return HttpResponseRedirect(reverse('todo:todo_detail', kwargs={'id': todo.pk}))

    context = {
        'form': form,
    }
    return render(request, 'create-todo.html', context)


def todo_detail(request, id):
    todo = get_object_or_404(Todo, pk=id)
    context = {
        'todo': todo,
    }
    return render(request, 'todo-detail.html', context)


def handel_not_found(request, exception):
    return render(request, '404.html')


def handel_server_error(request):
    return render(request, 'server-error.html')


def todo_delete(request, id):
    todo = get_object_or_404(Todo, pk=id)
    context = {
        'todo': todo,
    }
    if request.method == 'POST':
        todo.delete()
        return HttpResponseRedirect(reverse('todo:index'))
    return render(request, 'todo-delete.html', context)


def todo_edit(request, id):
    todo = get_object_or_404(Todo, pk=id)
    form = TodoForm(instance=todo)
    context = {
        'todo': todo,
        'form': form,
    }
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        is_completed = request.POST.get('is_completed', False)

        todo.title = title
        todo.description = description
        todo.is_completed = True if is_completed == 'on' else False

        todo.save()

        return HttpResponseRedirect(reverse('todo:todo_detail', kwargs={'id': todo.pk}))
    return render(request, 'todo-edit.html', context)
