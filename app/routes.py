from flask import render_template, request, redirect, url_for, flash
from app import app
from app.forms import LeagueIDForm
import json
from urllib.request import urlopen 
import pandas as pd


@app.route('/')
@app.route('/user_input_league_id', methods=['GET', 'POST'])
def user_input_league_id():

    form = LeagueIDForm()

    if form.validate_on_submit():
        return redirect(url_for('chart'))
    
    return render_template('user_input_league_id.html', title='League ID Input', form=form)


@app.route('/chart', methods=['GET', 'POST'])
def chart():
    
    league_id = request.form.get('league_id')

    # the league id enterred may be valid input but the number doesnt correspond to a League ID
    # IDs are created iteratively - most recently created league will have the largest ID number but we dont know what the largest one is
    # define url for fpl api
    url = f"https://draft.premierleague.com/api/league/{league_id}/details"

    try:
        # store the response of URL 
        response = urlopen(url) 
    except:
        flash('The League ID enterred could not be loaded. Try again with a different League ID.')
        return redirect(url_for('user_input_league_id'))
    
    # storing the JSON response  
    data_json = json.loads(response.read())

    # if scoring is head-to-head format
    if data_json['league']['scoring'] == 'h':

        league_details = data_json['league']
        league_name = league_details['name']

        # scatter plot
        ids = [i['id'] for i in data_json['league_entries']]
        names = [i['short_name'] for i in data_json['league_entries']]
        id_name_map = {i:v for i,v in zip(ids,names)}

        # create dataframe of current standings
        s_df = pd.DataFrame(data_json['standings'])

        s_df['player'] = s_df['league_entry'].apply(lambda x: id_name_map[x])
        player_initials = s_df['player'].values.tolist()

        s_df['average_points_for'] = s_df['points_for'] / (s_df['matches_won'] + s_df['matches_lost'] + s_df['matches_drawn'])
        s_df['average_points_against'] = s_df['points_against'] / (s_df['matches_won'] + s_df['matches_lost'] + s_df['matches_drawn'])

        pts_for = s_df['average_points_for'].values.tolist()
        pts_against = s_df['average_points_against'].values.tolist()

        scatter_data = []
        for i,v in zip(pts_for, pts_against):
            d = {'x': i, 'y': v}
            scatter_data.append(d)

        # expected league table
        matches = pd.DataFrame(data_json['matches'])

        matches1 = matches.loc[matches['finished']==True]
        matches1.drop(columns=['finished', 'started', 'winning_league_entry', 'winning_method'], inplace=True)
        matches1.rename(columns={'event': 'week',
                                'league_entry_1': 'player',
                                'league_entry_1_points': 'points_for',
                                'league_entry_2': 'opponent',
                                'league_entry_2_points': 'points_against'},
                    inplace=True)


        matches2 = matches.loc[matches['finished']==True]
        matches2.drop(columns=['finished', 'started', 'winning_league_entry', 'winning_method'], inplace=True)
        matches2.rename(columns={'event': 'week',
                                'league_entry_1': 'opponent',
                                'league_entry_1_points': 'points_against',
                                'league_entry_2': 'player',
                                'league_entry_2_points': 'points_for'},
                    inplace=True)

        matches_df = pd.concat([matches1, matches2]).sort_values(by=['week', 'points_for'], ascending=[True, False]).reset_index(drop=True)



        # get the rank of each players score in the gameweek
        matches_df['points_for_week_rank'] = matches_df.groupby('week')['points_for'].rank(ascending=False, method='max')
        matches_df['points_against_week_rank'] = matches_df.groupby('week')['points_against'].rank(ascending=False, method='min')


        matches_df['player'] = matches_df['player'].apply(lambda x: id_name_map[x].strip())

        matches_df['number_of_opponents_beaten_in_week'] = 10-matches_df['points_for_week_rank']
        matches_df['number_of_opponents_drawn_to_in_week'] = matches_df[['week', 'points_for']].duplicated(keep=False).astype(int).values


        matches_df['prob_winning_week'] = matches_df['number_of_opponents_beaten_in_week'].apply(lambda x: x/9)
        matches_df['prob_losing_week'] = 1 - matches_df['prob_winning_week']

        matches_df['expected_points_win'] = matches_df['prob_winning_week']*3
        matches_df['expected_points_draw'] = matches_df['number_of_opponents_drawn_to_in_week'].apply(lambda x: (x/9) * 1 )

        matches_df['expected_points'] = matches_df['expected_points_win'] + matches_df['expected_points_draw']

        s_df = pd.DataFrame(data_json['standings'])
        s_df['player'] = s_df['league_entry'].apply(lambda x: id_name_map[x])

        # aggregate epected points by player
        expected_standing = matches_df.groupby('player')['expected_points'].sum().round(1).reset_index()

        # get real standings
        standings = s_df[['player', 'total']].sort_values('player').reset_index(drop=True)
        standings['player'] = standings['player'].str.strip() # format player name



        standings['expected_points'] = expected_standing['expected_points']
        standings['over/under performance'] = standings['total']-standings['expected_points']
        standings.rename({'total': 'actual_points'}, inplace=True)
        standings.columns = ['Player', 'Actual Points', 'Expected Points', 'Over/Under Performance']

        print(standings)

        standings = standings.sort_values(by='Expected Points', ascending=False)

        xlt_row_data=list(round(standings,2).values.tolist())
        xlt_col_names = standings.columns.values

        return render_template(
            template_name_or_list='chart.html',
            league_id=league_id,
            data_dict=scatter_data,
            labels=player_initials,

            column_names=xlt_col_names, 
            row_data=xlt_row_data,
            zip=zip,
            
            league_name=league_name)
    
    else:
        flash('Only head-to-head leagues are currently supported. Try again with a different League ID.')
        return redirect(url_for('user_input_league_id'))



# @app.route('/rugby_matches')
# def rugby_matches():


#     # Fixtures with odds
#     # TODO find out what date the matches were on - join on match time, home and away team
#     odds = pd.read_csv("urc_latest_results_odds.csv")
#     odds_row_data=list(odds.values.tolist())
#     odds_col_names = odds.columns.values

#     # get what the predictions were for the past matches

#     return render_template('rugby_matches.html', 
#                            title='Rugby Matches',
#                             column_names=odds_col_names, 
#                             row_data=odds_row_data,
#                             zip=zip)


# @app.route('/rugby_season_simulation')
# def rugby_season_simulation():
#     return render_template('rugby_season_simulation.html', 
#                            title='Rugby Season Simulation')