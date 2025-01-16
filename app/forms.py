from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo


class LeagueIDForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    league_id = IntegerField('League ID', validators=[DataRequired()])
    submit = SubmitField('Generate Insights')