import os
import pandas as pd

class FileSystem:
    def get_file_list(self, dir_path):
        try:
            file_list = os.listdir(dir_path)
            return file_list
        except FileNotFoundError:
            print("Can not found Dir")
            return []
        except Exception as e:
            print(f"Error: {e}")
            return []
        
    def rename_file(self, old_filename, new_filename):
        try:
            os.rename(old_filename, new_filename)
            print(f"Change File name: {old_filename} to {new_filename}")
        except FileNotFoundError:
            print("Can not found file")
        except FileExistsError:
            print(f"{new_filename} is exist")
        except Exception as e:
            print(f"Error: {e}")

def main():
    dir_path = r"C:\Users\wsx21\Desktop\crawling\reviews"

    fs = FileSystem()
    file_list = fs.get_file_list(dir_path)

    df = pd.read_csv(r'C:\Users\wsx21\Desktop\crawling\data\cafe_list.csv', encoding='utf-8-sig', sep=',')

    cafe_name = df['name']
    cafe_addr = df['address']
    cafe_len = len(cafe_name)
    change_name = []

    for i in range(cafe_len):
            new_name = cafe_name[i] + "_" + cafe_addr[i] + ".csv"
            change_name.append(new_name)

    print(len(file_list), len(change_name))

    for i in range(len(file_list)):
        fs.rename_file(f'{dir_path}/{file_list[i]}', f'{dir_path}/{change_name[i]}')

    print(fs.get_file_list(dir_path))

if __name__ == "__main__":
    main()
