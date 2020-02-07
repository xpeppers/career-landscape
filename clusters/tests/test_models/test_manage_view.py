from django.test import RequestFactory, TestCase, Client
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from clusters.tests.factories.factory_methods import *

from clusters.models import Circle, Topic, Dimension, Score
from clusters.views import ManageView
from clusters.tests.factories.circle import CircleFactory
from clusters.tests.factories.topic import TopicFactory
from clusters.tests.factories.dimension import DimensionFactory

class MockListener:
    def uploadSuccessful(self, message):
        return

    def dataNotParsed(self):
        return

    def badFileFormat(self):
        return

    def uploadUnsuccessful(self, message):
        return

class ManageViewTest(TestCase):

    def test_manage_upload_xlsx_file_and_load_data(self):
        client = get_logged_staff_client()
        create_example_excel_file_context()

        with open('clusters/tests/test_models/excel_test_file/cl_example.xlsx','rb') as xlsx_file:
            response = client.post('/manage/',{ 'file' : xlsx_file }, follow=True)

        scores = Score.objects.filter(kind=0)
        self.assertEqual(len(scores),8)

    def test_manage_view_shows_correct_upload_file_message_if_success(self):
        client = get_logged_staff_client()
        xlsx_file = create_example_excel_file_context()

        with open('clusters/tests/test_models/excel_test_file/cl_example.xlsx','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file }, follow=True)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Upload Success!')

    def test_manage_view_shows_correct_upload_file_message_if_fail_with_wrong_file_post(self):
        client = get_logged_staff_client()
        xlsx_file = 'false_file'
        response = client.post('/manage/', { 'file' : xlsx_file })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'File in Upload Form is not Valid')

    def test_manage_view_upload_file_with_not_registered_user_shows_error_message(self):
        client = get_logged_staff_client()

        with open('clusters/tests/test_models/excel_test_file/cl_example.xlsx','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Error in xlsx file datas: User error: User not Found or multiple user with same first name and last name')

    def test_manage_view_upload_file_with_no_circle_in_db_shows_error_message(self):
        client = get_logged_staff_client()
        user = UserFactory.build(username='username', first_name='user_name', last_name='user_surname', password='us_test_ps_w')
        user.save()

        with open('clusters/tests/test_models/excel_test_file/cl_example.xlsx','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'No database Circle detected. Impossible to Proceed.')

    def test_manage_view_upload_file_with_not_registered_data_shows_error_message(self):
        client = get_logged_staff_client()
        user = UserFactory.build(username='username', first_name='user_name', last_name='user_surname', password='us_test_ps_w')
        user.save()
        circle = CircleFactory.create(name='Circle')

        with open('clusters/tests/test_models/excel_test_file/cl_example.xlsx','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Consistency Error: Topic <topic1> in xlsx file does not exists!')

    def test_manage_view_upload_bad_format_file_shows_correct_message(self):
        client = get_logged_staff_client()

        with open('clusters/tests/test_models/excel_test_file/error_file.txt','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'File reading generate error: please check file format.')

    def test_manage_view_upload_bad_excel_file_shows_correct_message(self):
        client = get_logged_staff_client()

        with open('clusters/tests/test_models/excel_test_file/wrong_excel.xlsx','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Xlsx File has incorrect format! Impossible to Proceed.')

    def test_manage_view_upload_bad_date_file_shows_correct_message(self):
        client = get_logged_staff_client()

        with open('clusters/tests/test_models/excel_test_file/excel_with_bad_date.xlsx','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Error in xlsx file datas: Data not correct ( correct data format: dd-mm-yyyy ) ')

    def test_manage_view_upload_with_error_caused_by_homonymous_User(self):
        client = get_logged_staff_client()
        user = UserFactory.build(username='username', first_name='user_name', last_name='user_surname', password='us_test_ps_w')
        user.save()
        user_homonymous = UserFactory.build(username='username_homonymous', first_name='user_name', last_name='user_surname', password='us_test_ps_w')
        user_homonymous.save()

        with open('clusters/tests/test_models/excel_test_file/cl_example.xlsx','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Error in xlsx file datas: User error: User not Found or multiple user with same first name and last name')

    def test_manage_view_upload_with_bad_circle_in_excel(self):
        client = get_logged_staff_client()
        user = UserFactory.build(username='username', first_name='user_name', last_name='user_surname', password='us_test_ps_w')
        user.save()
        circle = CircleFactory.create(name='Circle_wrong')

        with open('clusters/tests/test_models/excel_test_file/cl_example.xlsx','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Consistency Error: Circle <Circle> in xlsx file does not exists!')

    def test_manage_view_upload_file_with_not_existing_dimension_shows_error_message(self):
        client = get_logged_staff_client()
        user = UserFactory.build(username='username', first_name='user_name', last_name='user_surname', password='us_test_ps_w')
        user.save()
        circle = CircleFactory.create(name='Circle')
        topic_one = TopicFactory.create(name='topic1', circle=circle)
        topic_two = TopicFactory.create(name='topic2', circle=circle)

        with open('clusters/tests/test_models/excel_test_file/cl_example.xlsx','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Consistency Error: Dimension <dimension1> in xlsx file does not exists!')

    def test_manage_view_upload_file_with_circles_with_different_topics_numbers(self):
        client = get_logged_staff_client()
        xlsx_file = create_example_excel_file_topics_numbers()

        with open('clusters/tests/test_models/excel_test_file/cl_example_topics_disparity.xlsx','rb') as xlsx_file:
            response = client.post('/manage/', { 'file' : xlsx_file }, follow=True)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Upload Success!')

    def test_manage_view_shows_users_form(self):
        client = get_logged_staff_client()
        users = [ UserFactory.build(username= f'username{i}', password = f'blabla{i}', first_name=f'username{i}' ) for i in range(3)]
        for user in users:
            user.save()

        response = client.get('/manage/')

        for i in range(3):
            self.assertContains(response, f'username{i}')

    def test_manage_view_redirect_to_userview_after_selecting_a_user(self):
        client = get_logged_staff_client()
        user = UserFactory.build(username='username', first_name='user_name', last_name='user_surname', password='us_test_ps_w')
        user.save()

        response = client.get('/manage/', { 'selected_user' : user.id }, follow=True )

        self.assertContains(response,user.first_name)
        self.assertContains(response,user.last_name)
        self.assertRedirects(response, f'/users/{user.id}', status_code=302 )