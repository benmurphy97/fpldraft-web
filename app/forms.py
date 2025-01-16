from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, InputRequired, NumberRange


class LeagueIDForm(FlaskForm):
    league_id = IntegerField('League ID', 
                             validators=[InputRequired(), 
                                         NumberRange(min=2, 
                                                     max=None,
                                                     message='Negative IDs are not valid')])
    submit = SubmitField('Generate Insights')
