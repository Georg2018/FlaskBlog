from flask_wtf import FlaskForm
from flask_login import current_user
from flask_pagedown.fields import PageDownField
from wtforms import (
    widgets,
    StringField,
    IntegerField,
    TextField,
    SubmitField,
    BooleanField,
    SelectMultipleField,
)
from wtforms.validators import (
    Length, NumberRange, DataRequired, Email, Regexp, Optional
)
from wtforms import ValidationError
from .. import User


class UserInfoForm(FlaskForm):
    name = StringField("Name", validators=[Length(1, 32), Optional()])
    age = IntegerField(
        "Age",
        validators=[NumberRange(1, 200, "You must input a valid number."), Optional()],
    )
    location = StringField("Location", validators=[Length(1, 64), Optional()])
    about_me = TextField("About me", validators=[Length(1, 100), Optional()])
    submit = SubmitField("Submit")


class CheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=True)
    option_widget = widgets.CheckboxInput()


class AdminInfoEditForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 20), Email()])
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 20),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Username must have only letter, numbers, dots or underscores.",
            ),
        ],
    )
    confirmed = BooleanField("Confirmed", validators=[])
    active = BooleanField("Active", validators=[])

    name = StringField("Name", validators=[Length(1, 32), Optional()])
    age = IntegerField(
        "Age",
        validators=[NumberRange(1, 200, "You must input a valid number."), Optional()],
    )
    location = StringField("Location", validators=[Length(1, 64), Optional()])
    about_me = TextField("About me", validators=[Length(1, 100), Optional()])
    submit = SubmitField("Submit")

    permission = CheckboxField("Permission")

    def validate_email(self, field):
        if (
            field.data
            and field.data != self.user.email
            and User.query.filter_by(_email=field.data).first()
        ):
            raise ValidationError("Email already exists.")

    def validate_username(self, field):
        if (
            field.data
            and field.data != self.user.username
            and User.query.filter_by(username=field.data).first()
        ):
            raise ValidationError("Username already exists.")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[Length(1, 128)])
    body = PageDownField("Input your mind", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    body = StringField("Comment", validators=[Length(1, 526), DataRequired()])
    submit = SubmitField("Submit")

class SearchForm(FlaskForm):
    text = StringField('Search', validators=[Length(1, 256), DataRequired()])
    submit = SubmitField("submit")