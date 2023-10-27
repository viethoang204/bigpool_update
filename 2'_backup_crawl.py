from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
import json
import os
import glob
import time
import random

def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None

def delete_json_files(folder_list):
    for folder in folder_list:
        # Find all json files, including those in subdirectories
        for filename in glob.iglob(f"{folder}/**/*.json", recursive=True):
            try:
                os.remove(filename)
                print(f"Deleted {filename}")
            except Exception as e:
                print(f"Failed to delete {filename}. Reason: {e}")

def fetch_content_from_txt_file(txt_filename, lst_folder):
    file_name = txt_filename.split('.')[0]

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Trident/7.0; AS; rv:11.0) like Gecko',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'Mozilla/5.0 (iPad; CPU OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; Lumia 950) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.14900'
    ]

    def get_random_user_agent():
        return random.choice(user_agents)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'user-agent={get_random_user_agent()}')

    # Khởi tạo một đối tượng WebDriver với tùy chọn
    browser = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)

    with open(txt_filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if ': ' in line:
                key, url = line.strip().split(': ')
                print(f'downloading {key}-{file_name}')

                # Below is the logic from the fetch_content function
                value = find_key_by_value(lst_folder, key)
                if not value:
                    print(f"Invalid key: {key}")
                    continue

                try:
                    browser.get(url)
                    pre_content = browser.find_element(By.TAG_NAME, 'pre').text

                    # Save the content as JSON with filename prefix
                    output_filename = f"{value}/{file_name}.json"
                    with open(output_filename, 'w', encoding='utf-8') as f:
                        try:
                            json_content = json.loads(pre_content)
                            json.dump(json_content, f, ensure_ascii=False, indent=4)

                        except json.JSONDecodeError:
                            print(f"Nội dung từ URL {url} trong thẻ <pre> không phải là JSON hợp lệ.")
                    time.sleep(random.randint(90, 150))

                except Exception as e:
                    print(f"Đã xảy ra lỗi với URL {url}: {e}")

            else:
                print(f"Dòng không hợp lệ: {line.strip()}")
    browser.quit()

def extract_name_country(collection):
    with open(f'element/pool_football.{collection}.json', 'r') as file:
        data = json.load(file)
    dict_team_country = {}
    for document in data:
        name = document.get("name", "")
        country = document.get("country", {})
        dict_team_country[name] = country

    return dict_team_country

def get_dict_id(collection):
    with open(f'element/pool_football.{collection}.json', 'r') as file:
        data = json.load(file)
    dict = {}
    for document in data:
        dict[document["name"]] = document["_id"]

    return dict

def get_dict_image(collection):
    with open(f'element/pool_football.{collection}.json', 'r') as file:
        data = json.load(file)
    dict = {}
    for document in data:
        dict[document["name"]] = document["image"]

    return dict

# DICTIONARYS INFOMATION
dict_spt = get_dict_id('sports')
dict_utrm = get_dict_id('uniquetournaments')
dict_trm = get_dict_id('tournaments')
dict_category = get_dict_id('categories')
dict_country = get_dict_id('countries')
dict_team = get_dict_id('teams')
dict_team_country = extract_name_country('teams')
dict_image_team = get_dict_image("teams")
dict_image_tournaments = get_dict_image("tournaments")
dict_image_uniquetournaments = get_dict_image("uniquetournaments")

with open('config.json') as config_file:
    config = json.load(config_file)
lst_folder = config["lst_folder"]

# CRAWL DATA
fetch_content_from_txt_file("standing.txt", lst_folder)
fetch_content_from_txt_file("past.txt", lst_folder)
fetch_content_from_txt_file("upcoming.txt", lst_folder)


