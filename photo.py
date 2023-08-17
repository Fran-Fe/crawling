from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import connect_db


def chromeWebdriver():
    options = webdriver.ChromeOptions()
    # options.binary_location = '/opt/google/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    service = Service(
        executable_path="/usr/src/chrome/chromedriver")
    chrome = webdriver.Chrome(service=service,
                              options=options)
    return chrome


def save_image(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, '.KJY1Gc').click()
    except:
        print("요소 없음")
        return 0
    # 리스트 최대값을 저장
    max = 0
    # 사진을 담을 리스트
    photo_list = []
    # 스크롤 내리기
    while True:
        # 요소를 못찾는 에러를 방지하기 위해 1초 딜레이
        time.sleep(1)
        photo_list = driver.find_elements(By.CSS_SELECTOR, '.G0fO6c')
        # 리스트 맨 끝으로 스크롤
        driver.execute_script(
            'arguments[0].scrollIntoView(true);', photo_list[len(photo_list)-1])
        # 최대값이랑 리스트랑 비교
        if max == len(photo_list):
            # 최대값이랑 같으면 로딩이 끝
            print("loading Finished.")
            break
        # 다르면 최대값을 갱신
        max = len(photo_list)

    # 이미지 리스트
    images = driver.find_elements(By.XPATH, '//*[@alt="Photo"]')
    # 결과 리스트
    results = []
    for i in images:
        try:
            # 사진데이터가 "data-src", "src"에 나눠서 담겨 있음
            # "data-src"부터 처리하고 "src" 처리
            image = i.get_attribute("data-src")
            if "http" in image:
                # 링크에 http가 없는 이상한 값도 있어서 제외처리
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


def main():
    print("main")
    driver = chromeWebdriver()
    # 리뷰 파일 리스트 돌면서 이름 가져오고
    df = pd.read_csv("/home/jerry/Desktop/crawling/data/cafe_list.csv")
    cafe_name = df['name']
    cafe_address = df['address']
    postfix = "san francisco"

    # 검색문 만들기
    search_list = []
    cafe_info = []
    for i in range(len(cafe_name)):
        query = f'{cafe_name[i]} {cafe_address[i]} {postfix}'
        search_list.append(query)
        cafe_info.append({
            "name": cafe_name[i],
            "addr": cafe_address[i]
        })

    # MySQL 연결
    connection = connect_db.connect_to_mysql()
    # 이미지 서치
    for i in range(len(search_list)):
        # 카페 이름 검색하고 이미지 클릭
        start_search(driver=driver, query=search_list[i])
        # 실제 이미지 수집
        photo_list = save_image(driver=driver)
        if not photo_list:
            print(f"Error : 요소 없음")
            continue
        for link in photo_list:
            connect_db.insert_cafe_photo_urls(
                connection=connection, link=link, info=cafe_info[i])
    connect_db.disconnect_from_mysql(connection=connection)


if __name__ == "__main__":
    main()
