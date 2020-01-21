from django.shortcuts import render
from django.views import generic

from .models import Circle, Topic, Dimension, Score

class IndexView(generic.TemplateView):
    template_name = 'clusters/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_first_cirle_context(context)
        return context

    def add_first_cirle_context(self, context):

        for circle in Circle.objects.all():
            context['circle_name'] = circle.name
            topics = Topic.objects.filter(circle=circle).distinct()
            context['topics_details'] = { topic.name : self.count_people_in_topic(topic) for topic in topics}
            return context

        return context

    def count_people_in_topic(self, topic):
        dimensions_of_topic = Dimension.objects.filter(topic=topic)
        return Score.objects \
            .filter(dimension__in=dimensions_of_topic) \
            .filter(value__gt=0) \
            .distinct('person') \
            .count()
