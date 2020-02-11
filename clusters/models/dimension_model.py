from django.db import models
from clusters.models.topic_model import Topic


class Dimension(models.Model):
    name = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.topic} - Dimension of Knowledge: {self.name}"

    class Meta:
        unique_together = (("name", "topic"),)
