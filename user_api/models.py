from django.db import models

class User(models.Model):
    username = models.CharField(max_length=25, unique=True)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models. EmailField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'