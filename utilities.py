from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from collections import Counter
import json
import os
import glob
import time
import random
from bson.objectid import ObjectId

def convert_to_objectid(data):
    if not isinstance(data, dict):
        return data

    if list(data.keys()) == ["$oid"]:
        try:
            return ObjectId(data["$oid"])
        except:
            print(f"Invalid ObjectId: {data['$oid']}")
            return data

    for key, value in data.items():
        data[key] = convert_to_objectid(value)

    return data

def get_current_date_timestamp():
    current_date_timestamp = int(time.time())
    return current_date_timestamp

def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None

def get_week():
    dict_week = {}
    for folder in lst_folder:
        dict_name = f"{folder}-{year_trm}"
        folder_data = {
            # 'current_week': None,
            'past_week': None,
            'upcoming_week': None,
            'postpone_match': {}
        }
        file_path = f'{folder}/standing.json'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                data = data['standings'][0]
                round_num = []
                for item in data['rows']:
                    round_num.append(item['matches'])
        else:
            pass

            counter = Counter(round_num)
            round = counter.most_common(1)[0][0]
            # folder_data['current_week'] = current_week + 1
            folder_data['past_week'] = round
            folder_data['upcoming_week'] = round + 1
            dict_week[dict_name] = folder_data
    return dict_week

def delete_json_files():
    for folder in lst_folder:
        # Find all json files, including those in subdirectories
        for filename in glob.iglob(f"{folder}/**/*.json", recursive=True):
            try:
                os.remove(filename)
                print(f"Deleted {filename}")
            except Exception as e:
                print(f"Failed to delete {filename}. Reason: {e}")

def set_id_value(data_dict, key_path, id_map):
    keys = key_path.split('.')
    temp_data = data_dict

    # Navigate through the keys except the last one
    for index, key in enumerate(keys[:-1]):
        # If the current key is a list, loop through it and apply set_id_value recursively
        if isinstance(temp_data, list):
            for item in temp_data:
                set_id_value(item, '.'.join(keys[index:]), id_map)
            return
        # If the current key is missing, exit gracefully
        elif key not in temp_data:
            return
        # Otherwise, move to the next level of nesting
        temp_data = temp_data[key]

    last_key = keys[-1]

    # If the end structure is a list, loop through it
    if isinstance(temp_data, list):
        for item in temp_data:
            if isinstance(item, dict):
                if "name" in item:
                    oid_value = id_map.get(item["name"], None)
                    if oid_value is None:
                        print(f"Cannot find value for name '{item['name']}' in id_map.")
                    # item[last_key] = {'$oid': oid_value}
                    item[last_key] = oid_value
                else:
                    print(f"Item doesn't have a 'name' key: {item}")
    elif isinstance(temp_data, dict) and "name" in temp_data:
        oid_value = id_map.get(temp_data["name"], None)
        if oid_value is None:
            print(f"Cannot find value for name '{temp_data['name']}' in id_map.")
        # temp_data[last_key] = {'$oid': oid_value}
        temp_data[last_key] = oid_value
    elif isinstance(temp_data, dict) and "name" not in temp_data:
        print(f"Item doesn't have a 'name' key: {temp_data}")

def set_image_value(data_dict, key_path, id_map):
    keys = key_path.split('.')
    temp_data = data_dict

    # Navigate through the keys except the last one
    for index, key in enumerate(keys[:-1]):
        # If the current key is a list, loop through it and apply set_id_value recursively
        if isinstance(temp_data, list):
            for item in temp_data:
                set_image_value(item, '.'.join(keys[index:]), id_map)
            return
        # If the current key is missing, exit gracefully
        elif key not in temp_data:
            return
        # Otherwise, move to the next level of nesting
        temp_data = temp_data[key]

    last_key = keys[-1]

    # If the end structure is a list, loop through it
    if isinstance(temp_data, list):
        for item in temp_data:
            if isinstance(item, dict):
                if "name" in item:
                    oid_value = id_map.get(item["name"], None)
                    if oid_value is None:
                        print(f"Cannot find value for name '{item['name']}' in id_map.")
                    # item[last_key] = {'$oid': oid_value}
                    item[last_key] = oid_value
                else:
                    print(f"Item doesn't have a 'name' key: {item}")
    elif isinstance(temp_data, dict) and "name" in temp_data:
        oid_value = id_map.get(temp_data["name"], None)
        if oid_value is None:
            print(f"Cannot find value for name '{temp_data['name']}' in id_map.")
        # temp_data[last_key] = {'$oid': oid_value}
        temp_data[last_key] = oid_value
    elif isinstance(temp_data, dict) and "name" not in temp_data:
        print(f"Item doesn't have a 'name' key: {temp_data}")

