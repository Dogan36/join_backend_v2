from django.db import models

class Color(models.Model):
    name = models.CharField(max_length=100)
    hex_value = models.CharField(max_length=7)  # Hex-Farbcode, z.B. #FFFFFF
    
    def __str__(self):
        return self.name
