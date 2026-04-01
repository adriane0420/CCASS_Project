from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('employee', 'Employee'),
    )

    SITE_CHOICES = (
        ('caloocan', 'Caloocan'),
        ('taguig', 'Taguig'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    site = models.CharField(max_length=10, choices=SITE_CHOICES, default='caloocan')

    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, unique=True)

    email = models.EmailField(unique=True)