from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length


class FormReg(FlaskForm):
    '''Класс формы регистрации '''
    name = StringField('Имя ', validators=[DataRequired(), Length(min=4, max=20, message='От 4 до 20 символов')])
    email = StringField('Электронная почта ', validators=[Email('Некорректный адрес почты!')])
    psw = PasswordField('Пароль ', validators=[DataRequired(),Length(min=4, max=20)])
    submit  = SubmitField('Отправить')


class FormAvt(FlaskForm):
    '''Класс формы авторизации'''
    name = StringField('Имя ', validators=[DataRequired(), Length(min=4, max=20, message='От 4 до 20 символов')])
    remember = BooleanField('Запомнить', default=False)
    psw = PasswordField('Пароль ', validators=[DataRequired(),Length(min=4, max=20)])
    submit  = SubmitField('Отправить')