import pandas as pd
import key
from urllib import parse
import urllib.request
import json
import connect_db


def main():
    df = pd.read_csv(
        "/home/jerry/Desktop/crawling/data/cafe_list.csv", encoding='utf-8-sig', sep=',')
    cafe_addr = df['address']
    cafe_len = len(cafe_addr)

    connection = connect_db.connect_to_mysql()

    for i in range(cafe_len):
        address = f"{cafe_addr[i]}, San Francisco"
        address = parse.quote(address.replace(" ", "+"))
        url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={key.GOOGLE_API_KEY}'

        res = urllib.request.urlopen(url)
        res_code = res.getcode()
        if res_code == 200:
            res_body = res.read()
            res_dict = json.loads(res_body.decode('utf-8'))
            res_status = res_dict["status"]
            if res_status != "ZERO_RESULTS":
                location = res_dict["results"][0]["geometry"]["location"]

                if connection:
                    connect_db.update_cafes_loc(
                        connection=connection, location=location, address=cafe_addr[i])
            else:
                print(address)
        else:
            print("Error : ", res_code)
    connect_db.disconnect_from_mysql(connection=connection)


if __name__ == "__main__":
    main()
