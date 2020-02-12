from django.test import TestCase
from clusters.models import Circle, Score, Dimension
from clusters.tests.factories.circle import CircleFactory
from clusters.tests.factories.dimension import DimensionFactory
from clusters.tests.factories.topic import TopicFactory
from clusters.lib.use_cases import ExcelUploadUseCase
from django.contrib.auth.models import User
from clusters.repositories import (
    UserRepository,
    CircleRepository,
    ScoreRepository,
    TopicRepository,
    DimensionRepository,
    TransactionManager,
)


class MockListener:
    def uploadSuccessful(self):
        return

    def dataNotParsed(self):
        return

    def badFileFormat(self):
        return

    def noCircleInDatabase(self):
        return

    def userError(self):
        return

    def dataError(self):
        return

    def onDimensionRetrievalError(self, message):
        return


class UploadExcelUseCase(TestCase):
    def test_parse_xlsx_correct_import_datas_from_dataframe(self):
        circle = CircleFactory.create()

        result = ExcelUploadUseCase.Parser().parse_xlsx(
            "clusters/tests/test_models/excel_test_file/cl_example.xlsx",
            Circle.objects.all(),
        )
        expected_result = {
            "user_name": "user_name",
            "user_surname": "user_surname",
            "circles": [
                [
                    ("Circle", "topic1", "dimension1", 2),
                    ("Circle", "topic1", "dimension2", 1),
                    ("Circle", "topic1", "dimension3", 2),
                    ("Circle", "topic1", "dimension4", 1),
                    ("Circle", "topic2", "dimension1", 4),
                    ("Circle", "topic2", "dimension2", 4),
                    ("Circle", "topic2", "dimension3", 4),
                    ("Circle", "topic2", "dimension4", 4),
                ]
            ],
        }

        self.assertEqual(result[0]["user_name"], expected_result["user_name"])
        self.assertEqual(result[0]["user_surname"], expected_result["user_surname"])
        self.assertListEqual(result[0]["circles"], expected_result["circles"])

    def test_retrieve_object_ignoring_case(self):
        user = User(
            username="user", first_name="mario", last_name="rossi", password="blablabla"
        )
        user.save()
        circle = CircleFactory.create(name="circle")
        topics = [
            TopicFactory.create(name=f"Topic{i}", circle=circle) for i in range(1, 3)
        ]
        dimensions1 = [
            DimensionFactory.create(name=f"diMension{i}", topic=topics[0])
            for i in range(1, 5)
        ]
        dimensions2 = [
            DimensionFactory.create(name=f"dimenSion{i}", topic=topics[1])
            for i in range(1, 5)
        ]

        with open(
            "clusters/tests/test_models/excel_test_file/cl_example_2.xlsx", "rb"
        ) as xlsx_file:
            ExcelUploadUseCase(
                UserRepository(),
                CircleRepository(),
                ScoreRepository(),
                TopicRepository(),
                DimensionRepository(),
                TransactionManager(),
                MockListener(),
            ).uploadFile(xlsx_file)

        scores = Score.objects.all()

        self.assertTrue(len(scores) > 0)
