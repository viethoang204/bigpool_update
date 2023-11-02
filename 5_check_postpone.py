from utilities import check_player
from utilities import check_postpone_match
from utilities import check_postpone_dict
from utilities import get_week

# GET WEEK
week = get_week()

# CHECK POSTPONE
week = check_postpone_dict(week)
check_postpone_match(week, check_player, week_match_postpone = None, match_postpone = None)