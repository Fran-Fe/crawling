import pandas as pd
from PIL import Image
import os
import io
import urllib.request

csv_file = "/home/jerry/Downloads/cafe_image_url.csv"

df = pd.read_csv(csv_file)
url = df['url']
uuid = df['cafe_uuid']

for i in range(len(uuid)):
    try:
        os.mkdir(f"/home/jerry/Downloads/images/{uuid[i]}")
    except Exception as e:
        print(e)

for i in range(len(url)):
    try:
        # 이미지 다운로드
        image_data = urllib.request.urlopen(url[i]).read()
        # Pillow를 사용하여 이미지 화질 조절
        image = Image.open(io.BytesIO(image_data))
        # 원하는 화질로 조절 (quality 값은 1에서 100 사이의 정수)
        image.save(os.path.join(
            f"/home/jerry/Downloads/images/{uuid[i]}", f"{uuid[i]}_review_image_{i}.jpg"), quality=90)
        print("이미지 다운로드 완료.")
    except Exception as e:
        print(f"이미지 다운로드 실패: {e}")
