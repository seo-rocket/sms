from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(unique=True)

    def __str__(self):
        return self.name

class SMS(models.Model):
    phone_number = models.CharField(max_length=20)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    message = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)
    region = models.CharField(max_length=20)

    def __str__(self):
        return f"SMS from {self.service} to {self.phone_number}"

class Account(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    email_password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.username
