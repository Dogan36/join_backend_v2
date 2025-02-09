
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from colors.models import Color
User = get_user_model()

class Workspace(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='workspaces', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')
    join_code = models.CharField(max_length=8, blank=True, editable=False, unique=True) 

    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = uuid.uuid4().hex[:8]  # Erstellt einen 8 Zeichen langen Hexadezimalcode
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='categories')
    
    def __str__(self):
         return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('done', 'Done'),
        ('awaitingFeedback', 'Awaiting Feedback'),
        ('todo', 'To Do'),
        ('inProgress', 'In Progress'),
    ]
    PRIO_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    selected_contacts = models.ManyToManyField(User, related_name='selected_tasks', blank=True)
    due_date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    prio = models.CharField(max_length=10, choices=PRIO_CHOICES, default='medium')
    def __str__(self):
        return self.name
    
class Subtask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    name = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)


    def __str__(self):
        return self.name

