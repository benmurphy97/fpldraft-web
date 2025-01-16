from flask import render_template, request
from app import app
from app.forms import LeagueIDForm
import json
from urllib.request import urlopen 
import pandas as pd

@app.route('/')
@app.route('/index')
def index():
    return 'Hello World'

@app.route('/user_input_league_id', methods=['POST'])
def user_input_league_id():

    form = LeagueIDForm()
    
    return render_template('login.html', title='Sign In', form=form)


@app.route('/generate_league_insights', methods=['POST'])
def generate_league_insights():

    league_id = request.form.get('league_id')

    return f'{league_id}'



@app.route('/chart')
def chart():
    
    # parameter for urlopen 
    url = "https://draft.premierleague.com/api/league/18985/details"
    
    # store the response of URL 
    response = urlopen(url) 
    
    # storing the JSON response  
    data_json = json.loads(response.read()) 

    ids = [i['id'] for i in data_json['league_entries']]
    names = [i['short_name'] for i in data_json['league_entries']]
    id_name_map = {i:v for i,v in zip(ids,names)}


    s_df = pd.DataFrame(data_json['standings'])

    s_df['player'] = s_df['league_entry'].apply(lambda x: id_name_map[x])

    s_df['average_points_for'] = s_df['points_for'] / (s_df['matches_won'] + s_df['matches_lost'] + s_df['matches_drawn'])
    s_df['average_points_against'] = s_df['points_against'] / (s_df['matches_won'] + s_df['matches_lost'] + s_df['matches_drawn'])

    x = s_df['average_points_for'].values.tolist()
    y = s_df['average_points_against'].values.tolist()


    data_dict = []
    for i,v in zip(x, y):
        d = {'x': i, 'y': v}
        data_dict.append(d)
 
    return render_template(
        template_name_or_list='chart.html',
        data_dict=data_dict
        )



@app.route('/fplchart')
def fplchart():
    # Define Plot Data 
    # parameter for urlopen 
    url = "https://draft.premierleague.com/api/league/18985/details"
    
    # store the response of URL 
    response = urlopen(url) 
    
    # storing the JSON response  
    data_json = json.loads(response.read()) 

    ids = [i['id'] for i in data_json['league_entries']]
    names = [i['short_name'] for i in data_json['league_entries']]
    id_name_map = {i:v for i,v in zip(ids,names)}


    s_df = pd.DataFrame(data_json['standings'])

    s_df['player'] = s_df['league_entry'].apply(lambda x: id_name_map[x])

    s_df['average_points_for'] = s_df['points_for'] / (s_df['matches_won'] + s_df['matches_lost'] + s_df['matches_drawn'])
    s_df['average_points_against'] = s_df['points_against'] / (s_df['matches_won'] + s_df['matches_lost'] + s_df['matches_drawn'])

    x = s_df['average_points_for'].values.tolist()
    y = s_df['average_points_against'].values.tolist()


    data_dict = []
    for i,v in zip(x, y):
        d = {'x': i, 'y': v}
        data_dict.append(d)

    print(data_dict)
    data_dict = [{'x': -10, 'y': 0}, 
                 {'x': 0, 'y': 10}, 
                 {'x': 10, 'y': 5}, 
                 {'x': 0.5, 'y': 5.5}
                 ]
    
    data_dict = [{'x': 41.8, 'y': 39.55}, 
                 {'x': 42.55, 'y': 35.45}, 
                 {'x': 44.85, 'y': 39.5}, 
                 {'x': 43.45, 'y': 40.2}, 
                 {'x': 38.1, 'y': 39.3}, 
                 {'x': 37.9, 'y': 39.6},
                 {'x': 41.7, 'y': 40.85}, 
                 {'x': 34.25, 'y': 40.55}, 
                 {'x': 36.5, 'y': 41.95}, 
                 {'x': 35.15, 'y': 39.3}]
        
 
    return render_template(
        template_name_or_list='fplchart.html',
        data_dict=data_dict
        )