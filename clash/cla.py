from clash_api import clash
from stats import statistics_clash
import os
import warnings

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
    cla_tag=cla_data.get('tag').replace("#","%23")

    #search a cla members
    cla_members_URL = f'{url_base}/clans/{cla_tag}/members'

    #search statistics
    limit_river_race=5
    statistics_river_race_URL = f'{url_base}/clans/{cla_tag}/riverracelog?limit={limit_river_race}'

    statistics_river_race_result = clash_api.statistics_river_race(statistics_river_race_URL, token,cla_tag,cla_members_URL)

    statistics = statistics_river_race_result[['cla_ranking', 'seasonId','sectionIndex','createdDate', 'tag', 'name', 'role', 'fame']]
    statistics['rank_river_race'] = statistics['createdDate'].rank(method='dense', ascending=False)
    min_points = 2000

    #---------------------------#
    #--> Check promote and downgrade
    #---------------------------#
    bad_participants = clas_statistics.return_bad_participants(statistics,min_points)

    promote_participants = clas_statistics.return_promote_participants(statistics,bad_participants)

    bad_participants, promote_participants

    print('fineshed pipeline')

main()