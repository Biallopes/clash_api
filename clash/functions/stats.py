import numpy as np
import pandas as pd
import os
import warnings
from functions.clash_api import clash

'''Warning ignoring'''
warnings.filterwarnings("ignore")

class statistics_clash():

    run_file = os.path.realpath(__file__)
    current_directory = os.path.dirname(os.path.dirname(run_file))
    file_path = f'{current_directory}/data/downgrade_list.csv'
    eligible_file_path = f'{current_directory}/data/eligible_prize.csv'

    def check_downgrade(self):
        '''
        check members that downgraded previosly
        '''
        downgrade_list = pd.read_csv(self.file_path)
        downgrade_list['date'] = pd.to_datetime(downgrade_list['date'])
        downgrade_list['rescue_date'] = downgrade_list['date'] + pd.DateOffset(days=42) 

        return downgrade_list

    def delete_downgrade_list(self,tag):
        '''
        delete members that downgraded expired
        '''
        df = pd.read_csv(self.file_path)
        condicao = df['tag'] == tag
        df = df[~condicao]

        df.to_csv(self.file_path, index=False)

    def return_bad_participants(self,statistics,min_points,min_decks):
        '''
        return members that don't achieved the min points
        '''        
        last_river_race_data = statistics[statistics['rank_river_race'] == 1]
        last_river_race_data_min_points = last_river_race_data[last_river_race_data['fame'] < min_points]
        last_river_race_data_min_points = last_river_race_data_min_points[last_river_race_data_min_points['decksUsed'] < min_decks]
        bad_participants = last_river_race_data_min_points[['name','tag','role','fame','decksUsed','createdDate']]

        conditions = [
                        bad_participants['role'] == 'member',
                        bad_participants['role'] == 'elder',
                        bad_participants['role'] == 'coLeader'
                    ]

        choices = ['delete','downgrade','downgrade']
        
        bad_participants['action'] = np.select(conditions, choices, default='Unknown')

        delete_participants = bad_participants[bad_participants['action'] == 'delete']
        downgrade_participants = bad_participants[bad_participants['action'] == 'downgrade']
        
        #insert downgrade to control
        downgrade_participants[['name','tag','createdDate']].to_csv(self.file_path, mode='a', index=False, header=False)

        #delete downgrade to deleted members
        for tag in delete_participants['tag']:
            self.delete_downgrade_list(tag)

        return bad_participants

    def return_promote_participants(self,statistics,bads,min_points,min_decks):
        '''
        return members that achieved the min points to the river races settled as a goal
        '''   
        #check_downgrades    
        check_downgrade = self.check_downgrade()
        #create eligible prize list
        self.eligible_prize(statistics,min_points,min_decks)

        date_last_river = str(statistics[statistics['rank_river_race'] == 1]['createdDate'].iloc[0])[:10]
        check_downgrade.loc[check_downgrade['rescue_date'] == date_last_river, 'rescue'] = 'True'
        check_downgrade.loc[check_downgrade['rescue_date'] != date_last_river, 'rescue'] = 'False'

        last_river_race_data = statistics[statistics['role'] == 'member']
        
        last_river_race_data = last_river_race_data[~last_river_race_data['name'].isin(bads['name'].values.tolist())]
        count_participation = last_river_race_data.groupby(['name', 'tag']).size().reset_index(name='qtd')

        qtd_participants = count_participation[count_participation['qtd'] == 5]

        promoted_participants = pd.merge(qtd_participants, check_downgrade[['tag','rescue_date','rescue']], on='tag', how='left')

        conditions = [
            promoted_participants['rescue'] == 'False',
            promoted_participants['rescue'] == 'True'
        ]

        choices = ['Freeze for previosly downgrade', 'promote']

        promoted_participants['action'] = np.select(conditions, choices, default='promote')

#        promoted_participants = promoted_participants[['name','action', 'rescue', 'rescue_date']]

        #delete downgrade to promoted members
        delete_downgrade = promoted_participants[promoted_participants['rescue'] == 'True']
        for tag in delete_downgrade['tag']:
            self.delete_downgrade_list(tag)

        return promoted_participants
    
    def eligible_prize(self,data,min_points,min_decks ):

        possible_eligibles = {}
        df_members = pd.DataFrame({'tag': data['tag'].unique(), 'name': data['name'].unique()})

        for season in data['sectionIndex'].unique():
            s_participants = data.loc[data['sectionIndex'] == season]
            s_participants['eligible'] = s_participants.apply(lambda row: 1 if row['fame'] >= min_points or row['decksUsed'] >= min_decks else 0, axis=1)
            dict_eligible = dict(zip(s_participants['tag'], s_participants['eligible']))

            for chave, novo_valor in dict_eligible.items():
                if novo_valor != 0:
                    if chave in possible_eligibles:
                        possible_eligibles[chave] += novo_valor
                    else:
                        possible_eligibles[chave] = novo_valor
        
        eligibles = {chave: valor for chave, valor in possible_eligibles.items() if valor == 5}

        df_eligibles = pd.DataFrame({'tag': list(eligibles.keys())})
        df_eligibles = pd.merge(df_eligibles, df_members, on='tag', how='inner')
        df_eligibles.to_csv(self.eligible_file_path, mode='w', header=True, index=False)

        print(f'Create file {self.eligible_file_path} to eligibles for prize.')
