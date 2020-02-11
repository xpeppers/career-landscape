from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from clusters.models.dimension_model import Dimension


class Score(models.Model):
    class KindOfScore(models.IntegerChoices):
        CAREER_LANDSCAPE = 0
        MOMENTUM = 1
        NEXT_STEP = 2

    person = models.ForeignKey(User, on_delete=models.CASCADE)
    dimension = models.ForeignKey(Dimension, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now, blank=True)
    kind = models.IntegerField(
        choices=KindOfScore.choices, default=KindOfScore.CAREER_LANDSCAPE
    )

    def __str__(self):
        return f"[ {self.kind} Score ] {self.person} has assigned {self.value} in {self.dimension}"
