import pandas as pd
from filesystem import FileSystem
from keybert import KeyBERT
import os
DIR_PATH = r"C:\Users\wsx21\Desktop\crawling"

def find_file():
    dir_route = f'{DIR_PATH}\\results'
    fs = FileSystem()
    file_list = fs.get_file_list(dir_route)
    files = []
    for file in file_list:
        dir = f'{dir_route}\\{file}'
        files.append(dir)

    return files

def BERT():
    csv_files = find_file()
    for reviews in csv_files:
        print(reviews)

        index = reviews.find("reviews")
        filename = reviews[index+7:]
        if os.path.exists(f'{DIR_PATH}\\results\\{filename}'):
            continue
        df = pd.read_csv(reviews)
        bow = []
        kw_extractor = KeyBERT('distilbert-base-nli-mean-tokens')
        cafe_review = df["1"]
        for review in cafe_review:
            try:
                keywords = kw_extractor.extract_keywords(review)
            except Exception as e:
                print(e)
                continue
            bow.append(keywords)

        new_bow = []
        for i in range(len(bow)):
            for j in range(len(bow[i])):
                new_bow.append(bow[i][j])

        keyword = pd.DataFrame(new_bow, columns=['keyword', 'weight'])
        result_df = keyword.groupby('keyword').agg('sum').sort_values('weight', ascending=False)
        
        result_df.to_csv(f'{DIR_PATH}\\results\\{filename}')

def main():
    csv_files = find_file()
    keyword = []
    for result in csv_files:
        df = pd.read_csv(result)
        data = df['keyword'].tolist()
        for value in data:
            keyword.append(value)
    keyword = set(keyword)
    print(sorted(keyword), len(keyword))

if __name__ == "__main__":
    main()