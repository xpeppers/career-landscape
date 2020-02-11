from django.db import models

class Circle(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.name} Circle"