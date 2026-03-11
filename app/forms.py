from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 80)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 80)])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 128)])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名已被使用，请选择其他用户名。')


class PostForm(FlaskForm):
    content = TextAreaField('发表言论', validators=[DataRequired(), Length(1, 200)])
    submit = SubmitField('发布')


class CommentForm(FlaskForm):
    content = TextAreaField('评论', validators=[DataRequired(), Length(1, 200)])
    submit = SubmitField('评论')


class SearchForm(FlaskForm):
    q = StringField('搜索', validators=[DataRequired()])
    submit = SubmitField('搜索')
