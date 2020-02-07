from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytz


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
        unique_together = (("name", "circle"),)


class Dimension(models.Model):
    name = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.topic} - Dimension of Knowledge: {self.name}"

    class Meta:
        unique_together = (("name", "topic"),)


class Score(models.Model):

    class KindOfScore(models.IntegerChoices):
        CAREER_LANDSCAPE = 0
        MOMENTUM = 1
        NEXT_STEP = 2

    person = models.ForeignKey(User, on_delete=models.CASCADE)
    dimension = models.ForeignKey(Dimension, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now, blank=True)
    kind = models.IntegerField(choices=KindOfScore.choices, default=KindOfScore.CAREER_LANDSCAPE)

    def __repr__(self):
        return f"[ {self.kind} Score ] {self.person} has assigned {self.value} in {self.dimension}"

    def __str__(self):
        return f"[ {self.kind} Score ] {self.person} has assigned {self.value} in {self.dimension}"
