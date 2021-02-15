from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, PasswordField, 
                     RadioField, SelectField, TextAreaField, SubmitField)
from wtforms.validators import DataRequired, Email
from wtforms.fields.html5 import DateField, TimeField, EmailField


class ReservationForm(FlaskForm):

    name = StringField('* Imię:', validators=[DataRequired()])
    email = EmailField('* Adres e-mail:', validators=[DataRequired(), Email()])
    date = DateField('* Preferowana data rejsu:', validators=[DataRequired()], format='%Y-%m-%d')
    time = TimeField('* Orientacyjna godzina rejsu:', validators=[DataRequired()], format='%H:%M')
    duration = SelectField('* Długość rejsu:',
                          choices=[('1h', '1 godzina'), ('2h', '2 godziny'),
                                   ('3h', '3 godziny')] ,validators=[DataRequired()])
    numbers = SelectField('* Zakładana liczba osób:',
                          choices=[('<6', 'mniej niż 6 osób'), ('6-10', 'od 6 do 10 osób'),
                                   ('>10', 'ponad 10 osób')] ,validators=[DataRequired()])
    feedback = TextAreaField('Informacje dodatkowe:')
    submit = SubmitField('Prześlij zapytanie')


class ConfirmationForm(FlaskForm):
    confirmation = TextAreaField('Szczegóły potwierdzenia:', validators=[DataRequired()])
    submit = SubmitField('Potwierdzone')
    
    
class EmailForm(FlaskForm):
    email_text = TextAreaField('Wypełnij treść maila:', validators=[DataRequired()])
    submit = SubmitField('Wyślij e-mail')

    
class LoginForm(FlaskForm):
    username = StringField('Nazwa:', validators=[DataRequired()])
    password = PasswordField('Hasło:', validators=[DataRequired()])
    submit = SubmitField('Zaloguj')
