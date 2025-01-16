from flask import render_template, request
from app import app
from app.forms import LeagueIDForm
import json
from urllib.request import urlopen 
import pandas as pd

@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html', title='Home')

@app.route('/user_input_league_id', methods=['GET', 'POST'])
def user_input_league_id():
    form = LeagueIDForm()
    return render_template('user_input_league_id.html', title='League ID Input', form=form)

@app.route('/chart', methods=['GET', 'POST'])
def chart():
    
    league_id = request.form.get('league_id')

    # define url for fpl api
    # url = "https://draft.premierleague.com/api/league/18985/details"
    url = f"https://draft.premierleague.com/api/league/{league_id}/details"

    # store the response of URL 
    response = urlopen(url) 
    
    # storing the JSON response  
    data_json = json.loads(response.read()) 

    ids = [i['id'] for i in data_json['league_entries']]
    names = [i['short_name'] for i in data_json['league_entries']]
    id_name_map = {i:v for i,v in zip(ids,names)}

    # create dataframe of current standings
    s_df = pd.DataFrame(data_json['standings'])

    s_df['player'] = s_df['league_entry'].apply(lambda x: id_name_map[x])
    player_initials = s_df['player'].values.tolist()

    s_df['average_points_for'] = s_df['points_for'] / (s_df['matches_won'] + s_df['matches_lost'] + s_df['matches_drawn'])
    s_df['average_points_against'] = s_df['points_against'] / (s_df['matches_won'] + s_df['matches_lost'] + s_df['matches_drawn'])

    x = s_df['average_points_for'].values.tolist()
    y = s_df['average_points_against'].values.tolist()

    del(s_df)

    data_dict = []
    for i,v in zip(x, y):
        d = {'x': i, 'y': v}
        data_dict.append(d)
 
    return render_template(
        template_name_or_list='chart.html',
        league_id=league_id,
        data_dict=data_dict,
        labels=player_initials)
