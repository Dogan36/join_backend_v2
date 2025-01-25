from re import sub
import uuid
from django.db import models
from django.contrib.auth import get_user_model

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

class Color(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=7)  # Hex-Farbcode, z.B. #FFFFFF
    
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
        ('awaiting_feedback', 'Awaiting Feedback'),
        ('todo', 'To Do'),
        ('inprogress', 'In Progress'),
    ]
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    
    def __str__(self):
        return self.name

class Subtask(models.Model):
    done = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')

    def __str__(self):
        return self.name