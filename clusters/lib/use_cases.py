import pandas as pd

from datetime import datetime
from dateutil.parser import parse


class ExcelUploadUseCase:
    user_repository = None
    circle_repository = None
    score_repository = None
    topic_repository = None
    dimension_repository = None
    transaction_manager = None
    listener = None

    def __init__(
        self,
        user_repository,
        circle_repository,
        score_repository,
        topic_repository,
        dimension_repository,
        transaction_manager,
        listener,
    ):
        self.user_repository = user_repository
        self.circle_repository = circle_repository
        self.score_repository = score_repository
        self.topic_repository = topic_repository
        self.dimension_repository = dimension_repository
        self.transaction_manager = transaction_manager
        self.listener = listener

    def uploadFile(self, file):
        try:
            parsed_sheets = self.Parser().parse_xlsx(
                file, self.circle_repository.get_all_circles()
            )
        except Exception as e:
            self.listener.badFileFormat()
            return
        if not parsed_sheets:
            self.listener.dataNotParsed()
            return
        try:
            self.transaction_manager.apply_transaction(parsed_sheets, self)
        except Exception as e:
            return
        else:
            self.listener.uploadSuccessful()

    def save_new_scores(self, parsed_data):
        try:
            datetime.strptime(str(parsed_data["compilation_date"]), "%Y-%m-%d 00:00:00")
            date = parsed_data["compilation_date"]
        except ValueError as _:
            self.listener.dataError()
            raise Exception
        person = self.user_repository.get_user_by_first_name_and_last_name(
            parsed_data["user_name"], parsed_data["user_surname"]
        )
        if person is None:
            self.listener.userError()
            raise Exception
        circles = parsed_data["circles"]
        if not circles:
            self.listener.noCircleInDatabase()
            raise Exception
        for circle in circles:
            for circle_name, topic_name, dimension_name, value in circle:
                circle = self.circle_repository.get_circle_by_name(circle_name)
                if circle is None:
                    self.listener.onDimensionRetrievalError(f"Circle <{circle_name}>")
                    raise Exception
                topic = self.topic_repository.get_topic_by_name_and_circle(
                    topic_name, circle
                )
                if topic is None:
                    self.listener.onDimensionRetrievalError(f"Topic <{topic_name}>")
                    raise Exception
                dimension = self.dimension_repository.get_dimension_by_name_and_topic(
                    dimension_name, topic
                )
                if dimension is None:
                    self.listener.onDimensionRetrievalError(
                        f"Dimension <{dimension_name}>"
                    )
                    raise Exception
                self.score_repository.save_score(
                    dimension=dimension,
                    person=person,
                    value=value,
                    date=date,
                    kind=parsed_data["kind"],
                )

    class Parser:
        def parse_xlsx(self, file, circles, sheets_numbers=[0, 2, 3]):
            parsed_sheets = []
            xlsx_dataframe = pd.read_excel(
                file, header=None, index_col=False, sheet_name=sheets_numbers
            )
            for i in range(0, len(sheets_numbers)):
                dataframe = xlsx_dataframe[sheets_numbers[i]]
                try:
                    tables_dataframe = dataframe[3:]
                    parsed_circles = []
                    lines_of_table = 7
                    table_index = 0
                    for _ in range(len(circles)):
                        sub_dataframe = tables_dataframe[
                            table_index : table_index + lines_of_table
                        ]
                        parsed_circles.append(self.parse_circle(sub_dataframe))
                        table_index = table_index + lines_of_table
                    parsed_sheets.append(
                        {
                            "user_name": dataframe.iloc[1, 1],
                            "user_surname": dataframe.iloc[1, 2],
                            "compilation_date": dataframe.iloc[1, 3],
                            "kind": i,
                            "circles": parsed_circles,
                        }
                    )
                except IndexError as _:
                    return []
            return parsed_sheets

        def parse_circle(self, dataframe):
            lines = []
            circle_name = dataframe.iat[0, 0]
            for topic_index in dataframe.columns[1:]:
                topic = dataframe.iat[1, topic_index]
                if pd.isnull(topic):
                    return lines
                for dimension_index in range(2, 6):
                    dimension = dataframe.iat[dimension_index, 0]
                    value = dataframe.iat[dimension_index, topic_index]
                    lines.append((circle_name, topic, dimension, value))
            return lines
