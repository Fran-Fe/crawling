import os
import re
import time
import pandas as pd
from keybert import KeyBERT
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from filesystem import FileSystem

DIR_PATH = r"C:\Users\wsx21\Desktop\crawling"


def find_file():
    dir_route = f'{DIR_PATH}\\reviews'
    fs = FileSystem()
    file_list = fs.get_file_list(dir_route)
    files = []
    for file in file_list:
        dir = f'{dir_route}\\{file}'
        files.append(dir)

    return files


def data_text_cleaning(data):
    # 영문자 이외 문자는 공백으로 변환
    only_english = re.sub('[^a-zA-Z]+', ' ', data)
    # 불용어 제거
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(only_english)
    no_stops = [word for word in words if word.lower() not in stop_words]
    # 어간 추출
    lemmatizer = WordNetLemmatizer()
    stemmer_words = [lemmatizer.lemmatize(word) for word in no_stops]
    # 공백으로 구분된 문자열로 결합하여 결과 반환
    return ' '.join(stemmer_words)


def BERT():
    csv_files = find_file()
    for reviews in csv_files:
        print(reviews)
        start_time = time.time()
        index = reviews.find("reviews")
        filename = reviews[index+7:]
        if os.path.exists(f'{DIR_PATH}\\test\\{filename}'):
            continue
        df = pd.read_csv(reviews)
        bow = []
        kw_extractor = KeyBERT('distilbert-base-nli-mean-tokens')
        cafe_review = df["1"]
        for review in cafe_review:
            try:
                review = data_text_cleaning(review)
                keywords = kw_extractor.extract_keywords(
                    review, keyphrase_ngram_range=(1, 2), stop_words=None)
            except Exception as e:
                print(e)
                continue
            bow.append(keywords)

        new_bow = []
        for i in range(len(bow)):
            for j in range(len(bow[i])):
                new_bow.append(bow[i][j])

        keyword = pd.DataFrame(new_bow, columns=['keyword', 'weight'])
        result_df = keyword.groupby('keyword').agg(
            'sum').sort_values('weight', ascending=False)

        result_df.to_csv(f'{DIR_PATH}\\test\\{filename}')
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"실행 시간: {execution_time:.6f} 초")


if __name__ == "__main__":
    nltk.download('wordnet')
    BERT()
