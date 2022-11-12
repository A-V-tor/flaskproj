from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_ckeditor import CKEditorField


class FormReg(FlaskForm):
    """Класс формы регистрации"""

    name = StringField(
        "Имя ",
        validators=[
            DataRequired(),
            Length(min=4, max=20, message="От 4 до 20 символов"),
        ],
    )
    email = StringField(
        "Электронная почта ", validators=[Email("Некорректный адрес почты!")]
    )
    psw = PasswordField("Пароль ", validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField("Отправить")


class FormAvt(FlaskForm):
    """Класс формы авторизации"""

    email = StringField(
        "Электронная почта ", validators=[Email("Некорректный адрес почты!")]
    )
    remember = BooleanField("Запомнить", default=False)
    psw = PasswordField("Пароль ", validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField("Отправить")


class New_Psw(FlaskForm):
    new_psw = PasswordField(
        "Новый пароль ", validators=[DataRequired(), Length(min=4, max=20)]
    )
    check_psw = PasswordField(
        "Повтор пароля ", validators=[DataRequired(), Length(min=4, max=20)]
    )
    submit = SubmitField("Сменить пароль")


class PostUser(FlaskForm):
    title = StringField(
        "Заголовок отзыва", validators=[DataRequired(), Length(min=4, max=50)]
    )
    body = CKEditorField(
        "Комментарий", validators=[DataRequired(), Length(min=4, max=250)]
    )
    submit = SubmitField("Оставить отзыв")
