from quizapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    """Keep track of logged-in user."""
    return User.query.get(int(user_id))


tags = db.Table('tags',
    db.Column('question_id', db.Integer, db.ForeignKey('quizquestion.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
    )


class Userscore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('quizquestion.id'))
    total = db.Column(db.Integer, default=0)
    correct = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'Score({self.user_id}, {self.question_id}, {self.correct}, {self.total}, {self.correct / self.total})'


class Quizquestion(db.Model):
    """Database Model for Flashcard Questions."""

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, unique=True, nullable=False)
    answer = db.Column(db.String, nullable=False)
    chapter = db.Column(db.Integer, nullable=False)
    #daily = db.Column(db.Boolean, default=False)
    tags = db.relationship('Tag', secondary='tags', 
        backref=db.backref('questions', lazy=True))

    def __repr__(self):
        """Representation of QuizQuestion Model."""
        return f"QuizQuestion({self.question}, {self.answer}, {self.tags})"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String, unique=True, nullable=False)
    def __repr__(self):
        return f"Tag({self.label})"


class User(db.Model, UserMixin):
    """User Model."""

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    questions_answered = db.relationship('Quizquestion', secondary='userscore',
        backref=db.backref('user', lazy=True))

    def __repr__(self):
        """Representation of User Model."""
        return f"User({self.email}, {self.password})"
