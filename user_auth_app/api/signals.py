from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models
from django.db.models import Count
from ..models import CustomUser, Contact
from colors.models import Color
import random

import logging

@receiver(pre_save, sender=CustomUser)
def assign_random_color(sender, instance, **kwargs):
    if not instance.pk:  # Überprüfe, ob das Objekt neu erstellt wird
        random_color_id = random.randint(1, 30)  # Wähle eine zufällige ID zwischen 1 und 30
        
        try:
            color = Color.objects.get(id=random_color_id)  # Holt die Color Instanz mit dieser ID
        except Color.DoesNotExist:
            logging.error(f"Farbe mit ID {random_color_id} existiert nicht. Setze Standardfarbe.")
            color = Color.objects.first()  # Fallback auf die erste Farbe (oder eine andere Standardfarbe)
        
        instance.color = color  # Weise die Farbe zu, bevor der Benutzer gespeichert wird


@receiver(pre_save, sender=CustomUser)
def assign_avatar(sender, instance, **kwargs):
    name = instance.name
    parts = name.split()
    if len(parts) > 1:
        instance.avatar = f"{parts[0][0]}{parts[-1][0]}".upper()
    else:
        instance.avatar = f"{parts[0][0]}".upper()
        
@receiver(pre_save, sender=Contact)
def assign_random_color(sender, instance, **kwargs):
    if not instance.pk:  # Überprüfe, ob das Objekt neu erstellt wird
        random_color_id = random.randint(1, 30)  # Wähle eine zufällige ID zwischen 1 und 5
        color = Color.objects.get(id=random_color_id)  # Holt die Color Instanz mit dieser ID
        instance.color = color  # Weise die Farbe zu, bevor der Benutzer gespeichert wird


@receiver(pre_save, sender=Contact)
def assign_avatar(sender, instance, **kwargs):
    name = instance.name
    parts = name.split()
    if len(parts) > 1:
        instance.avatar = f"{parts[0][0]}{parts[-1][0]}".upper()
    else:
        instance.avatar = f"{parts[0][0]}".upper()