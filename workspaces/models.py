import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Workspace(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='workspaces', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')
    join_code = models.CharField(max_length=8, blank=True, editable=False)  # Generierter Code für den Beitritt

    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = uuid.uuid4().hex[:8]  # Erstellt einen 8 Zeichen langen Hexadezimalcode
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name