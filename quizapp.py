from random import randint, shuffle
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField, PasswordField, RadioField
from wtforms.validators import DataRequired, Email
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


# Configs
app = Flask(__name__)
app.config['SECRET_KEY'] = 'testing'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

########## Utilities ##########

########## Models ##########
class QuizQuestion(db.Model):
    '''Database Model for Flashcard Questions'''
    id = db.Column(db.Integer, primary_key=True)
    ## Basic Data ##
    question = db.Column(db.Text, unique=True, nullable=False)
    answer = db.Column(db.String, nullable=False)
    ## Categories ##
    tags = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"QuizQuestion({self.question}, {self.answer}, {self.tags})"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


########## Forms ##########

class CreateQuestionForm(FlaskForm):
    question = TextAreaField('Question', validators=[DataRequired()])
    answer = StringField('Answer', validators=[DataRequired()])
    tags = StringField('Tags', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AnswerQuestionForm(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Submit')


def multiple_choice_form(card):
    correct = int(card.answer)
    choices = [correct, correct+1, correct * 2, correct //2]
    shuffle(choices)
    class MultipleChoiceForm(FlaskForm):
        answer = RadioField('Answer', choices=choices)
        submit = SubmitField('Submit')
    return MultipleChoiceForm()


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

########## Routes ##########

@app.route('/')
def index():
    '''main route of app'''
    return render_template('index.html', title='Home')

@app.route('/quiz')
def quiz():
    cards = QuizQuestion.query.all()
    shuffle(cards)
    tags = request.args.get('tag')
    if tags:
        tags = tags.split(',')
        cards = [card for card in cards if any([tag in card.tags for tag in tags])]
    return render_template('quiz.html', cards=cards, title='Quiz')

@app.route('/create_question', methods=['GET', 'POST'])
def create_question():
    form = CreateQuestionForm()
    if form.validate_on_submit():
        card = QuizQuestion(question=form.question.data, answer=form.answer.data, tags=form.tags.data)
        db.session.add(card)
        db.session.commit()
        print(card)
        return redirect(url_for('quiz'))
    return render_template('create_question.html', form=form, legend='Create Question', title='Create Question')


@app.route('/question/<int:card_id>', methods=['GET', 'POST'])
def individual_question(card_id):
    
    card = QuizQuestion.query.filter_by(id=card_id).first()
    form = multiple_choice_form(card)
    if request.method == "POST":
        print(form.answer.data)
        if form.answer.data == card.answer:
            flash('Correct', 'success')
        else:
            flash('Incorrect', 'danger')
    return render_template('multiple_choice.html', card=card, 
                                                   form=form, 
                                                   title='Question')


@app.route('/question<int:card_id>/edit', methods=['GET', 'POST'])
def edit_question(card_id):
    form = CreateQuestionForm()
    card = QuizQuestion.query.get_or_404(card_id)
    if form.validate_on_submit():
        card.question = form.question.data
        card.answer = form.answer.data
        card.tags = form.tags.data
        db.session.commit()
        flash('Your post has been updated!')
        return redirect(url_for('quiz'))
    elif request.method == 'GET':
        form.question.data = card.question
        form.answer.data = card.answer
        form.tags.data = card.tags
    return render_template('create_question.html', title='Edit Question', form=form)


@app.route('/question/<int:card_id>/delete', methods=['POST'])
def delete_question(card_id):
    card = QuizQuestion.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    flash('The question has been deleted.', 'success')
    return redirect(url_for('quiz'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form, title='Login')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
