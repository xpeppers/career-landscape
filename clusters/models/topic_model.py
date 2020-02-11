from django.db import models
from clusters.models.circle_model import Circle


class Topic(models.Model):
    name = models.CharField(max_length=500)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} Topic"

    class Meta:
        unique_together = (("name", "circle"),)
