from functions.clash_api import clash
from functions.stats import statistics_clash
import os
import warnings
import sys

#-----> to run locally
from dotenv import load_dotenv
load_dotenv()

'''Warning ignoring'''
warnings.filterwarnings("ignore")


def main():
    #---------------------------#
    #--> get env variables
    #---------------------------#
    key = os.environ['key']
    cla_name = os.environ['cla_name']
    #---------------------------#
    #--> clash variables
    #---------------------------#
    url_base = 'https://api.clashroyale.com/v1'
    token = 'Bearer {}'.format(key) 
    #---------------------------#
    #--> APIs URLs
    #---------------------------#
    url = f'{url_base}/clans?name={cla_name}'

    clash_api = clash()
    clas_statistics = statistics_clash()

    #search a cla tag
    cla_data = clash_api.make_request(url, token, cla_name)
    try: 
        cla_tag=cla_data.get('tag').replace("#","%23")
    except:
        sys.exit(f"Error: {cla_data.get('reason')}") 

    #search a cla members
    cla_members_URL = f'{url_base}/clans/{cla_tag}/members'

    #search statistics
    limit_river_race=5
    statistics_river_race_URL = f'{url_base}/clans/{cla_tag}/riverracelog?limit={limit_river_race}'

    statistics_river_race_result = clash_api.statistics_river_race(statistics_river_race_URL, token,cla_tag,cla_members_URL)

    statistics = statistics_river_race_result[['cla_ranking', 'seasonId','sectionIndex','createdDate', 'tag', 'name', 'role', 'fame','decksUsed']]
    statistics['rank_river_race'] = statistics['createdDate'].rank(method='dense', ascending=False)
    min_points = 2000
    decks_day = 4 
    war_days = 4
    min_decks = decks_day * war_days
    #---------------------------#
    #--> Check promote and downgrade
    #---------------------------#
    bad_participants = clas_statistics.return_bad_participants(statistics,min_points,min_decks)

    promote_participants = clas_statistics.return_promote_participants(statistics,bad_participants)

    print('Bad participants to downgrade or delete.')
    if len(bad_participants) > 0:
        print(bad_participants.sort_values(by='fame', ascending=False))
    else:
        print('Does not have downgrades or deletes')
    print('-'*50)

    print('Good participants to promote.')
    if len(promote_participants) > 0:
        print(promote_participants)
    else:
        print('Does not have promotes')

    print('fineshed pipeline')

main()