from main import get_dict_id
from main import extract_name_country
from main import get_dict_image
from main import process_past_json
from main import process_standing_json
from main import process_upcoming_json
from main import update_current_round
from main import get_week

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

# GET WEEK
week = get_week()

# UPDATE CURRENT ROUND
update_current_round(week)

# CLEAN AND UPLOAD
process_standing_json(dict_spt, dict_utrm, dict_trm, dict_category, dict_team)
# process_past_json( dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team)
# process_upcoming_json(dict_spt, dict_utrm, dict_trm, dict_category, week, dict_team)