def delete_nested_key(data, keys):
    if not keys:
        return

    if len(keys) == 1:
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and keys[0] in item:
                    del item[keys[0]]
        elif isinstance(data, dict) and keys[0] in data:
            del data[keys[0]]
    else:
        key = keys[0]
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and key in item:
                    delete_nested_key(item[key], keys[1:])
        elif isinstance(data, dict) and key in data:
            delete_nested_key(data[key], keys[1:])

def delete_keys(data, keys_to_delete):
    for key in keys_to_delete:
        keys = key.split('.')
        delete_nested_key(data, keys)
    return data

def extract_name_country(collection):
    collection = db[f'{collection}']

    dict_team_country = {}
    for document in collection.find():
        name = document.get("name", "")
        country = document.get("country", {})
        dict_team_country[name] = country

    return dict_team_country

def get_dict_id(collection):
    collection = db[f'{collection}']

    dict = {}
    for document in collection.find():
        dict[document["name"]] = document["_id"]

    return dict

def get_dict_image(collection):
    collection = db[f'{collection}']

    dict = {}
    for document in collection.find():
        dict[document["name"]] = document["image"]

    return dict

def fetch_content_from_txt_file(txt_filename):
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

def process_standing_json(dict_spt, dict_utrm, dict_trm, dict_category, dict_team):
    print("=========================================STANDING=============================================")
    collection = db['standingsTest']

    for folder in lst_folder:
        file_path = os.path.join('.', folder, "standing.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                data = data['standings'][0]

                # Update
                data['tournament']['name'] = data['tournament']['name'] + ' ' + year_trm
                data['tournament']['slug'] = data['tournament']['slug'] + '-' + year_trm
                data['tournament']['image'] = ""
                data['tournament']['uniqueTournament']['image'] = ""

                round_num = []
                num_power = len(data['rows'])

                for item in data['rows']:
                    item['descriptions'] = ""
                    item['team']['country'] = dict_team_country.get(item['team']['name'], "")
                    item['team']['image'] = ""
                    round_num.append(item['matches'])
                    item['power'] = (num_power + 1) - item['position']

                counter = Counter(round_num)
                most_common_value = counter.most_common(1)[0][0]
                for item in data['rows']:
                    item['round'] = most_common_value

                # ID
                set_id_value(data, 'tournament._id', dict_trm)
                set_id_value(data, 'tournament.uniqueTournament._id', dict_utrm)
                set_id_value(data, 'tournament.category._id', dict_category)
                set_id_value(data, 'tournament.uniqueTournament.category._id', dict_category)
                set_id_value(data, 'tournament.category.sport._id', dict_spt)
                set_id_value(data, 'tournament.uniqueTournament.category.sport._id', dict_spt)
                set_id_value(data, 'rows.team.sport._id', dict_spt)
                set_id_value(data, 'rows.team._id', dict_team)

                # Image
                set_image_value(data, 'tournament.image', dict_image_tournaments)
                set_image_value(data, 'tournament.uniqueTournament.image', dict_image_uniquetournaments)
                set_image_value(data, 'rows.team.image', dict_image_team)

                # Delete
                keys_to_delete = [
                    'tournament.priority', 'tournament.id', 'type', 'tournament.category.flag', 'name', 'id',
                    'rows.promotion', 'updatedAtTimestamp',
                    'tournament.category.alpha2', 'tieBreakingRule', 'tournament.uniqueTournament.primaryColorHex',
                    'tournament.uniqueTournament.secondaryColorHex', 'rows.liveMatchWinnerCodeColumn', 'rows.promotion',
                    'tournament.uniqueTournament.displayInverseHomeAwayTeams', 'tournament.uniqueTournament.id',
                    'tournament.uniqueTournament.category.id', 'tournament.uniqueTournament.category.flag',
                    'tournament.uniqueTournament.category.alpha2', 'tournament.uniqueTournament.category.sport.id',
                    'tournament.category.sport.id', 'tournament.category.id', 'descriptions', 'rows.team.type',
                    'rows.team.id', 'tournament.uniqueTournament.hasPerformanceGraphFeature',
                    'rows.team.teamColors', 'rows.team.national', 'rows.team.disabled', 'rows.team.gender',
                    'rows.team.sport.id', 'rows.id'
                ]
                data = delete_keys(data, keys_to_delete)
                # print(data)

                a = data['tournament']
                layout = {'tournament': a}
                for item in data['rows']:
                    new_layout = {**layout, **item}
                    new_layout['updatedAtTimestamp'] = get_current_date_timestamp()
                    collection.insert_one(new_layout)
                    print(f"Pushed raking of {item['team']['name']}")
        else:
            print(f"File standing.json in the directory {folder} does not exist.")

def process_past_json(dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team):
    print("=========================================PAST=================================================")
    collection_events = db['eventsTest']
    collection_rounds = db['rounds']
    for folder in lst_folder:
        file_path = os.path.join('.', folder, "past.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                data = data['events']

                # Update
                for item in data:
                    item['tournament']['name'] = item['tournament']['name'] + ' ' + year_trm
                    item['tournament']['slug'] = item['tournament']['slug'] + '-' + year_trm
                    item['round'] = item['roundInfo']['round']
                    item['tournament']['image'] = ""
                    item['tournament']['uniqueTournament']['image'] = ""
                    item['homeTeam']['image'] = ""
                    item['awayTeam']['image'] = ""
                    item['homeTeam']['country'] = dict_team_country[item['homeTeam']['name']]
                    item['awayTeam']['country'] = dict_team_country[item['awayTeam']['name']]
                    item['slug'] = item['homeTeam']['slug'] + '-' + item['awayTeam']['slug']

                # ID
                set_id_value(data, 'tournament._id', dict_trm)
                set_id_value(data, 'tournament.uniqueTournament._id', dict_utrm)
                set_id_value(data, 'tournament.category._id', dict_category)
                set_id_value(data, 'tournament.uniqueTournament.category._id', dict_category)
                set_id_value(data, 'tournament.category.sport._id', dict_spt)
                set_id_value(data, 'tournament.uniqueTournament.category.sport._id', dict_spt)
                set_id_value(data, 'homeTeam.sport._id', dict_spt)
                set_id_value(data, 'awayTeam.sport._id', dict_spt)
                set_id_value(data, 'homeTeam._id', dict_team)
                set_id_value(data, 'awayTeam._id', dict_team)

                # Image
                set_image_value(data, 'tournament.image', dict_image_tournaments)
                set_image_value(data, 'tournament.uniqueTournament.image', dict_image_uniquetournaments)
                set_image_value(data, 'homeTeam.image', dict_image_team)
                set_image_value(data, 'awayTeam.image', dict_image_team)

                # Delete
                keys_to_delete = [
                    'finalResultOnly', 'id', 'winProbability', 'crowdsourcingDataDisplayEnabled',
                    'detailId', 'hasEventPlayerHeatMap', 'hasEventPlayerStatistics', 'hasXg', 'hasGlobalHighlights',
                    'changes',
                    'homeRedCards', 'awayRedCards', 'roundInfo',
                    'customId',
                    'homeTeam.gender', 'homeTeam.disabled', 'homeTeam.national', 'homeTeam.type', 'homeTeam.id',
                    'homeTeam.subTeams', 'homeTeam.teamColors', 'homeTeam.sport.id',
                    'awayTeam.gender', 'awayTeam.disabled', 'awayTeam.national', 'awayTeam.type', 'awayTeam.id',
                    'awayTeam.subTeams', 'awayTeam.teamColors', 'awayTeam.sport.id', 'tournament.id',
                    'tournament.priority',
                    'tournament.uniqueTournament.primaryColorHex', 'tournament.uniqueTournament.secondaryColorHex',
                    'tournament.uniqueTournament.crowdsourcingEnabled',
                    'tournament.uniqueTournament.hasPerformanceGraphFeature',
                    'tournament.uniqueTournament.hasEventPlayerStatistics',
                    'tournament.uniqueTournament.displayInverseHomeAwayTeams',
                    'tournament.uniqueTournament.country', 'tournament.uniqueTournament.id', 'tournament.category.id',
                    'tournament.category.flag', 'tournament.category.alpha2',
                    'tournament.uniqueTournament.category.id', 'tournament.uniqueTournament.category.flag',
                    'tournament.uniqueTournament.category.alpha2', 'tournament.uniqueTournament.category.sport.id',
                    'tournament.category.sport.id'
                ]
                data = delete_keys(data, keys_to_delete)
                layout = {}
                has_match_postponed = False

                for item in data:
                    if item['status']['code'] == 60 and item['round'] == week[f'{folder}-{year_trm}']['past_week']: # 60 này của dữ liệu crawl #
                        has_match_postponed = True

                    if item['round'] == week[f'{folder}-{year_trm}']['past_week']:
                        filter_criteria = {
                            'slug': item['slug'],
                            'round': item['round']
                        }

                        update_data = {
                            '$set': {
                                'status': item['status'],
                                'awayScore': item['awayScore'],
                                'homeScore': item['homeScore'],
                                'winnerCode': item.get('winnerCode', None),
                                'updatedAtTimestamp': get_current_date_timestamp()
                            }
                        }

                        filter_criteria_rounds = {
                            'events.slug': item['slug'],
                            'events.round': item['round'],
                            'round': item['round']
                        }

                        update_data_rounds = {
                            '$set': {
                                'events.$.status': item['status'],
                                'events.$.awayScore': item['awayScore'],
                                'events.$.homeScore': item['homeScore'],
                                'events.$.winnerCode': item.get('winnerCode', None),
                                'events.$.updatedAtTimestamp': get_current_date_timestamp()
                            }
                        }
                        if has_match_postponed:
                            update_data_rounds['$set'].update({
                                'status.code': 60,
                                'status.description': 'Tạm hoãn',
                                'color': '#17A2B8'
                            })
                        else:
                            update_data_rounds['$set'].update({
                                'status.code': 100,
                                'status.description': 'Kết thúc',
                                'color': '#6610F2'
                            })

                        # Update the document in the MongoDB collections1
                        collection_events.update_one(filter_criteria, update_data)
                        collection_rounds.update_one(filter_criteria_rounds, update_data_rounds)
                        print(f"Updated match {item['homeTeam']['name']} vs {item['awayTeam']['name']} last week")

        else:
            print(f"File past.json in the directory {folder} does not exist.")

def process_upcoming_json(dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team):
    print("=========================================UPCOMING=============================================")
    collection = db['events']
    for folder in lst_folder:
        file_path = os.path.join('.', folder, "upcoming.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                data = data['events']

                # Update
                for item in data:
                    item['tournament']['name'] = item['tournament']['name'] + ' ' + year_trm
                    item['tournament']['slug'] = item['tournament']['slug'] + '-' + year_trm
                    item['round'] = item['roundInfo']['round']
                    item['tournament']['image'] = ""
                    item['tournament']['uniqueTournament']['image'] = ""
                    item['homeTeam']['image'] = ""
                    item['awayTeam']['image'] = ""
                    item['homeTeam']['country'] = dict_team_country[item['homeTeam']['name']]
                    item['awayTeam']['country'] = dict_team_country[item['awayTeam']['name']]
                    item['slug'] = item['homeTeam']['slug'] + '-' + item['awayTeam']['slug']

                # ID
                set_id_value(data, 'tournament._id', dict_trm)
                set_id_value(data, 'tournament.uniqueTournament._id', dict_utrm)
                set_id_value(data, 'tournament.category._id', dict_category)
                set_id_value(data, 'tournament.uniqueTournament.category._id', dict_category)
                set_id_value(data, 'tournament.category.sport._id', dict_spt)
                set_id_value(data, 'tournament.uniqueTournament.category.sport._id', dict_spt)
                set_id_value(data, 'homeTeam.sport._id', dict_spt)
                set_id_value(data, 'awayTeam.sport._id', dict_spt)
                set_id_value(data, 'homeTeam._id', dict_team)
                set_id_value(data, 'awayTeam._id', dict_team)

                # Image
                set_image_value(data, 'tournament.image', dict_image_tournaments)
                set_image_value(data, 'tournament.uniqueTournament.image', dict_image_uniquetournaments)
                set_image_value(data, 'homeTeam.image', dict_image_team)
                set_image_value(data, 'awayTeam.image', dict_image_team)

                # Delete
                keys_to_delete = [
                    'finalResultOnly', 'id', 'winProbability', 'crowdsourcingDataDisplayEnabled',
                    'detailId', 'hasEventPlayerHeatMap', 'hasEventPlayerStatistics', 'hasXg', 'hasGlobalHighlights',
                    'changes', 'time.currentPeriodStartTimestamp', 'time.injuryTime1', 'time.injuryTime2',
                    'awayScore.current', 'homeRedCards', 'awayRedCards', 'roundInfo',
                    'awayScore.display', 'awayScore.period1', 'awayScore.period2', 'awayScore.normaltime',
                    'homeScore.current',
                    'homeScore.display', 'homeScore.period1', 'homeScore.period2', 'homeScore.normaltime',
                    'customId',
                    'homeTeam.gender', 'homeTeam.disabled', 'homeTeam.national', 'homeTeam.type', 'homeTeam.id',
                    'homeTeam.subTeams', 'homeTeam.teamColors', 'homeTeam.sport.id',
                    'awayTeam.gender', 'awayTeam.disabled', 'awayTeam.national', 'awayTeam.type', 'awayTeam.id',
                    'awayTeam.subTeams', 'awayTeam.teamColors', 'awayTeam.sport.id', 'tournament.id',
                    'tournament.priority',
                    'tournament.uniqueTournament.primaryColorHex', 'tournament.uniqueTournament.secondaryColorHex',
                    'tournament.uniqueTournament.crowdsourcingEnabled',
                    'tournament.uniqueTournament.hasPerformanceGraphFeature',
                    'tournament.uniqueTournament.hasEventPlayerStatistics',
                    'tournament.uniqueTournament.displayInverseHomeAwayTeams',
                    'tournament.uniqueTournament.country', 'tournament.uniqueTournament.id', 'tournament.category.id',
                    'tournament.category.flag', 'tournament.category.alpha2',
                    'tournament.uniqueTournament.category.id', 'tournament.uniqueTournament.category.flag',
                    'tournament.uniqueTournament.category.alpha2', 'tournament.uniqueTournament.category.sport.id',
                    'tournament.category.sport.id'
                ]
                data = delete_keys(data, keys_to_delete)
                for item in data:
                    if item['round'] == week[f'{folder}-{year_trm}']['upcoming_week']:
                        item['updatedAtTimestamp'] = get_current_date_timestamp()
                        collection.insert_one(item)
                        print(f"Pushed match {item['homeTeam']['name']} vs {item['awayTeam']['name']} this week")
        else:
            print(f"File upcoming.json in the directory {folder} does not exist.")

def check_postpone_dict(week):
    print("=====================================POSTPONE_WEEK===========================================")
    collection_round = db['rounds']

    for document in collection_round.find({'status.code': 60}):
        for event in document['events']:
            if event['status']['code'] == 60: # 60 này của dữ liệu crawl #
                week[event['tournament']['uniqueTournament']['slug']]['postpone_match'][event['slug']] = event['round']
    return week

def check_player(week, week_match_postpone=None, match_postpone=None, is_postpone=False):
    print("=====================================CHECK_PLAYER=============================================")
    collection_eventplayers = db['eventplayers']
    collection_round = db['rounds']

    resultColor = {
        'win': '#28A745',
        'postpone': '#17A2B8',
        'lose': '#DC3545'
    }

    for folder in lst_folder:
        round_status = None

        if not is_postpone:
            round = week[f'{folder}-{year_trm}']['past_week']
            dict_result = {}
            print(f'{folder}-{year_trm}')
            for document in collection_round.find({'round': round, 'tournament.slug': f'{folder}-{year_trm}'}):
                round_status = document['status']
                for item in document['events']:
                    dict_result[item["slug"]] = item.get("winnerCode")
        else:
            round = week_match_postpone
            dict_result = match_postpone
            for document in collection_round.find({'round': round}):
                round_status = document['status']
        print(round)
        print(dict_result)

        for document in collection_eventplayers.find({"round.round": round, 'round.tournament.slug': f'{folder}-{year_trm}'}):
            total_reward = 0
            win = 0
            lose = 0
            postpone = 0
            updated_events = []

            for item in document["round"]["events"]:
                if item["slug"] in dict_result and item["playerChoice"] == dict_result[item["slug"]]:
                    item['winnerCode'] = dict_result[item["slug"]]
                    item["resultCode"] = resultColor['win']
                    item["result"] = {}
                    item["result"]["code"] = 1
                    item["result"]["description"] = "Trúng"
                    if item['strongerTeam'] == 1:
                        dict_reward = {1:item['odd']['strong'], 2:item['odd']['weak'], 3:item['odd']['draw']}
                        # reward = item["reward"] = dict_reward[item['playerChoice']] * 1000
                        item["reward"] = dict_reward[item['playerChoice']] * 1000
                    elif item['strongerTeam'] == 2:
                        dict_reward = {1: item['odd']['weak'], 2: item['odd']['strong'], 3: item['odd']['draw']}
                        # reward = item["reward"] = dict_reward[item['playerChoice']] * 1000
                        item["reward"] = dict_reward[item['playerChoice']] * 1000
                    item["status"]["code"] = 100
                    item["status"]["description"] = 'Ended'
                    item["status"]["type"] = 'finished'
                # elif item["slug"] in dict_result and item["playerChoice"] != dict_result[item["slug"]] and dict_result[item["slug"]] == None:
                elif item["slug"] in dict_result and dict_result[item["slug"]] is None:
                    item['winnerCode'] = dict_result[item["slug"]]
                    item["resultCode"] = resultColor['postpone']
                    item["result"] = {}
                    item["result"]["code"] = 2
                    item["result"]["description"] = "Tạm hoãn"
                    item["reward"] = 0
                    item["status"]["code"] = 60
                    item["status"]["description"] = "Postponed"
                    item["status"]["type"] = "postponed"
                # elif item["slug"] not in dict_result:
                #     lose = lose
                else:
                    item['winnerCode'] = dict_result[item["slug"]]
                    item["resultCode"] = resultColor['lose']
                    item["result"] = {}
                    item["result"]["code"] = 0
                    item["result"]["description"] = "Trượt"
                    item["reward"] = 0
                    item["status"]["code"] = 100
                    item["status"]["description"] = 'Ended'
                    item["status"]["type"] = 'finished'
                updated_events.append(item)
                total_reward += item['reward']

                if item["result"]["code"] == 0:
                    lose += 1
                elif item["result"]["code"] == 2:
                    postpone += 1
                elif  item["result"]["code"] == 1:
                    win += 1

            collection_eventplayers.update_one({"_id": document["_id"]}, {"$set": {"round.events": updated_events}})

            if postpone != 0:
                document["totalResult"] = {}
                document["totalResult"]["code"] = 2
                document["totalResult"]["description"] = "Tạm hoãn"
                document["totalReward"] = None
            else:
                if win >= 7:
                    document["totalResult"] = {}
                    document["totalResult"]["code"] = 1
                    document["totalResult"]["description"] = "Trúng"
                    document["totalReward"] = total_reward
                else:
                    document["totalResult"] = {}
                    document["totalResult"]["code"] = 0
                    document["totalResult"]["description"] = "Trượt"
                    document["totalReward"] = 0

            document["round"]["status"] = round_status
            document['rewardedAtTimestamp'] = get_current_date_timestamp()
            document["totalResult"]["win"] = win
            document["totalResult"]["lose"] = lose
            document["totalResult"]["postpone"] = postpone
            collection_eventplayers.update_one({"_id": document["_id"]}, {"$set": {"round": document["round"], "totalResult": document["totalResult"], "totalReward": document["totalReward"],"rewardedAtTimestamp": document['rewardedAtTimestamp']}})

def check_postpone_match(week, check_player, week_match_postpone, match_postpone):
    collection_events = db['events']
    collection_rounds = db['rounds']
    print("==================================CHECK_POSTPONE_MATCH========================================")
    for folder in lst_folder:
        file_path = os.path.join('.', folder, "past.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                data = data['events']

                # Update
                for item in data:
                    item['round'] = item['roundInfo']['round']

                # Delete
                keys_to_delete = [
                    'finalResultOnly', 'id', 'winProbability', 'crowdsourcingDataDisplayEnabled', 'startTimestamp', 'endTimestamp', 'time', 'awayScore', 'homeScore', 'awayTeam', 'homeTeam', 'status', 'tournament',
                    'detailId', 'hasEventPlayerHeatMap', 'hasEventPlayerStatistics', 'hasXg', 'hasGlobalHighlights',
                    'changes',
                    'homeRedCards', 'awayRedCards', 'roundInfo',
                    'customId',
                    'homeTeam.gender', 'homeTeam.disabled', 'homeTeam.national', 'homeTeam.type', 'homeTeam.id',
                    'homeTeam.subTeams', 'homeTeam.teamColors', 'homeTeam.sport.id',
                    'awayTeam.gender', 'awayTeam.disabled', 'awayTeam.national', 'awayTeam.type', 'awayTeam.id',
                    'awayTeam.subTeams', 'awayTeam.teamColors', 'awayTeam.sport.id', 'tournament.id',
                    'tournament.priority',
                    'tournament.uniqueTournament.primaryColorHex', 'tournament.uniqueTournament.secondaryColorHex',
                    'tournament.uniqueTournament.crowdsourcingEnabled',
                    'tournament.uniqueTournament.hasPerformanceGraphFeature',
                    'tournament.uniqueTournament.hasEventPlayerStatistics',
                    'tournament.uniqueTournament.displayInverseHomeAwayTeams',
                    'tournament.uniqueTournament.country', 'tournament.uniqueTournament.id', 'tournament.category.id',
                    'tournament.category.flag', 'tournament.category.alpha2',
                    'tournament.uniqueTournament.category.id', 'tournament.uniqueTournament.category.flag',
                    'tournament.uniqueTournament.category.alpha2', 'tournament.uniqueTournament.category.sport.id',
                    'tournament.category.sport.id'
                ]
                data = delete_keys(data, keys_to_delete)
                for i in week:
                    lst_postpone_match = {**week[i]['postpone_match']}
                match_postpone = {}
                for i in data:
                    if i['slug'] in lst_postpone_match and i['round'] == lst_postpone_match[i['slug']] and 'winnerCode' in i and i['winnerCode'] != None:   #bổ sung code của trận đấu cho chắc#
                        match_postpone[i['slug']] = i['winnerCode']
                        week_match_postpone = i['round']

                        filter_criteria = {
                            'slug': i['slug'],
                            'round': i['round']
                        }

                        update_data = {
                            '$set': {
                                'status': {
                                    'code': 100,
                                    'description': 'Ended',
                                    'type': 'finished'
                                },
                                'winnerCode': i['winnerCode'],
                                'updatedAtTimestamp': get_current_date_timestamp()
                            }
                        }

                        filter_criteria_rounds = {
                            'events.slug': i['slug'],
                            'events.round': i['round'],
                            'round': i['round']
                        }

                        update_data_rounds = {
                            '$set': {
                                'events.$.status': {
                                    'code': 100,
                                    'description': 'Ended',
                                    'type': 'finished'
                                },
                                'events.$.winnerCode': i['winnerCode'],
                                'events.$.updatedAtTimestamp': get_current_date_timestamp()
                            }
                        }

                        collection_events.update_one(filter_criteria, update_data)
                        collection_rounds.update_one(filter_criteria_rounds, update_data_rounds)

                        check_player(week, week_match_postpone, match_postpone, is_postpone=True)
                        update_status_round(week_match_postpone)
                    else:
                        continue

def update_status_round(week_match_postpone):
    collection_eventplayers = db['eventplayers']
    collection_rounds = db['rounds']

    for document in collection_rounds.find({'round': week_match_postpone}):
        num_match = 0
        num_winnercode = 0
        for item in document['events']:
            num_match += 1
            if item['winnerCode'] is not None:
                num_winnercode += 1

        if num_match == num_winnercode:
            collection_rounds.update_one({'_id': document['_id']}, {'$set': {'status.code': 100, 'status.description': "Kết thúc", 'status.color': '#6610F2'}})

    for document in collection_eventplayers.find({'round.round': week_match_postpone}):
        num_match = 0
        num_winnercode = 0
        for item in document['round']['events']:
            num_match += 1
            if item['winnerCode'] is not None:
                num_winnercode += 1

        if num_match == num_winnercode:
            collection_eventplayers.update_one({'_id': document['_id']}, {'$set': {'round.status.code': 100, 'round.status.description': "Kết thúc", 'round.status.color': '#6610F2'}})

def update_current_round(week):
    print("=====================================UPDATE_ROUND=============================================")
    collection = db['tournaments']
    # get_dict_id('tournaments')
    for item in collection.find():
        if item['slug'] in week:
            collection.update_one({"_id": item['_id']}, {'$set': {
                'currentRound': week[f"{item['slug']}"]['upcoming_week'],
            }})

with open('config.json') as config_file:
    config = json.load(config_file)
MONGO_URI = config["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client[config["db_name"]]
lst_folder = config["lst_folder"]
year_trm = config["year_trm"]

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

# if __name__ == "__main__":

    # DELETE ALL FILE JSON
    # delete_json_files()

    # CRAWL DATA
    # fetch_content_from_txt_file("standing.txt", lst_folder)
    # fetch_content_from_txt_file("past.txt", lst_folder)
    # fetch_content_from_txt_file("upcoming.txt", lst_folder)

    # GET WEEK
    # week = get_week()
    # week = {'premier-league-23/24': {'past_week': 20, 'upcoming_week': 10, 'postpone_match': {}}, 'laliga-23/24': {'past_week': 21, 'upcoming_week': 11, 'postpone_match': {}}, 'serie-a-23/24': {'past_week': 20, 'upcoming_week': 10, 'postpone_match': {}}, 'bundesliga-23/24': {'past_week': 19, 'upcoming_week': 9, 'postpone_match': {}}, 'ligue-1-23/24': {'past_week': 20, 'upcoming_week': 10, 'postpone_match': {}}}
    # print(week)

    # UPDATE CURRENT ROUND
    # update_current_round(week)

    # CLEAN AND UPLOAD
    # process_standing_json(lst_folder, dict_spt, dict_utrm, dict_trm, dict_category, dict_team)
    # process_past_json(lst_folder, dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team)
    # process_upcoming_json(lst_folder, dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team)

    # CHECK PLAYER
    # check_player(week, week_match_postpone = None, match_postpone = None, is_postpone=False)

    # CHECK POSTPONE
    # week = check_postpone_dict(week)
    # print(week)
    # check_postpone_match(lst_folder, week, check_player, week_match_postpone = None, match_postpone = None)




