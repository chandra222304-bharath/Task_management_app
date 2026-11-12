from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return f"{self.title} ({self.status}) - {self.user.username}"

    def clean(self):
        super().clean()
        if self.start_date and self.due_date:
            if self.start_date > self.due_date:
                raise ValidationError({
                    'due_date': 'Due date cannot be earlier than start date.'
                })

    @property
    def is_overdue(self):
        """Returns True if task is not completed and past due date."""
        if self.status != 'Completed' and self.due_date:
            return self.due_date < timezone.now().date()
        return False

    @property
    def days_remaining(self):
        """Returns number of days remaining until due date (negative if overdue)."""
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None
