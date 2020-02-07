from django.test import TestCase
from clusters.models import Circle
from clusters.tests.factories.circle import CircleFactory
from clusters.use_cases import ExcelUploadUseCase


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

        self.assertEqual(result["user_name"], expected_result["user_name"])
        self.assertEqual(result["user_surname"], expected_result["user_surname"])
        self.assertListEqual(result["circles"], expected_result["circles"])
