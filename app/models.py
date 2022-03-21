from django.db import models


class Users(models.Model):
    user_id = models.CharField(max_length = 50)
    email = models.CharField(max_length = 50)
    password = models.CharField(max_length = 50)

    def __str__(self):
        return self.user_id
