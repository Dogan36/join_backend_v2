
from django.contrib.auth.models import AbstractBaseUser,  PermissionsMixin
from django.db import models
from django.contrib.auth.models import BaseUserManager
from colors.models import Color

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Die E-Mail-Adresse ist erforderlich')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser muss is_staff=True haben.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser muss is_superuser=True haben.')

        return self.create_user(email, name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()
    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True)
    avatar = models.CharField(max_length=2, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    
    
    def __str__(self):
        return self.email
    
   
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contacts')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.CharField(max_length=2, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.name

