from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views import generic
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from datetime import datetime

from .forms import UploadFileForm
from .models import Circle, Topic, Dimension, Score
from .use_cases import ExcelUploadUseCase
from .repositories import (
    UserRepository,
    CircleRepository,
    ScoreRepository,
    TopicRepository,
    DimensionRepository,
)


class AboutView(generic.TemplateView):
    template_name = "clusters/about.html"


@method_decorator(staff_member_required, name="dispatch")
class ManageView(generic.TemplateView):
    template_name = "clusters/manage.html"
    form_classes = {
        "upload": UploadFileForm,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.form_classes)
        context = self.append_user_form_context(context)
        return context

    def get(self, request):
        user = self.request.GET.get("selected_user", -1)
        if user != -1:
            return HttpResponseRedirect(f"/users/{user}")
        return render(request, "clusters/manage.html", self.get_context_data())

    def post(self, request):
        upload_form = UploadFileForm(request.POST, request.FILES)
        if upload_form.is_valid():
            self.upload_form_valid(upload_form)
        else:
            self.upload_form_invalid(upload_form)
        return HttpResponseRedirect("/manage")

    def append_user_form_context(self, context):
        users = {
            user.id: (user.first_name, user.last_name) for user in User.objects.all()
        }
        context["users"] = users
        return context

    def upload_form_valid(self, form):
        ExcelUploadUseCase(
            UserRepository(),
            CircleRepository(),
            ScoreRepository(),
            TopicRepository(),
            DimensionRepository(),
            self,
        ).uploadFile(form, self.request.FILES["file"].file)

    def upload_form_invalid(self, form):
        messages.error(self.request, "File in Upload Form is not Valid")

    def uploadSuccessful(self):
        messages.success(self.request, "Upload Success!")

    def dataNotParsed(self):
        messages.error(
            self.request, "Xlsx File has incorrect format! Impossible to Proceed."
        )

    def badFileFormat(self):
        messages.error(
            self.request, "File reading generate error: please check file format."
        )

    def noCircleInDatabase(self):
        messages.error(
            self.request, "No database Circle detected. Impossible to Proceed."
        )

    def userError(self):
        messages.error(
            self.request,
            "Error in xlsx file datas: User error: User not Found or multiple user with same first name and last name",
        )

    def dataError(self):
        messages.error(
            self.request,
            "Error in xlsx file datas: Data not correct ( correct data format: dd-mm-yyyy ) ",
        )

    def onDimensionRetrievalError(self, message):
        messages.error(
            self.request, f"Consistency Error: {message} in xlsx file does not exists!"
        )


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
        if self.request.GET.get("momentum", False):
            context["selected_topic"] = self.request.GET.get("selected_topic")
            context["apply_momentum_to_radar"] = True
        if self.request.GET.get("next-step", False):
            context["selected_topic"] = self.request.GET.get("selected_topic")
            context["apply_next_step_to_radar"] = True
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


@method_decorator(login_required, name="dispatch")
class IndexView(generic.TemplateView):
    template_name = "clusters/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_circles_context(context)
        return context

    def add_circles_context(self, context):
        circle_dictionary = {}
        for circle in Circle.objects.all():
            topic_value_gt, topic_dimension_eq = self.set_value_and_dimension_filters(
                circle.id
            )
            topics = Topic.objects.filter(circle=circle).distinct()
            topic_details = {
                topic.name: self.count_people_in_topic(
                    topic, topic_value_gt, topic_dimension_eq
                )
                for topic in topics
            }
            dimensions = list(
                Dimension.objects.filter(topic__in=topics)
                .distinct("name")
                .values("id", "name")
            )
            circle_dictionary[circle.name] = {
                "topics_details": topic_details,
                "dimensions": dimensions,
                "circle_id": circle.id,
                "topic_value_gt": topic_value_gt,
                "topic_dimension_eq": topic_dimension_eq,
            }
        context["circles"] = circle_dictionary
        return context

    def set_value_and_dimension_filters(self, circle_id):
        topic_value_gt = self.request.GET.get(f"topic_value_gt_{circle_id}", 0)
        topic_dimension_eq_id = int(
            self.request.GET.get(f"topic_dimension_eq_{circle_id}", "-1")
        )
        if topic_dimension_eq_id != -1:
            return (
                topic_value_gt,
                Dimension.objects.get(id=topic_dimension_eq_id).name,
            )
        return (topic_value_gt, "")

    def count_people_in_topic(self, topic, topic_value_gt=0, topic_dimension_eq=""):
        dimensions = Dimension.objects.filter(topic=topic)
        if topic_dimension_eq:
            dimensions = [dimensions.get(name=topic_dimension_eq)]
        return (
            Score.objects.filter(dimension__in=dimensions)
            .filter(value__gt=topic_value_gt, kind=0)
            .distinct("person")
            .count()
        )
