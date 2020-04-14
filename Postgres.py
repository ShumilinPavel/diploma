import psycopg2


class Postgres:
    def __init__(self, database, user, password, host, port):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connect(self):
        self.connection = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    # data = [(name, score, date, likes, has_photo, text), ...]
    def write(self, data, table):
        cursor = self.connection.cursor()
        for name, score, date, likes, has_photo, text in data:
            if likes == '':
                likes = 0
            query = """INSERT INTO {0} (name, score, date, likes, has_photo, text) VALUES (left(%s, 35), %s, %s, %s, %s, %s)""".format(table)
            cursor.execute(query, (name, score, date, likes, has_photo, text))
        self.connection.commit()
