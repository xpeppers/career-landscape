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
        context_with_new_variables = context
        circles = Circle.objects.all()

        if circles.count() > 0:
            circle = Circle.objects.first()
            context_with_new_variables['circle_name'] = list(circles.values_list('name', flat=True))[0]
            topics = self.get_topics_of_circle(circle)
            context_with_new_variables['topics_names'] = list(topics.values_list('name', flat=True))
            number_of_people_in_topics = [0] * topics.count()
            counter = 0
            for topic in topics:
                number_of_people_in_topics[counter] = self.count_people_in_topic(topic)
            context_with_new_variables['topics_numbers'] = number_of_people_in_topics

        return context_with_new_variables

    def count_people_in_topic(self, topic):
        scores_of_topic = self.get_scores_more_than_zero_of_topic(topic)
        return self.count_distinct_people_in_scores(scores_of_topic)

    def count_distinct_people_in_scores(self, scores):
        if scores.count() < 1:
            return 0
        score_one_per_person = scores.distinct('person')
        return score_one_per_person.count()

    def get_scores_more_than_zero_of_topic(self, topic):
        dimensions_of_topic = self.get_dimensions_of_topic(topic)
        score_of_topic = Score.objects.filter(dimension__in=dimensions_of_topic)
        return score_of_topic.filter(value__gt=0)

    def get_dimensions_of_topic(self, topic):
        return Dimension.objects.filter(topic=topic)

    def get_topics_of_circle(self, circle):
        return Topic.objects.filter(circle=circle).distinct()

        # # Implementazione parziale per il solo circle 'delivery' !!
        # # ma basta ciclare su name per ottenerli tutti
        # delivery_circle = Circle.objects.get(name='Delivery')
        # topics_of_delivery_circle = Topic.objects.filter(circle=delivery_circle).distinct()
        # orders_of_delivery = Order.objects.filter(topic__in=topics_of_delivery_circle)
        # levels_of_delivery = Level.objects.filter(order__in=orders_of_delivery)

        # number_of_people_in_topics = [0] * topics_of_delivery_circle.count()
        # counter = 0

        # for topic in topics_of_delivery_circle:
        #     orders_of_this_topic = orders_of_delivery.filter(topic=topic)
        #     levels_of_this_topic = levels_of_delivery.filter(order__in=orders_of_this_topic)
        #     levels_more_than_zero = levels_of_this_topic.filter(value__gt=0)
        #     if levels_more_than_zero.count() > 0:
        #         levels_one_per_person = levels_more_than_zero.distinct('person')
        #         number_of_people = levels_one_per_person.count()
        #         number_of_people_in_topics[counter] = number_of_people
        #         counter += 1

        # topics_names = [ element for element in topics_of_delivery_circle.values_list('name', flat=True)]
        # topics_numbers = list(number_of_people_in_topics)

        # context['topics_names'] = topics_names
        # context['topics_values'] = topics_numbers
        # return context