from random import shuffle
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email

class CreateQuestionForm(FlaskForm):
    """Form for creating new Questions. Admin use only."""

    question = TextAreaField('Question', validators=[DataRequired()])
    answer = StringField('Answer', validators=[DataRequired()])
    chapter = IntegerField('Chapter', validators=[DataRequired()])
    tags = StringField('Tags', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AnswerQuestionForm(FlaskForm):
    """Form for fill-in-the-blank question answers."""

    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Submit')


def multiple_choice_form(card):
    """Function allows card object to be passed to form."""
    correct = int(card.answer)
    choices = [correct, correct+1, correct * 2, correct //2]
    shuffle(choices)
    class MultipleChoiceForm(FlaskForm):
        """Form for multiple-choice question answers."""

        answer = RadioField('Answer', choices=choices)
        submit = SubmitField('Submit')
    return MultipleChoiceForm()


class LoginForm(FlaskForm):
    """Form for logging in users."""

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')
    remember = BooleanField('Remember Me')
