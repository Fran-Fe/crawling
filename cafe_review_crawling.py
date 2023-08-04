import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import keyboard


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


def start_search(driver, cafe_info):
    url = "https://www.google.com/maps?hl=en"
    driver.get(url)
    driver.implicitly_wait(5)
    search = driver.find_element(By.CSS_SELECTOR, "#searchboxinput")

    print(cafe_info.get("search"))
    search.clear()
    search.send_keys(cafe_info.get("search"))
    search.send_keys(Keys.ENTER)
    return get_store_review_data(driver, cafe_info)


def click_button(driver, string):
    driver.implicitly_wait(5)
    time.sleep(1)
    aria_label_value = f'{string}'
    button = driver.find_element(
        By.XPATH, f'//*[@aria-label="{aria_label_value}"]')
    button.click()


def get_store_review_data(driver, cafe_info):
    print("검색")
    cafe_name = cafe_info.get("cafe_name")
    cafe_name = f'Reviews for {cafe_name}'
    click_button(driver, cafe_name)
    driver.implicitly_wait(5)
    time.sleep(1)
    # 스크롤
    while True:
        try:
            scroll = driver.find_elements(By.CSS_SELECTOR, '.jftiEf')
            # scroll = driver.find_elements(By.CSS_SELECTOR, '.MyEned')
            print(f'scroll 길이 {len(scroll)}')
            driver.execute_script(
                'arguments[0].scrollIntoView(true)', scroll[len(scroll)-1])
            time.sleep(5)
            if keyboard.is_pressed("q"):
                break
            if len(scroll) == 1100:
                break
            if len(scroll) == int(cafe_info.get("review_count")):
                break
        except Exception as e:
            print(e)
            break

    while True:
        try:
            click_button(driver, 'See more')
        except:
            break

    # 스크롤 끝났으니 수집
    reviews = driver.find_elements(By.CSS_SELECTOR, '.wiI7pd')
    result = [[cafe_info.get("cafe_name"), review.text.replace(
        "\n", " ")] for review in reviews]
    return result, cafe_info.get("cafe_name").replace(":", ""), cafe_info.get("cafe_address")


def main():
    driver = chromeWebdriver()

    df = pd.read_csv(
        r'C:\Users\wsx21\Desktop\crwaling\data\cafe_list.csv', encoding='utf-8-sig', sep=',')
    cafe_id = df['id']
    cafe_rating = df['rating']
    cafe_name = df['name']
    cafe_addr = df['address']
    cafe_len = len(cafe_name)
    search_name = []

    for i in range(cafe_len):
        search = cafe_name[i] + " " + cafe_addr[i]
        result = re.search(r'\(([\d,]+)\)', cafe_rating[i])
        review_count = result.group(1).replace(',', '')
        search_name.append({
            "search": search,
            "cafe_name": cafe_name[i],
            "cafe_address": cafe_addr[i],
            "cafe_id": cafe_id[i],
            "review_count": review_count
        })

    for i in range(1):
        print("크롤링 시작")
        result, result_cafe_name, result_cafe_addr = start_search(
            driver, search_name[75])
        print("결과 : ", result)
        data = pd.DataFrame(result)
        # 누적
        if not os.path.exists(f'reviews/{result_cafe_name}_{result_cafe_addr}_reviews.csv'):
            data.to_csv(f'reviews/{result_cafe_name}_{result_cafe_addr}_reviews.csv',
                        index=False, sep=',', mode="w", encoding="utf-8-sig")


if __name__ == "__main__":
    main()
