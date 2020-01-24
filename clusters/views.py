from django.shortcuts import render
from django.views import generic

from .models import Circle, Topic, Dimension, Score


class IndexView(generic.TemplateView):
    template_name = "clusters/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_cirles_context(context)

        return context

    def add_cirles_context(self, context):
        circle_dictionary = {}
        for circle in Circle.objects.all():
            topic_value_gt, topic_dimension_eq = self.set_value_and_dimension_filters(circle.id)
            topics = Topic.objects.filter(circle=circle).distinct()
            topic_details = {
                topic.name: self.count_people_in_topic(topic, topic_value_gt, topic_dimension_eq) for topic in topics
             }
            dimensions = list(Dimension.objects.filter(topic__in=topics) \
                                    .distinct("name") \
                                    .values('id','name')
                                )
            circle_dictionary[circle.name] = {
                'topics_details' : topic_details,
                'dimensions' : dimensions ,
                'circle_id' : circle.id,
                'topic_value_gt' : topic_value_gt,
                'topic_dimension_eq' : topic_dimension_eq
                }
        context['circles'] = circle_dictionary
        return context

    def set_value_and_dimension_filters(self, circle_id):
            topic_value_gt = self.request.GET.get(f'topic_value_gt_{circle_id}', 0)
            topic_dimension_eq_id= int(self.request.GET.get(f'topic_dimension_eq_{circle_id}', "-1"))
            if topic_dimension_eq_id != -1:
                return (topic_value_gt, Dimension.objects.get(id=topic_dimension_eq_id).name)
            return (topic_value_gt, "")

    def count_people_in_topic(self, topic, topic_value_gt=0, topic_dimension_eq=""):
        dimensions = Dimension.objects.filter(topic=topic)
        if topic_dimension_eq:
            dimensions = [dimensions.get(name=topic_dimension_eq)]
        return (
            Score.objects.filter(dimension__in=dimensions)
            .filter(value__gt=topic_value_gt)
            .distinct("person")
            .count()
        )
