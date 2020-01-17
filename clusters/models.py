from django.db import models
from django.contrib.auth.models import User

class Circle(models.Model):
    name = models.CharField(max_length=500)

    def __repr__(self):
        return f"{self.name} Circle"

    def __str__(self):
        return f"{self.name} Circle"

class Topic(models.Model):
    name = models.CharField(max_length=500)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} Topic"

    class Meta:
        unique_together = (("name","circle"),)


