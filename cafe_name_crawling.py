from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import json
import re


def chromeWebdriver():
    options = webdriver.ChromeOptions()
    # options.binary_location = '/opt/chrome/chrome'
    options.add_experimental_option('detach', True)
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    service = Service(
        executable_path="/home/jerry/Desktop/crawling/photo/chromedriver")
    chrome = webdriver.Chrome(service=service,
                              options=options)
    return chrome


def start_search(driver, query):
    print("start_search")
    url = "https://www.google.com/maps?hl=en"
    driver.get(url)
    driver.implicitly_wait(3)
    time.sleep(1)
    search = driver.find_element(By.ID, "searchboxinput")
    search.clear()
    search.send_keys(query.get("search"))
    search.send_keys(Keys.ENTER)
    print("end")


def find_list(driver):
    print("find_list")
    max = 0
    while True:
        time.sleep(1)
        last_cafe = driver.find_elements(By.CSS_SELECTOR, '.UaQhfb')
        driver.execute_script(
            'arguments[0].scrollIntoView(true);', last_cafe[len(last_cafe)-1])
        if max == len(last_cafe):
            print("Error : INF loading.")
            return last_cafe
        try:
            # 중단점 찾기
            stop = driver.find_element(By.CSS_SELECTOR, '.HlvSq')
            if stop:
                print("found stop position.")
                return last_cafe
        except:
            max = len(last_cafe)
            continue


def save_data(filename, data):
    csv_filename = f"{filename}.csv"
    for item in data:
        df = pd.DataFrame(
            item, columns=['name', 'rating', 'address', 'description', 'openclose'])
        df.to_csv(csv_filename, mode='a', index=False, encoding='utf-8-sig')


def remove_duplicate(file):
    df = pd.read_csv(file)
    df = df.drop_duplicates(['name', 'address'])
    df = df.sort_values(by='name', ascending=True)
    df.to_csv("cafe_list.csv", index=False, encoding='utf-8-sig')


def main():
    driver = chromeWebdriver()
    search_list = [{"search": "San Francisco, cafe"},
                   {"search": "San Francisco, coffee shop"},
                   {"search": "San Francisco, coffee"}]

    result = []
    for i in range(len(search_list)):
        start_search(driver, search_list[i])
        # 카페 리스트 찾기
        cafe_list = find_list(driver)
        print("end")
        cafes = []
        for i in range(len(cafe_list)):
            cafes.append(cafe_list[i].text.split("\n"))

            # 백슬래시, 콜론 제거
            pattern = r'[\\/:]'
            cafes[i][0] = re.sub(pattern, ' ', cafes[i][0])

            # 주소만 추출
            index = cafes[i][2].find("·")
            cafes[i][2] = cafes[i][2][index+2:]

        result.append(cafes)
    driver.quit()
    save_data("raw_cafe_list", result)
    remove_duplicate("raw_cafe_list.csv")


def handler(event=None, context=None):
    # TODO implement
    start = time.time()
    main()
    end = time.time()
    print(f'{end-start} 초 걸림')

    return {
        "statusCode": 200,
        "body": json.dumps("test")
    }


if __name__ == "__main__":
    handler()
