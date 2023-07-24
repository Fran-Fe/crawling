from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def chromeWebdriver():
    options = Options()
    options.add_argument("lang=ko_KR")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_experimental_option('detach', True)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def main():
    driver = chromeWebdriver()
    url = 'https://www.google.co.kr/maps/search/san+francisco,+cafe/@37.7209573,-122.4855949,12z/data=!4m2!2m1!6e5?hl=en&entry=ttu'
    driver.get(url)
    
    cafe_list = []
    while True:
        last_cafe = driver.find_elements(By.CSS_SELECTOR, '.UaQhfb')
        driver.execute_script('arguments[0].scrollIntoView(true);', last_cafe[len(last_cafe)-1])
        time.sleep(5)
        print(len(last_cafe))
        if len(last_cafe) == 122:
            cafe_list = last_cafe
            break
        
    cafes = []
    for i in range(len(cafe_list)):
        cafes.append(cafe_list[i].text.split("\n"))
    
    csv_filename = f"cafe_cafes.csv"
    df = pd.DataFrame(cafes, columns=['name', 'rating', 'address', 'description', 'openclose'])
    print(cafes)
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    
if __name__ == "__main__":
    main()