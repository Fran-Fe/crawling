import os


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
