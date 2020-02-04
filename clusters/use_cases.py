import pandas as pd

from datetime import datetime


class ExcelUploadUseCase():
    user_repository = None
    circle_repository = None
    score_repository = None
    topic_repository = None
    dimension_repository = None
    listener = None

    def __init__(self, user_repository, circle_repository, score_repository, topic_repository, dimension_repository, listener):
        self.user_repository = user_repository
        self.circle_repository = circle_repository
        self.score_repository = score_repository
        self.topic_repository = topic_repository
        self.dimension_repository = dimension_repository
        self.listener = listener

    def uploadFile(self, form, file):
        try:
            parsed_data = self.Parser().parse_xlsx(file, self.circle_repository.get_all_circles())
        except Exception as _:
            self.listener.badFileFormat()
            return
        if not parsed_data:
            self.listener.dataNotParsed()
            return
        self.save_new_scores(parsed_data)


    def save_new_scores(self, parsed_data):
        try:
            date = datetime.strptime(parsed_data['compilation_date'], "%d-%m-%Y")
        except ValueError as _:
            self.listener.dataError()
            return
        person = self.user_repository.get_user_by_first_name_and_last_name(parsed_data['user_name'], parsed_data['user_surname'])
        if person is None:
            self.listener.userError()
            return
        circles = parsed_data['circles']
        if not circles:
            self.listener.noCircleInDatabase()
            return
        for circle in circles:
            for circle_name, topic_name, dimension_name, value in circle:
                circle = self.circle_repository.get_circle_by_name(circle_name)
                if circle is None:
                    self.listener.onDimensionRetrievalError(f'Circle <{circle_name}>')
                    return
                topic = self.topic_repository.get_topic_by_name_and_circle(topic_name, circle)
                if topic is None:
                    self.listener.onDimensionRetrievalError(f'Topic <{topic_name}>')
                    return
                dimension = self.dimension_repository.get_dimension_by_name_and_topic(dimension_name, topic)
                if dimension is None:
                    self.listener.onDimensionRetrievalError(f'Dimension <{dimension_name}>')
                    return
                self.score_repository.save_score(
                    dimension=dimension,
                    person=person,
                    value=value,
                    date=date )
        self.listener.uploadSuccessful()

    class Parser():

        def parse_xlsx(self, file, circles):
            dataframe = pd.read_excel(file, header=None, index_col=False)
            try:
                n_tables = len(circles)
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
            return lines



