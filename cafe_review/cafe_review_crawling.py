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
    time.sleep(2)
    search = driver.find_element(By.CSS_SELECTOR, "#searchboxinput")
    search.clear()
    search.send_keys(cafe_info.get("search"))
    search.send_keys(Keys.ENTER)
    try:
        time.sleep(1)
        cafe_name = driver.find_elements(
            By.CSS_SELECTOR, '.hfpxzc',)
        cafe_name[0].click()
    except:
        return get_store_review_data(driver, cafe_info)
    return get_store_review_data(driver, cafe_info)


def click_review(driver):
    print("click_review")
    time.sleep(3)

    aria = driver.find_element(
        By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[1]/h1'
    )
    print(aria.text)
    try:
        button = driver.find_element(
            By.XPATH, f'//*[@aria-label="Reviews for {aria.text}"]')
        button.click()
    except:
        return 0


def click_more(driver):
    button = driver.find_element(
        By.XPATH, f'//*[@aria-label="See more"]')
    button.click()


def get_store_review_data(driver, cafe_info):
    flag = click_review(driver)
    if flag == 0:
        return 0
    time.sleep(2)
    MAX = 0
    review_count_dir = driver.find_element(
        By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]')
    review_count = review_count_dir.text
    index = review_count.find("r")
    endpoint = review_count[:index-1]
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
            # 끝나는 지점
            if endpoint == len(scroll):
                print("End")
                break
            MAX = len(scroll)

        except Exception as e:
            print(e)
            break
    print("스크롤 끝")
    while True:
        try:
            click_more(driver)
        except:
            break
    print("클릭 끝")
    # 스크롤 끝났으니 수집
    reviews = driver.find_elements(By.CSS_SELECTOR, '.MyEned')
    result = [[cafe_info.get("cafe_name"), cafe_info.get("cafe_address"), review.text.replace(
        "\n", " ")] for review in reviews]

    return result


def make_query():
    df = pd.read_csv(
        "./cafe_list.csv", encoding='utf-8-sig', sep=',')
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
        })

    return search_name


def main():
    DIR_PATH = "./review"
    driver = chromeWebdriver()
    search_name = make_query()

    for i in range(len(search_name)):
        print(f"{i} 번째 시작")

        pattern = r'[\\/:]'
        cafe_name = re.sub(pattern, " ", search_name[i].get("cafe_name"))
        cafe_addr = search_name[i].get("cafe_address")

        if not os.path.exists(f'{DIR_PATH}/{cafe_name}_{cafe_addr}_reviews.csv'):
            print("검색 시작")
            result = start_search(
                driver, search_name[i])
            if result != 0:
                print("파일 저장")
                data = pd.DataFrame(result)
                data.to_csv(f'{DIR_PATH}/{cafe_name}_{cafe_addr}_reviews.csv',
                            index=False, sep=',', mode="w", encoding="utf-8-sig")
        print(f"{i} 번째 끝")


if __name__ == "__main__":
    main()
