from django.contrib import admin
from .models import Workspace, Category, Color, Task, Subtask

# Register your models here.
admin.site.register(Workspace)
admin.site.register(Category)
admin.site.register(Task)
admin.site.register(Subtask)
