from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from pymongo import MongoClient
from collections import Counter
import json
import os
import glob
import time
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

def get_week(lst_folder):
    dict_week = {}
    for folder in lst_folder:
        dict_name = f"{folder}"
        folder_data = {
            # 'current_week': None,
            'past_week': None,
            'upcoming_week': None
        }
        with open(f'{folder}/standing.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            data = data['standings'][0]
            round_num = []
            for item in data['rows']:
                round_num.append(item['matches'])

            counter = Counter(round_num)
            round = counter.most_common(1)[0][0]
            # folder_data['current_week'] = current_week + 1
            folder_data['past_week'] = round
            folder_data['upcoming_week'] = round + 1
            dict_week[dict_name] = folder_data
    return dict_week

def delete_json_files(folder_list):
    for folder in folder_list:
        # Find all json files, including those in subdirectories
        for filename in glob.iglob(f"{folder}/**/*.json", recursive=True):
            try:
                os.remove(filename)
                print(f"Deleted {filename}")
            except Exception as e:
                print(f"Failed to delete {filename}. Reason: {e}")

def extract_name_country(collection_name):
    collection = db[collection_name]

    dict_team_country = {}
    for document in collection.find():
        name = document.get("name", "")
        country = document.get("country", {})
        dict_team_country[name] = country

    return dict_team_country

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

def fetch_content_from_txt_file(txt_filename, lst_folder):
    file_name = txt_filename.split('.')[0]

    # Create a Chrome WebDriver instance
    browser = webdriver.Chrome(executable_path="./chromedriver")

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

                except Exception as e:
                    print(f"Đã xảy ra lỗi với URL {url}: {e}")

            else:
                print(f"Dòng không hợp lệ: {line.strip()}")
    browser.quit()

def process_standing_json(lst_folder, dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team):
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
                for item in data['rows']:
                    item['descriptions'] = ""
                    item['team']['country'] = dict_team_country[item['team']['name']]
                    item['team']['image'] = ""
                    item['power'] = 21 - item['position']
                    round_num.append(item['matches'])

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
                    print(f"Updated raking of {item['team']['name']}")
        else:
            print(f"File standing.json in the directory {folder} does not exist.")

def process_past_json(lst_folder, dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team):
    print("=========================================PAST=================================================")
    collection_events = db['events']
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
                for item in data:
                    if item['round'] == week[folder]['past_week']:
                        filter_criteria = {
                            'slug': item['slug'],
                            'round': item['round']
                        }

                        update_data = {
                            '$set': {
                                'status': item['status'],
                                'awayScore': item['awayScore'],
                                'homeScore': item['homeScore'],
                                'winnerCode': item['winnerCode'],
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
                                'status.code': 100,
                                'status.description': 'Kết thúc',
                                'events.$.status': item['status'],
                                'events.$.awayScore': item['awayScore'],
                                'events.$.homeScore': item['homeScore'],
                                'events.$.winnerCode': item['winnerCode'],
                                'events.$.updatedAtTimestamp': get_current_date_timestamp()
                            }
                        }

                        # Update the document in the MongoDB collections
                        collection_events.update_one(filter_criteria, update_data)
                        collection_rounds.update_one(filter_criteria_rounds, update_data_rounds)
                        print(f"Updated match {item['homeTeam']['name']} vs {item['awayTeam']['name']} last week")

        else:
            print(f"File past.json in the directory {folder} does not exist.")

def process_upcoming_json(lst_folder, dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team):
    print("=========================================UPCOMING=============================================")
    collection = db['eventsTest']
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
                    if item['round'] == week[folder]['upcoming_week']:
                        item['updatedAtTimestamp'] = get_current_date_timestamp()
                        collection.insert_one(item)
                        print(f"Pushed match {item['homeTeam']['name']} vs {item['awayTeam']['name']} this week")
        else:
            print(f"File upcoming.json in the directory {folder} does not exist.")

def check_player(week):
    print("=====================================CHECK_PLAYER=============================================")
    collection_events = db['events']
    collection_eventplayers = db['eventplayers']

    for folder in lst_folder:
        dict_result = {}

        for document in collection_events.find():
            if document['round'] == week[folder]['past_week']:
                dict_result[document["_id"]] = document["winnerCode"]

        for document in collection_eventplayers.find():
            total_reward = 0
            total_result = 0
            win = 0
            lose = 0
            updated_events = []

            for item in document["round"]["events"]:
                if item["_id"] in dict_result and item["playerChoice"] == dict_result[item["_id"]]:
                    item["result"] = {}
                    item["result"]["code"] = 1
                    item["result"]["description"] = "Trúng"
                    total_result += 1
                    win += 1
                    if item['strongerTeam'] == 1:
                        dict_reward = {1:item['odd']['strong'], 2:item['odd']['weak'], 3:item['odd']['draw']}
                        reward = item["reward"] = dict_reward[item['playerChoice']] * 1000
                        total_reward += reward
                    elif item['strongerTeam'] == 2:
                        dict_reward = {1: item['odd']['weak'], 2: item['odd']['strong'], 3: item['odd']['draw']}
                        reward = item["reward"] = dict_reward[item['playerChoice']] * 1000
                        total_reward += reward
                else:
                    item["result"] = {}
                    item["result"]["code"] = 0
                    item["result"]["description"] = "Trượt"
                    item["reward"] = 0
                    lose += 1
                updated_events.append(item)
            collection_eventplayers.update_one({"_id": document["_id"]}, {"$set": {"round.events": updated_events}})

            if total_result >= 7:
                document["totalResult"] = {}
                document["totalResult"]["code"] = 1
                document["totalResult"]["description"] = "Trúng"
            else:
                document["totalResult"] = {}
                document["totalResult"]["code"] = 0
                document["totalResult"]["description"] = "Trượt"

            document["totalResult"]["win"] = win
            document["totalResult"]["lose"] = lose
            document["totalReward"]= total_reward
            collection_eventplayers.update_one({"_id": document["_id"]},{"$set": {"totalResult": document["totalResult"], "totalReward": document["totalReward"]}})

# MONGODB INFORMAITON
MONGO_URI = "mongodb://10.254.59.57:27017/"
client = MongoClient(MONGO_URI)
db = client['pool_football']

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

# LIST TOUR INFOMATION
lst_folder = {
    "premier_league": "EN",
    "laliga":"ES",
    "serie_a":"IT",
    "bundesliga":"DE",
    "ligue_1":"FR"
}

if __name__ == "__main__":
    year_trm = '23/24'

    # DELETE ALL FILE JSON
    # delete_json_files(lst_folder)

    # CRAWL DATA
    # fetch_content_from_txt_file("standing.txt", lst_folder)
    # fetch_content_from_txt_file("past.txt", lst_folder)
    # fetch_content_from_txt_file("upcoming.txt", lst_folder)

    # GET WEEK
    week = get_week(lst_folder)
    # week = {'premier_league': {'past_week': 6, 'upcoming_week': 7}}

    # CLEAN AND UPLOAD
    process_standing_json(lst_folder, dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team)
    # process_past_json(lst_folder, dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team)
    # process_upcoming_json(lst_folder, dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team)

    # CHECK PLAYER
    # check_player(week)

