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


class Quizquestion(db.Model):
    """Database Model for Flashcard Questions."""

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, unique=True, nullable=False)
    answer = db.Column(db.String, nullable=False)
    chapter = db.Column(db.Integer, nullable=False)
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

    def __repr__(self):
        """Representation of User Model."""
        return f"User({self.email}, {self.password})"
