from django.views import generic
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from clusters.models import Circle, Topic, Dimension, Score


@method_decorator(staff_member_required, name="dispatch")
class UserView(generic.TemplateView):
    template_name = "clusters/users.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs["user_id"]
        selected_circle = self.request.GET.get("selected_user_circle", -1)
        if selected_circle != -1:
            context["user_topics_values"] = self.add_circle_context(
                user_id, selected_circle
            )
            context["circle_name"] = Circle.objects.get(id=selected_circle).name
            context["selected_circle_id"] = Circle.objects.get(id=selected_circle).id
        context["first_name"] = User.objects.get(id=user_id).first_name
        context["last_name"] = User.objects.get(id=user_id).last_name
        context["circles"] = list(Circle.objects.values_list("id", "name"))
        context["user_id"] = user_id
        return context

    def add_circle_context(self, user_id, circle_id):
        topic_dictionary = {}
        person = User.objects.get(id=user_id)
        topics = Topic.objects.filter(circle=Circle.objects.get(id=circle_id))
        for topic in topics:
            dimensions = Dimension.objects.filter(topic=topic)
            dimensions_with_values = {}
            try:
                for dimension in dimensions:
                    dimensions_with_values[dimension.name] = [
                        Score.objects.get(
                            person=person, dimension=dimension, kind=kind
                        ).value
                        for kind in range(0, 3)
                    ]
            except ObjectDoesNotExist as _:
                return {}
            topic_dictionary[topic.name] = dimensions_with_values
        return topic_dictionary
