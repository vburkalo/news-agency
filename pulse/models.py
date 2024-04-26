from django.contrib.auth.models import AbstractUser
from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Redactor(AbstractUser):
    years_of_experience = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username} ({self.years_of_experience} years of experience)"


class Newspaper(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    published_date = models.DateField()
    topic = models.ManyToManyField(Topic)
    publishers = models.ManyToManyField(Redactor)

    def __str__(self):
        return self.title
