import mysql.connector
import pandas as pd
import os
import re
import key
from filesystem import FileSystem
# MySQL 서버에 연결하는 함수


def connect_to_mysql():
    try:
        # MySQL 서버에 연결
        connection = mysql.connector.connect(
            host=key.RDS_ENDPOINT,
            user=key.RDS_USER,
            password=key.RDS_PASSWORD,
            database="franfe"
        )

        if connection.is_connected():
            print("MySQL에 연결되었습니다.")
            return connection

    except Exception as e:
        print("MySQL 연결 에러:", e)
        return None

# 데이터를 조회하는 함수


def select_data(connection, table_name):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM {table_name}')

            # 결과 출력
            for row in cursor.fetchall():
                print(row)

            cursor.close()

    except Exception as e:
        print("데이터 조회 에러:", e)


def get_data(dir_path):
    fs = FileSystem()
    file_list = fs.get_file_list(dir_path)

    return file_list


def cafe_table_insert(connection):
    import uuid
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            file_path = r"C:\Users\wsx21\Desktop\crawling\data\cafe_list.csv"
            df = pd.read_csv(file_path)
            df_id = df['id']
            df_address = df['address']
            df_place_name = df['name']
            df_rating = df['rating']
            df_overview = df['description']
            for i in range(len(df_address)):
                uuid_ = uuid.uuid1()
                id = df_id[i]
                address = df_address[i]
                place_name = df_place_name[i]

                index = df_rating[i].find("(")
                rating = df_rating[i][:index]

                overview = df_overview[i]

                query = ("INSERT INTO cafes "
                         "(id, uuid, address, place_name, overview,rating) "
                         f'VALUES ({id}, "{uuid_.hex}","{address}","{place_name}","{overview}",{float(rating)})'
                         )

                cursor.execute(query)
                connection.commit()
    except Exception as e:
        print("데이터 조회 에러:", e)


def cafe_reviews_insert(connection):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            dir_path = r"C:\Users\wsx21\Desktop\crawling\reviews"
            file_list = get_data(dir_path)
            for file in file_list:
                # Open할 파일 이름
                filename = dir_path + f"\\{file}"

                # 주소, 이름 분리
                file, _ = os.path.splitext(file)
                place_name, address = file.split('_')

                df = pd.read_csv(filename)
                text = df['1']  # 집어 넣을 데이터
                for i in range(len(text)):
                    review = str(text[i])
                    pattern = r"['\":/\\]"
                    review = re.sub(pattern, "", review)
                    print(review)
                    query = (
                        "INSERT INTO cafe_reviews (cafe_uuid, text) "
                        f'(SELECT uuid, "{review}" FROM cafes '
                        f'WHERE address="{address}" AND '
                        f'place_name="{place_name}")'
                    )
                    cursor.execute(query)
                print(file)
                connection.commit()
    except Exception as e:
        print("데이터 조회 에러:", e)


def cafe_review_texts_insert(connection):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            dir_path = r"C:\Users\wsx21\Desktop\crawling\reviews"
            file_list = get_data(dir_path)
            CAFE_REVIEW_ID = 1
            for file in file_list:
                # Open할 파일 이름
                filename = dir_path + f"\\{file}"

                # 주소, 이름 분리
                file, _ = os.path.splitext(file)
                df = pd.read_csv(filename)
                text = df['1']  # 집어 넣을 데이터
                for i in range(len(text)):
                    review = str(text[i])
                    pattern = r"['\":/\\]"
                    review = re.sub(pattern, "", review)
                    print(review)
                    query = (
                        "INSERT INTO cafe_review_texts (cafe_review_id, text) "
                        f'VALUES ({CAFE_REVIEW_ID}, "{review}")'
                    )
                    CAFE_REVIEW_ID += 1
                    cursor.execute(query)
                print(file)
                connection.commit()
    except Exception as e:
        print("데이터 조회 에러:", e)

# MySQL 서버와의 연결 해제


def cafe_hashtags_insert(connection):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            dir_path = r"C:\Users\wsx21\Desktop\crawling\results"
            file_list = get_data(dir_path)
            for file in file_list:
                filename = dir_path + f"\\{file}"

                file, _ = os.path.splitext(file)
                place_name, address = file.split('_')

                df = pd.read_csv(filename)
                keyword = df['keyword']
                for i in range(len(keyword)):
                    query = (
                        "INSERT INTO cafe_hashtags (cafe_uuid, hashtag) "
                        f'(SELECT uuid, "{keyword[i]}" FROM cafes '
                        f'WHERE address="{address}" AND '
                        f'place_name="{place_name}")'
                    )
                    cursor.execute(query)
                print(file)
                connection.commit()
    except Exception as e:
        print("데이터 조회 에러:", e)


def update_cafes_loc(connection, location, address):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            query = ("SET sql_safe_updates=0;")
            cursor.execute(query)
            query = (
                "UPDATE cafes "
                f'SET lat = {location["lat"]}, lng = {location["lng"]}'
                f'WHERE address="{address}";'
            )
            cursor.execute(query)
            query = ("SET sql_safe_updates=1;")
            cursor.execute(query)
            connection.commit()

    except Exception as e:
        print("데이터 조회 에러:", e)


def insert_cafe_photo_urls(connection, link, info):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            query = (
                "INSERT INTO cafe_photo_urls (cafe_uuid, url) "
                f'SELECT uuid, "{link}" FROM cafes '
                f'WHERE place_name = "{info["name"]}" and address = "{info["addr"]}";'
            )
            cursor.execute(query)
            connection.commit()

    except Exception as e:
        print("데이터 조회 에러:", e)


def insert_cafe_options(connection, option, name, addr):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            query = (
                "INSERT INTO cafe_options (cafe_uuid, option_name) "
                f'SELECT uuid, "{option}" FROM cafes '
                f'WHERE place_name = "{name}" and '
                f'address = "{addr}";'
            )
            cursor.execute(query)
            connection.commit()
    except Exception as e:
        print("데이터 조회 에러:", e)


def select_cafe_options(connection, name, addr):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            query = (
                "SELECT * FROM cafe_options "
                "WHERE cafe_uuid = (SELECT uuid FROM cafes "
                f'WHERE place_name = "{name}"; '
                # f'and address = "{addr}");'
            )
            cursor.execute(query)
            for row in cursor.fetchall():
                print(row)

            connection.commit()
    except Exception as e:
        print("데이터 조회 에러:", e)


def disconnect_from_mysql(connection):
    try:
        if connection.is_connected():
            connection.close()
            print("MySQL 연결이 해제되었습니다.")
    except Exception as e:
        print("MySQL 연결 해제 에러:", e)


if __name__ == "__main__":
    # MySQL에 연결
    connection = connect_to_mysql()

    if connection:
        # 데이터 삽입
        # cafe_table_insert(connection)
        # 데이터 조회
        # cafe_hashtags_insert(connection=connection)
        # cafe_reviews_insert(connection)
        # MySQL 연결 해제
        disconnect_from_mysql(connection)
