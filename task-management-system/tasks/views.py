from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import Task
from .forms import TaskForm, UserRegisterForm, UserUpdateForm


# ========================================================
# AUTHENTICATION VIEWS
# ========================================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Welcome {user.username}! Your account has been created successfully.")
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ========================================================
# DASHBOARD VIEW
# ========================================================

@login_required
def dashboard(request):
    user_tasks = Task.objects.filter(user=request.user)
    today = timezone.now().date()

    total_tasks = user_tasks.count()
    pending_tasks = user_tasks.filter(status='Pending').count()
    in_progress_tasks = user_tasks.filter(status='In Progress').count()
    completed_tasks = user_tasks.filter(status='Completed').count()

    # Overdue tasks: past due_date and not completed
    overdue_tasks = user_tasks.filter(due_date__lt=today).exclude(status='Completed').count()

    # Completion percentage
    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

    # Priority counts for chart
    priority_low = user_tasks.filter(priority='Low').count()
    priority_medium = user_tasks.filter(priority='Medium').count()
    priority_high = user_tasks.filter(priority='High').count()

    # Recent tasks (last 5 created)
    recent_tasks = user_tasks.order_by('-created_at')[:5]

    # Upcoming tasks due soon (within next 7 days or closest deadlines)
    upcoming_tasks = user_tasks.filter(due_date__gte=today).exclude(status='Completed').order_by('due_date')[:5]

    context = {
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'completion_rate': completion_rate,
        'priority_low': priority_low,
        'priority_medium': priority_medium,
        'priority_high': priority_high,
        'recent_tasks': recent_tasks,
        'upcoming_tasks': upcoming_tasks,
    }
    return render(request, 'tasks/dashboard.html', context)


# ========================================================
# TASK CRUD VIEWS
# ========================================================

@login_required
def task_list(request):
    user_tasks = Task.objects.filter(user=request.user)
    today = timezone.now().date()

    # 1. Search by title or description
    query = request.GET.get('q', '').strip()
    if query:
        user_tasks = user_tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # 2. Filter by status
    status_filter = request.GET.get('status', '').strip()
    if status_filter in ['Pending', 'In Progress', 'Completed']:
        user_tasks = user_tasks.filter(status=status_filter)

    # 3. Filter by priority
    priority_filter = request.GET.get('priority', '').strip()
    if priority_filter in ['Low', 'Medium', 'High']:
        user_tasks = user_tasks.filter(priority=priority_filter)

    # 4. Filter overdue
    overdue_filter = request.GET.get('overdue', '').strip()
    if overdue_filter == '1':
        user_tasks = user_tasks.filter(due_date__lt=today).exclude(status='Completed')

    # 5. Sorting
    sort_by = request.GET.get('sort', 'created_desc').strip()
    if sort_by == 'due_asc':
        user_tasks = user_tasks.order_by('due_date', 'title')
    elif sort_by == 'due_desc':
        user_tasks = user_tasks.order_by('-due_date', 'title')
    elif sort_by == 'created_asc':
        user_tasks = user_tasks.order_by('created_at')
    elif sort_by == 'priority':
        # Custom sorting logic using Case/When if needed, or simple priority ordering
        user_tasks = user_tasks.order_by('priority', '-created_at')
    else:  # default created_desc
        user_tasks = user_tasks.order_by('-created_at')

    # Pagination: 8 tasks per page
    paginator = Paginator(user_tasks, 8)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    context = {
        'tasks': page_obj,
        'total_count': paginator.count,
        'query': query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'overdue_filter': overdue_filter,
        'sort_by': sort_by,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f"Task '{task.title}' created successfully!")
            return redirect('task_detail', pk=task.pk)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Create New Task',
        'is_edit': False
    })


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f"Task '{task.title}' updated successfully!")
            return redirect('task_detail', pk=task.pk)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task,
        'title': 'Edit Task',
        'is_edit': True
    })


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f"Task '{task_title}' was deleted successfully.")
        return redirect('task_list')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle_status(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if task.status == 'Completed':
        task.status = 'In Progress'
    elif task.status == 'In Progress':
        task.status = 'Completed'
    else:
        task.status = 'Completed'
    task.save()
    messages.success(request, f"Status of '{task.title}' updated to '{task.status}'.")

    # Redirect back to where the user clicked
    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('task_list')


# ========================================================
# USER PROFILE VIEW
# ========================================================

@login_required
def profile_view(request):
    user_tasks = Task.objects.filter(user=request.user)
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(status='Completed').count()
    pending_tasks = user_tasks.filter(status='Pending').count()
    in_progress_tasks = user_tasks.filter(status='In Progress').count()

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserUpdateForm(instance=request.user)

    context = {
        'form': form,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
    }
    return render(request, 'tasks/profile.html', context)
