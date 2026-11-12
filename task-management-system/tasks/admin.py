from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'priority',
        'status',
        'start_date',
        'due_date',
        'is_overdue_badge',
        'created_at'
    )
    list_filter = ('status', 'priority', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'user__username', 'user__email')
    date_hierarchy = 'due_date'
    ordering = ('-created_at',)
    list_per_page = 20

    @admin.display(description='Overdue?', boolean=True)
    def is_overdue_badge(self, obj):
        return obj.is_overdue
