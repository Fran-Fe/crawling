from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import json
import re
import os
import boto3
import stat


def chromeWebdriver():
    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")
    service = Service(executable_path="/opt/chromedriver")
    driver = webdriver.Chrome(service=service,
                              options=options)

    return driver


def start_search(driver, query):
    print("start search")
    url = "https://www.google.com/maps?hl=en"
    driver.get(url)
    time.sleep(5)
    search = driver.find_element(By.ID, "searchboxinput")
    search.clear()
    search.send_keys(query.get("search"))
    search.send_keys(Keys.ENTER)
    time.sleep(5)
    print("End start search")


def find_list(driver):
    print("find_list")
    max = 0
    while True:
        time.sleep(5)
        last_cafe = driver.find_elements(By.CSS_SELECTOR, '.UaQhfb')
        print(len(last_cafe))
        try:
            driver.execute_script(
                'arguments[0].scrollIntoView(true);', last_cafe[len(last_cafe)-1])
        except:
            return
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
    print("save_data")
    csv_filename = f"/tmp/{filename}.csv"
    for item in data:
        df = pd.DataFrame(
            item, columns=['name', 'rating', 'address', 'description', 'openclose'])
        df.to_csv(csv_filename, mode='a', index=False, encoding='utf-8-sig')
        os.chmod(csv_filename, stat.S_IWRITE)
    remove_duplicate(csv_filename)


def remove_duplicate(file):
    os.chmod(file, 0o777)
    df = pd.read_csv(file, header=0)
    df = df.drop_duplicates(subset=["name", "address"])
    df = df.sort_values(by='name', ascending=True)
    df.to_csv("/tmp/cafe_list.csv", index=False, encoding='utf-8-sig')
    os.chmod('/tmp/cafe_list.csv', 0o777)
    s3 = s3_connection()
    try:
        s3.upload_file(
            '/tmp/cafe_list.csv', "franfe-cafe-reviews", 'cafe_list.csv')
    except Exception as e:
        print(e)


def s3_connection():
    import key
    try:
        # s3 클라이언트 생성
        s3 = boto3.client(
            service_name="s3",
            region_name="us-west-1",
            aws_access_key_id=key.access_id,
            aws_secret_access_key=key.secret_key,
        )
        print("s3 bucket connected!")
        return s3

    except Exception as e:
        print(e)


def main():
    driver = chromeWebdriver()
    search_list = [{"search": "San Francisco, cafe"},
                   {"search": "San Francisco, coffee shop"},
                   {"search": "San Francisco, coffee"}]

    result = []
    for i in range(len(search_list)):
        start_search(driver, search_list[i])
        # 카페 리스트 찾기
        time.sleep(10)
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
