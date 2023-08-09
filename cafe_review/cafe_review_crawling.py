import os
import re
import time
from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd


def chromeWebdriver():
    options = webdriver.ChromeOptions()
    # options.binary_location = '/opt/chrome/chrome'
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
    service = Service(executable_path="/usr/src/chrome/chromedriver")
    driver = webdriver.Chrome(service=service,
                              options=options)

    return driver


def start_search(driver, cafe_info):
    url = "https://www.google.com/maps?hl=en"
    driver.get(url)
    driver.implicitly_wait(5)
    search = driver.find_element(By.CSS_SELECTOR, "#searchboxinput")
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
    time.sleep(2)
    MAX = 0
    review_count_dir = driver.find_element(
        By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]')

    text = review_count_dir.text
    index = text.find("reviews")
    endpoint = text[:index-1]
    endpoint = int(re.sub(r',', "", endpoint))
    # 스크롤
    while True:
        try:
            scroll = driver.find_elements(By.CSS_SELECTOR, '.jftiEf')
            driver.execute_script(
                'arguments[0].scrollIntoView(true)', scroll[len(scroll)-1])
            time.sleep(5)
            # 무한 로딩 처리
            if MAX == len(scroll):
                print("Error : INF Loading.")
                break
            MAX = len(scroll)
            # 끝나는 지점
            if endpoint == len(scroll):
                print("End")
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
    reviews = driver.find_elements(By.CSS_SELECTOR, '.MyEned')
    result = [[cafe_info.get("cafe_name"), review.text.replace(
        "\n", " ")] for review in reviews]
    pattern = r'[\\/:]'
    name = re.sub(pattern, " ", cafe_info.get("cafe_name"))
    addr = cafe_info.get("cafe_address")
    return result, name, addr


def make_query():
    df = pd.read_csv(
        "./cafe_list.csv", encoding='utf-8-sig', sep=',')
    cafe_id = df['id']
    cafe_name = df['name']
    cafe_addr = df['address']
    cafe_len = len(cafe_name)
    search_name = []

    for i in range(cafe_len):
        search = cafe_name[i] + " " + cafe_addr[i]
        search_name.append({
            "search": search,
            "cafe_name": cafe_name[i],
            "cafe_address": cafe_addr[i],
            "cafe_id": cafe_id[i],
        })

    return search_name


def main():
    driver = chromeWebdriver()
    search_name = make_query()
    DIR_PATH = "./review"
    for i in range(len(search_name)):
        print(f"{i} 번째 시작")
        result, result_cafe_name, result_cafe_addr = start_search(
            driver, search_name[i])
        print("파일 저장")
        data = pd.DataFrame(result)

        if not os.path.exists(f'{DIR_PATH}/{result_cafe_name}_{result_cafe_addr}_reviews.csv'):
            data.to_csv(f'{DIR_PATH}/{result_cafe_name}_{result_cafe_addr}_reviews.csv',
                        index=False, sep=',', mode="w", encoding="utf-8-sig")
        print(f"{i} 번째 끝")


if __name__ == "__main__":
    main()
