from random import shuffle
from flask import render_template, url_for, flash, redirect, request
from quizapp import app, db
from quizapp.forms import AnswerQuestionForm, CreateQuestionForm, multiple_choice_form, LoginForm
from quizapp.models import Quizquestion, User, Tag, Userscore
from flask_login import login_user, current_user, logout_user

@app.route('/')
def index():
    '''main route of app'''
    return render_template('index.html', title='Home')    


@app.route('/quiz')
def quiz():
    cards = Quizquestion.query.all()
    #shuffle(cards)
    search_tags = request.args.get('tag')
    if search_tags:
        searched = search_tags.split(', ')
        cards = set()
        for tag in searched:
            qt = Tag.query.filter_by(label=tag).first()
            for q in qt.questions:
                cards.add(q)
        
    return render_template('quiz.html', cards=cards, title='Quiz')


@app.route('/create_question', methods=['GET', 'POST'])
def create_question():
    form = CreateQuestionForm()
    if form.validate_on_submit():
        card = Quizquestion(question=form.question.data, answer=form.answer.data, chapter=int(form.chapter.data))
        db.session.add(card)
        tags_list = form.tags.data.split(', ')
        for text in tags_list:
            already_in = Tag.query.filter_by(label=text).first()
            if already_in:
                card.tags.append(already_in)
            else:
                tag = Tag(label=text)
                db.session.add(tag)
                card.tags.append(tag)

        db.session.commit()
        return redirect(url_for('quiz'))
    return render_template('create_question.html', form=form,
                                                   legend='Create Question', 
                                                   title='Create Question')


@app.route('/question/<int:card_id>', methods=['GET', 'POST'])
def individual_question(card_id):
    
    card = Quizquestion.query.filter_by(id=card_id).first()
    form = AnswerQuestionForm()
    if request.method == "POST":
        registered_score = Userscore.query.filter_by(user_id=current_user.id, question_id=card_id).first()
        if registered_score:
            registered_score.total += 1
        else:
            registered_score = Userscore(user_id=current_user.id, question_id=card_id, total=1, correct=0)
            db.session.add(registered_score)
        if form.answer.data == card.answer:
            registered_score.correct += 1
            flash('Correct', 'success')
        else:
            flash('Incorrect', 'danger')
        db.session.commit()
    return render_template('single_question.html', card=card, 
                                                   form=form,
                                                   tags=card.tags,
                                                   title='Question')


@app.route('/question<int:card_id>/edit', methods=['GET', 'POST'])
def edit_question(card_id):
    form = CreateQuestionForm()
    card = Quizquestion.query.get_or_404(card_id)
    if form.validate_on_submit():
        card.question = form.question.data
        card.answer = form.answer.data
        card.chapter = form.chapter.data

        tags_list = form.tags.data.split(', ')
        for text in tags_list:
            already_in = Tag.query.filter_by(label=text).first()
            if already_in:
                card.tags.append(already_in)
            else:
                tag = Tag(label=text)
                db.session.add(tag)
                card.tags.append(tag)
        db.session.commit()
        flash('Your post has been updated!', 'info')
        return redirect(url_for('quiz'))
    elif request.method == 'GET':
        form.question.data = card.question
        form.answer.data = card.answer
        form.chapter.data = card.chapter
        form.tags.data = ', '.join([tag.label for tag in card.tags])
    return render_template('create_question.html', title='Edit Question', form=form, card=card)


@app.route('/question/<int:card_id>/delete', methods=['POST'])
def delete_question(card_id):
    card = Quizquestion.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    flash('The question has been deleted.', 'success')
    return redirect(url_for('quiz'))


@app.route('/question/<int:card_id>/make_live', methods=['POST'])
def make_live(card_id):
    card = Quizquestion.query.get_or_404(card_id)
    db.session.commit()
    flash('The question has been deleted.', 'success')
    return redirect(url_for('quiz'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('Email not in database.', 'danger')
        elif user.password != form.password.data:
            flash('Password not correct.', 'danger')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
    return render_template('login.html', form=form, title='Login')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/live")
def live():
    questions = Quizquestion.query.filter_by(daily=True)
    return render_template('scores.html', questions=questions)
