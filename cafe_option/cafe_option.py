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
    service = Service(
        executable_path="/usr/src/chrome/chromedriver")
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
    '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div/a'
    try:
        cafe_name = driver.find_elements(
            By.CSS_SELECTOR, '.hfpxzc',)
        cafe_name[0].click()
    except:
        return get_store_review_data(driver, cafe_info)
    return get_store_review_data(driver, cafe_info)


def click_button(driver):
    time.sleep(2)
    aria = driver.find_element(
        By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[1]/h1'
    )
    button = driver.find_element(
        By.XPATH, f'//*[@aria-label="About {aria.text}"]')
    button.click()


def get_store_review_data(driver, cafe_info):
    print("검색")
    click_button(driver)
    time.sleep(1)
    div = driver.find_elements(By.CSS_SELECTOR, '.iP2t7d')
    results = []
    for item in div:
        options = item.find_elements(By.CSS_SELECTOR, '.hpLkke')
        results.append([option.text for option in options])

    pattern = r'[\\/:]'
    name = re.sub(pattern, " ", cafe_info.get("cafe_name"))
    addr = cafe_info.get("cafe_address")
    return results, name, addr


def make_query():
    df = pd.read_csv(
        "./cafe_list.csv", encoding='utf-8-sig', sep=',')
    cafe_name = df['name']
    cafe_addr = df['address']
    cafe_len = len(cafe_name)
    search_name = []

    for i in range(cafe_len):
        search = f'{cafe_name[i]} {cafe_addr[i]} San Francisco CA'
        search_name.append({
            "search": search,
            "cafe_name": cafe_name[i],
            "cafe_address": cafe_addr[i],
        })

    return search_name


def main():
    import connect_db
    connection = connect_db.connect_to_mysql()
    driver = chromeWebdriver()
    search_name = make_query()
    for i in range(len(search_name)):
        print(f"{i} 번째 시작")
        print(search_name[i])
        result, result_cafe_name, result_cafe_addr = start_search(
            driver, search_name[i])
        print("데이터 저장")
        for option_list in result:
            for option in option_list:
                connect_db.insert_cafe_options(
                    connection, option, result_cafe_name, result_cafe_addr)

        print(f"{i} 번째 끝")


if __name__ == "__main__":
    main()
