from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SelectMultipleField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import ColorInput
from models import Team, Staff, Stadium, Competitions, Division, TimerDisplayMode, Player
import os


class MatchForm(FlaskForm):
    team_a = SelectField('Drużyna A', validators=[DataRequired()], choices=[('', '')])
    team_b = SelectField('Drużyna B', validators=[DataRequired()], choices=[('', '')])
    periods = IntegerField('ilość części meczu', validators=[DataRequired()])
    period_length = StringField('długość części meczu (s)', validators=[DataRequired()])
    panel_timer_display_mode = SelectField('format czasu (panel)', validators=[DataRequired()], choices=[('', '')])
    is_panel_timer_ascending = BooleanField('czy czas rosnąco? (panel)')
    stream_timer_display_mode = SelectField('format czasu (stream)', validators=[DataRequired()], choices=[('', '')])
    is_stream_timer_ascending = BooleanField('czy czas rosnąco? (stream)')
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
        competition_id = 1
        for key, value in kwargs.items():
            if key == 'competition_id':
                competition_id = int(str(value))
        _competition = Competitions.query.filter_by(id=competition_id).first()
        self.team_a.choices = [('', '')] + [(team.id, team.full_name) for team in Team.query.filter_by(
            competitions=competition_id).order_by('full_name').all()]
        self.team_b.choices = [('', '')] + [(team.id, team.full_name) for team in Team.query.filter_by(
            competitions=competition_id).order_by('full_name').all()]
        self.cameramen.choices = [(staff.id, staff.first_name + ' ' + staff.last_name) for staff in
                                  Staff.query.order_by('last_name').all()]
        self.commentators.choices = [(staff.id, staff.first_name + ' ' + staff.last_name) for staff in
                                     Staff.query.order_by('last_name').all()]
        self.referees.choices = [(staff.id, staff.first_name + ' ' + staff.last_name) for staff in
                                 Staff.query.order_by('last_name').all()]
        self.stadium.choices = [(stadium.id, stadium.name + ' ' + stadium.address) for stadium in
                                Stadium.query.order_by('name').all()]
        self.competitions.choices = [(competitions.id, competitions.name) for competitions in
                                     Competitions.query.order_by('name').all()]
        self.competitions.default = competition_id
        self.division.choices = [(division.id, division.name) for division in
                                 Division.query.filter_by(competition_id=competition_id).order_by('id').all()]
        self.period_length.default = _competition.period_length
        self.panel_timer_display_mode.choices = [(display_mode.id, display_mode.format) for display_mode in
                                                 TimerDisplayMode.query.order_by('id').all()]
        self.panel_timer_display_mode.default = _competition.panel_timer_display_mode
        self.is_panel_timer_ascending.default = _competition.is_panel_timer_ascending
        self.stream_timer_display_mode.choices = [(display_mode.id, display_mode.format) for display_mode in
                                                  TimerDisplayMode.query.order_by('id').all()]
        self.stream_timer_display_mode.default = _competition.stream_timer_display_mode
        self.is_stream_timer_ascending.default = _competition.is_stream_timer_ascending
        self.is_added_time_allowed.default = _competition.is_added_time_allowed


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
    bibs_color = StringField('Lebijka', widget=ColorInput(), default='#0F0')
    logo_file = SelectField('Wybierz logo')
    competitions = SelectField('Rozgrywki', validators=[DataRequired()])
    name_16 = StringField('Nazwa 16', validators=[DataRequired(), Length(min=3, max=16)])

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


class MatchPeriodForm(FlaskForm):
    length = IntegerField('Period length', validators=[DataRequired()])
    submit = SubmitField('Dodaj')


class PlayerForm(FlaskForm):
    default_nr = StringField('Numer')
    first_name = StringField('Imię', validators=[DataRequired])
    last_name = StringField('Nazwisko', validators=[DataRequired])
    is_goalkeeper = BooleanField('Bramkarz')
    is_captain = BooleanField('Kapitan')
