import requests
import pandas as pd
import warnings

'''Warning ignoring'''
warnings.filterwarnings("ignore")

class clash():

    def make_request(self,url, token, cla_tag=None):
        cla_search = requests.get(url,headers={'Authorization':token})
        cla_search = cla_search.json()

        try:
            if cla_tag != None:
                for cla in cla_search.get('items'):
                    if cla.get('tag') == cla_tag:
                        cla_search = cla
        except:
            print(cla_search.get('message'))

        return cla_search

    def cla_members(self,cla_members_url,token):
        cla_members_data = self.make_request(cla_members_url, token)
        return pd.DataFrame(cla_members_data.get('items'))

    def statistics_river_race(self,statistics_river_race_URL,token,cla_tag,cla_members_url):
        participants_war = pd.DataFrame()
        statistics_river_race_data = self.make_request(statistics_river_race_URL, token)

        cla_members = self.cla_members(cla_members_url,token)[['tag','role']]

        for river_races in statistics_river_race_data.get('items'):
            seasonId = river_races.get('seasonId')
            sectionIndex = river_races.get('sectionIndex') 
            createdDate = river_races.get('createdDate')[:8]
            ranking = river_races.get('standings')

            for ranking in ranking:
                if ranking.get('clan').get('tag') == f'#{cla_tag[3:]}':
                    ranking_clan = ranking.get('clan')
                    participants = pd.DataFrame(ranking_clan.get('participants'))
                    participants = participants[participants['tag'].isin(cla_members['tag'].values.tolist())]
                    participants = pd.merge(participants, cla_members, on='tag')
                    participants['seasonId'] = seasonId
                    participants['sectionIndex'] = sectionIndex
                    participants['createdDate'] = createdDate
                    participants['createdDate'] = pd.to_datetime(participants['createdDate'])
                    participants['cla_ranking'] = ranking.get('rank')
                    participants_war = participants_war.append(participants)
                    print(f'Read data from river race SeasonID {seasonId} created on {createdDate}')
        return participants_war



