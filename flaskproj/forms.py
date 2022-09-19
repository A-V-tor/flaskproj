from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length


class FormRegAvt(FlaskForm):
    '''Класс для формы регистрации и авторизации'''
    name = StringField('Имя ', validators=[DataRequired(), Length(min=4, max=20, message='От 4 до 20 символов')])
    email = StringField('Электронная почта ', validators=[Email('Некорректный адрес почты')])
    remember = BooleanField('Запомнить', default=False)
    psw = PasswordField('Пароль ', validators=[DataRequired(),Length(min=4, max=20)])
    submit  = SubmitField('Отправить')