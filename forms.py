from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SelectMultipleField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import ColorInput
from models import Team, Staff, Stadium, Competitions, Division, TimerDisplayMode
import os


class MatchForm(FlaskForm):
    team_a = SelectField('Drużyna A', validators=[DataRequired()], choices=[('', '')])
    team_b = SelectField('Drużyna B', validators=[DataRequired()], choices=[('', '')])
    periods = IntegerField('ilość części meczu', validators=[DataRequired()])
    period_length = IntegerField('długość części meczu (s)', validators=[DataRequired()])
    is_actual = BooleanField('Aktualny mecz')
    is_added_time_allowed = BooleanField('Czas dodatkowy')
    extra_time_periods = IntegerField('ilość części dogrywki', validators=[DataRequired()])
    extra_time_period_length = IntegerField('długość części dogrywki (s)', validators=[DataRequired()])
    cameramen = SelectMultipleField('Kamerzyści', validators=[DataRequired()])
    commentators = SelectMultipleField('Komentatorzy', validators=[DataRequired()])
    referees = SelectMultipleField('Sędziowie', validators=[DataRequired()])
    stadium = SelectField('Stadion', validators=[DataRequired()])
    date_time = StringField('Data i godzina', validators=[DataRequired()])
    competitions = SelectField('Rozgrywki', validators=[DataRequired()])
    division = SelectField('Dywizja', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        self.team_a.choices = [('', '')] + [(team.id, team.full_name) for team in Team.query.order_by('full_name').all()]
        self.team_b.choices = [('', '')] + [(team.id, team.full_name) for team in Team.query.order_by('full_name').all()]
        self.cameramen.choices = [(staff.id, staff.first_name + ' ' + staff.last_name) for staff in Staff.query.order_by('last_name').all()]
        self.commentators.choices = [(staff.id, staff.first_name + ' ' + staff.last_name) for staff in Staff.query.order_by('last_name').all()]
        self.referees.choices = [(staff.id, staff.first_name + ' ' + staff.last_name) for staff in Staff.query.order_by('last_name').all()]
        self.stadium.choices = [(stadium.id, stadium.name + ' ' + stadium.address) for stadium in Stadium.query.order_by('name').all()]
        self.competitions.choices = [(competitions.id, competitions.name) for competitions in Competitions.query.order_by('name').all()]
        self.division.choices = [(division.id, division.name) for division in Division.query.order_by('name').all()]


class CreateTeamForm(FlaskForm):
    full_name = StringField('Nazwa', validators=[DataRequired()])
    short_name = StringField('Skrót', validators=[DataRequired()])
    link = StringField('Link do nalffutsal.pl (opcjonalnie)')
    home_color_1 = StringField('Kolory stroju 1', widget=ColorInput())
    home_color_2 = StringField(widget=ColorInput())
    home_color_3 = StringField(widget=ColorInput())
    away_color_1 = StringField('Kolory stroju 2', widget=ColorInput())
    away_color_2 = StringField(widget=ColorInput())
    away_color_3 = StringField(widget=ColorInput())
    logo_file = SelectField('Wybierz logo')
    competitions = SelectField('Rozgrywki', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(CreateTeamForm, self).__init__(*args, **kwargs)
        self.logo_file.choices = self.get_logo_choices()
        self.competitions.choices = [(competitions.id, competitions.name) for competitions in
                                     Competitions.query.order_by('name').all()]

    def get_logo_choices(self):
        logos_folder_path = os.path.join(os.getcwd(), 'static', 'images', 'logos')
        logo_files = [f for f in os.listdir(logos_folder_path)
                      if os.path.isfile(os.path.join(logos_folder_path, f))
                      and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        logo_choices = [(logo, logo) for logo in logo_files]
        return logo_choices


class EditTeamForm(FlaskForm):
    squad = BooleanField('Squad')
    default_nr = StringField('Default Number', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    position = BooleanField('Position')
    captain = BooleanField('Captain')
    submit = SubmitField('Save Changes')


class TimerDisplayModeForm(FlaskForm):
    format = SelectField('Format czasu', validators=[DataRequired()], choices=[('', '')])

    def __init__(self, *args, **kwargs):
        super(TimerDisplayModeForm, self).__init__(*args, **kwargs)
        self.format.choices = [('', '')] + [(mode.id, mode.format) for mode in TimerDisplayMode.query.all()]
