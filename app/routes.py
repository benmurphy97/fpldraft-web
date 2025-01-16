from flask import render_template, request
from app import app
from app.forms import LeagueIDForm

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
    # Define Plot Data 
    x = [0, 10, 15, 8, 22, 18, 25]
    y = [7, 8, 4, 6, 10, 2, 6]

    data_dict = {"data_1": [1, 2, 3, 4], 
                "data_2": [5, 6, 7, 8]}

    data_dict = [{
        'x': -10,
        'y': 0
        }, {
        'x': 0,
        'y': 10
        }, {
        'x': 10,
        'y': 5
        }, {
        'x': 0.5,
        'y': 5.5
        }]
 
    return render_template(
        template_name_or_list='chart.html',
        data_dict=data_dict
        )