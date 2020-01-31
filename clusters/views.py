from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

import pandas as pd
from datetime import datetime

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

    def form_valid(self, form):
        self.uploadFile(self.request, form)
        return super(IndexView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'File in Upload Form is not Valid')
        return super(IndexView, self).form_invalid(form)

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

    def uploadFile(self, request, form):
        myfile = self.safe_read_excel(request.FILES['file'].file)
        if myfile is None:
            messages.error(request, 'File reading generate error: please check file format.')
            return
        parsed_data = self.parse_xlsx(myfile)
        if not parsed_data:
            messages.error(request, 'Xlsx File has incorrect format! Impossible to Proceed.')
            return
        success, message = self.add_xlsx_datas(parsed_data)
        if not success:
            messages.error(request, message)
            return
        messages.success(request, message)
        return


    def safe_read_excel(self, file):
        try:
            return pd.read_excel(file, header=None, index_col=False)
        except Exception:
            return None

    def add_xlsx_datas(self, parsed_data):
        user_and_data, error_message =  self.get_user_and_date(parsed_data)
        if not user_and_data:
            return (False, f'Error in xlsx file datas: {error_message}')

        timed_date = user_and_data['timed_date']
        person = user_and_data['person']
        circles = parsed_data['circles']
        if not circles:
            return (False, "No database Circle detected. Impossible to Proceed.")
        for circle in circles:
            for circle_name, topic_name, dimension_name, value in circle:
                dimension, error_message = self.get_score_context(circle_name, topic_name, dimension_name)
                if dimension is None:
                    return (False, f'Consistency Error: {error_message}')
                score = Score(dimension=dimension, person=person, value=value, date=timed_date)
                score.save()
        return (True, 'Upload Success!')

    def get_user_and_date(self, parsed_data):
        try:
            timed_data = datetime.strptime(parsed_data['compilation_date'], "%d-%m-%Y")
            user_name = parsed_data['user_name']
            user_surname = parsed_data['user_surname']
            person = User.objects.get(first_name=user_name, last_name=user_surname)
            return ({ 'timed_date': timed_data, 'person': person }, '')
        except ValueError as _:
            return ({}, 'Data not correct ( correct data format: dd-mm-yyyy ) ')
        except ObjectDoesNotExist as _:
            return ({}, f'User not registered! First add User {user_name} {user_surname} in database.')
        except MultipleObjectsReturned as _:
            return ({}, f'Multiple User with same First-Name and Last-Name ({user_name} {user_surname}): Consistency Error!')
        except Exception as _:
            return ({}, 'Unknown Error Occurred during User and Date evaluation.')

    def get_score_context(self, circle_name, topic_name, dimension_name):
        try:
            circle = Circle.objects.get(name=circle_name)
            topic = Topic.objects.get(circle= circle, name=topic_name)
            dimension = Dimension.objects.get(topic=topic, name=dimension_name)
            return (dimension, '')
        except Circle.DoesNotExist as _ :
            return (None, f'Circle <{circle_name}> in xlsx file does not exists!')
        except Topic.DoesNotExist as _ :
            return (None, f'Topic <{topic_name}> in xlsx file does not exists!')
        except Dimension.DoesNotExist as _ :
            return (None, f'Dimension <{dimension_name}> in xlsx file does not exists!')
        except Exception as _:
            return (None, 'Unknown Error Occurred during xlsx data acquisition.')


    def parse_xlsx(self, dataframe):
        try:
            n_tables = len(Circle.objects.all())
            tables_dataframe = dataframe[3:]
            circles = []
            lines_of_table = 7
            table_index = 0
            for _ in range(n_tables):
                sub_dataframe = tables_dataframe[table_index:table_index + lines_of_table]
                circles.append( self.parse_circle(sub_dataframe) )
                table_index = table_index + lines_of_table
            return {
                'user_name': dataframe.iloc[1,1],
                'user_surname': dataframe.iloc[1,2],
                'compilation_date' : dataframe.iloc[1,3],
                'circles': circles }
        except IndexError as ie:
            return {}

    def parse_circle(self, dataframe):
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
        return lines # questo viene usato se ci sono tabelle con numero di topic != tra loro!
