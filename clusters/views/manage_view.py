from django.views import generic
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from django.contrib.auth.models import User
from clusters.forms import UploadFileForm
from clusters.models import Circle, Topic, Dimension, Score
from clusters.lib.use_cases import ExcelUploadUseCase
from clusters.repositories import (
    UserRepository,
    CircleRepository,
    ScoreRepository,
    TopicRepository,
    DimensionRepository,
)


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
            self.upload_form_valid()
        else:
            self.upload_form_invalid()
        return HttpResponseRedirect("/manage")

    def append_user_form_context(self, context):
        users = {
            user.id: (user.first_name, user.last_name)
            for user in User.objects.filter(is_staff=False)
        }
        context["users"] = users
        return context

    def upload_form_valid(self):
        ExcelUploadUseCase(
            UserRepository(),
            CircleRepository(),
            ScoreRepository(),
            TopicRepository(),
            DimensionRepository(),
            self,
        ).uploadFile(self.request.FILES["file"].file)

    def upload_form_invalid(self):
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
            "Error in xlsx file datas: Data not correct ( correct data format: dd/mm/yyyy ) ",
        )

    def onDimensionRetrievalError(self, message):
        messages.error(
            self.request, f"Consistency Error: {message} in xlsx file does not exists!"
        )
