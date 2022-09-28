from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
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


class FormAddCard(FlaskForm):
    """Форма для привязки карты"""
    number_card = StringField('Номер карты', validators=[DataRequired(), Length(min=19, max=19)])
    validity = StringField('Срок действия', validators=[DataRequired()])
    secret_code = StringField('Секретный код', validators=[DataRequired(),Length(min=3, max=3)])
    firstname = StringField('Имя', validators=[DataRequired(), Length(min=2, max=80)])
    surname = StringField('Фамилия', validators=[DataRequired(), Length(min=4, max=80)])
    patronymic = StringField('Отчество', validators=[DataRequired(), Length(min=4, max=80)])
    submit = SubmitField('Добавить')