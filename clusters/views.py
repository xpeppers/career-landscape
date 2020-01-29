from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.contrib.auth.models import User
import pandas as pd
from datetime import datetime
from django.utils import timezone

from .forms import UploadFileForm
from .models import Circle, Topic, Dimension, Score


class IndexView(generic.FormView):
    template_name = "clusters/index.html"
    form_class = UploadFileForm
    success_url = '/'

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

def uploadFile(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filehandle = request.FILES['file']
            xlsx = filehandle.file
            myfile = pd.read_excel(xlsx, header=None, index_col=False)
            parsed_data = parse_xlsx(myfile)
            add_xlsx_datas(parsed_data)
        else:
            print('Error in form is valid')
    else:
        print('no post method find')
    return HttpResponseRedirect(reverse('clusters:index'))

def add_xlsx_datas(parsed_data):
    user_name = parsed_data['user_name']
    user_surname = parsed_data['user_surname']
    date = parsed_data['compilation_data']
    timed_data = datetime.strptime(date, "%d-%m-%Y")

    person = User.objects.get(first_name=user_name, last_name=user_surname)
    circles = parsed_data['circles']

    for circle in circles:
        for circle_name, topic_name, dimension_name, value in circle:
            circle = Circle.objects.get(name=circle_name)
            topic = Topic.objects.get(circle= circle, name=topic_name)
            dimension = Dimension.objects.get(topic=topic, name=dimension_name)
            score = Score(dimension=dimension, person=person, value=value, date=timed_data)
            score.save()


def parse_xlsx(dataframe):
    n_tables = len(Circle.objects.all())
    user_name = dataframe.iloc[1,1]
    user_surname = dataframe.iloc[1,2]
    compilation_data = dataframe.iloc[1,3]
    dataframe = dataframe[3:]
    circles = []
    lines_of_table = 7
    table_index = 0
    for _ in range(n_tables):
        sub_dataframe = dataframe[table_index:table_index + lines_of_table]
        circles.append( parse_circle(sub_dataframe) )
        table_index = table_index + lines_of_table
    return {'user_name': user_name, 'user_surname': user_surname, 'compilation_data' : compilation_data, 'circles': circles }


def parse_circle(dataframe):
    lines = []
    circle_name = dataframe.iat[0,0]
    for topic_index in dataframe.columns[1:]:
        topic = dataframe.iat[1, topic_index]
        if pd.isnull(topic):
            return lines
        for dimension_index in range(2, 6):
            dimension = dataframe.iat[dimension_index, 0]
            value = dataframe.iat[dimension_index, topic_index]
            lines.append((circle_name, topic, dimension, value))
    return lines
