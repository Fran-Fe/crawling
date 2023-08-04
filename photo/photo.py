from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from PIL import Image
import time
import pandas as pd
import re
import boto3
import urllib.request
import io
import os


def chromeWebdriver():
    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/google/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    service = Service(executable_path="/home/jerry/Desktop/photo/chromedriver")
    chrome = webdriver.Chrome(service=service,
                              options=options)
    return chrome


def save_image(driver):
    max = 0
    photo_list = []
    while True:
        time.sleep(1)
        photo_list = driver.find_elements(By.CSS_SELECTOR, '.G0fO6c')
        driver.execute_script(
            'arguments[0].scrollIntoView(true);', photo_list[len(photo_list)-1])
        if max == len(photo_list):
            print("loading Finished.")
            break
        max = len(photo_list)
    images = driver.find_elements(By.XPATH, '//*[@alt="Photo"]')
    results = []
    for i in images:
        try:
            image = i.get_attribute("data-src")
            if "http" in image:
                results.append(image)
                continue
        except:
            image = i.get_attribute("src")
            if "http" in image:
                results.append(image)
            continue
    return results


def start_search(driver, query):
    url = "https://www.google.com/?hl=en"
    driver.get(url)
    driver.implicitly_wait(5)
    search = driver.find_element(By.XPATH, f'//*[@type="search"]')
    search.clear()
    search.send_keys(query)
    search.send_keys(Keys.ENTER)
    driver.implicitly_wait(5)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '.KJY1Gc').click()


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
    print("main")
    driver = chromeWebdriver()
    # 리뷰 파일 리스트 돌면서 이름 가져오고
    df = pd.read_csv("/home/jerry/Desktop/photo/cafe_list.csv")
    cafe_name = df['name']
    cafe_address = df['address']
    postfix = "san francisco"

    # 검색문 만들기
    search_list = []
    for i in range(len(cafe_name)):
        query = f'{cafe_name[i]} {cafe_address[i]} {postfix}'
        search_list.append(query)

    s3 = s3_connection()
    # 이미지 서치
    for i in range(178, len(search_list)):
        # 카페 이름 검색하고 이미지 클릭
        print(search_list[i])
        start_search(driver=driver, query=search_list[i])
        # 실제 이미지 수집
        photo_list = save_image(driver=driver)
        os.mkdir(f'/home/jerry/Desktop/tmp/{search_list[i]}')
        index = 0
        for link in photo_list:
            try:
                # 이미지 다운로드
                image_data = urllib.request.urlopen(link).read()
                # Pillow를 사용하여 이미지 화질 조절
                image = Image.open(io.BytesIO(image_data))
                # 원하는 화질로 조절 (quality 값은 1에서 100 사이의 정수)
                image_name = f"{search_list[i]}_review_image_{index}.jpg"
                index += 1
                image.save(os.path.join(
                    f'/home/jerry/Desktop/tmp/{search_list[i]}', image_name), quality=90)
                try:
                    s3.upload_file(
                        f'/home/jerry/Desktop/tmp/{search_list[i]}/{image_name}', "franfe-cafe-images", f'{search_list[i]}/{image_name}')
                    os.remove(
                        f'/home/jerry/Desktop/tmp/{search_list[i]}/{image_name}')
                except Exception as e:
                    print(e)
            except Exception as e:
                print(f"이미지 다운로드 실패: {e}")

    # 이미지 저장
    # for j in range(len(photo_list)):
    #
    #
    # print("iter j END")


if __name__ == "__main__":
    main()
