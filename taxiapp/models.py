from django.db import models
from django.contrib.auth.models import User

class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant')
    name = models.CharField(max_length=400)
    phone = models.CharField(max_length=220)
    address = models.CharField(max_length=500)
    

    def __str__(self):
        return self.name
