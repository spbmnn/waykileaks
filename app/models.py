from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import app, login, db
import jwt
from time import time

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    alive = db.Column(db.Boolean, default=True)
    role = db.Column(db.Integer, default=1)
    ''' USER ROLE IDS:
        1: Serf (user)
        2: Baron (approved user)
        3: Vassal (moderator)
        4: King (admin)
    '''

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_role(self):
        return self.role

    def get_karma(self):
        karma = 0
        for quote in self.submissions:
            karma += quote.score
        return karma

    def get_approved_count(self):
        count = 0
        for quote in self.submissions:
            if quote.published:
                count += 1
        return count

    def get_existence(self):
        return self.alive

    def get_password_reset_token(self, expires_in=600):
        return jwt.encode(
                {'reset_password': self.id, 'exp': time() + expires_in},
                app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                    algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    u = User.query.get(int(id))
    if u:
        return u
    else:
        return None

class Speaker(db.Model):
    __tablename__ = 'speaker'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True)

class Quote(db.Model):
    __tablename__ = 'quote'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1024), unique=True)
    topic = db.Column(db.String(256))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    submitter = db.relationship(User, backref='submissions')
    user_id = db.Column(db.Integer, db.ForeignKey(User.id)) # not entirely sure if this is necessary
    speaker = db.relationship(Speaker, backref='quotes')
    speaker_id = db.Column(db.Integer, db.ForeignKey(Speaker.id)) # this too
    published = db.Column(db.Boolean, default=False)
    moderated = db.Column(db.Boolean, default=False)
    deny_reason = db.Column(db.String(128))
    score = db.Column(db.Integer, default=0)

    def __init__(self, speaker_id, body, topic, user_id):
        self.speaker_id = speaker_id
        self.body = body
        self.topic = topic
        self.user_id = user_id

    def __repr__(self):
        return '<Quote on {}>'.format(self.topic)

    def has_upvoted(self, user_id):
        select_votes = quote_upvotes.select(
            db.and_(
                quote_upvotes.c.user_id == user_id,
                quote_upvotes.c.quote_id == self.id
            )
        )
        rs = db.engine.execute(select_votes).first()
        if rs is None: # the original thing had rowcount but that's always -1??
            return False
        else:
            return True

    def has_downvoted(self, user_id):
        select_votes = quote_upvotes.select(
            db.and_(
                quote_downvotes.c.user_id == user_id,
                quote_downvotes.c.quote_id == self.id
            )
        )
        rs = db.engine.execute(select_votes).first()
        if rs is None:
            return False
        else:
            return True

    def upvote(self, user_id): # props to codelucas/flask-reddit
        already_voted = self.has_upvoted(user_id)
        vote_status = None
        if not already_voted:
            if self.has_downvoted(user_id):
                self.downvote(user_id)
            db.engine.execute(
                    quote_upvotes.insert(),
                    user_id = user_id,
                    quote_id = self.id
            )
            self.score += 1
            vote_status = True
        else:
            db.engine.execute(
                    quote_upvotes.delete(
                        db.and_(
                            quote_upvotes.c.user_id == user_id,
                            quote_upvotes.c.quote_id == self.id
                        )
                    )
            )
            self.score -= 1
            vote_status = False
        db.session.commit()
        return vote_status

    def downvote(self, user_id):
        already_voted = self.has_downvoted(user_id)
        vote_status = None
        if not already_voted:
            if self.has_upvoted(user_id):
                self.upvote(user_id)
            db.engine.execute(
                    quote_downvotes.insert(),
                    user_id = user_id,
                    quote_id = self.id
            )
            self.score -= 1
            vote_status = True
        else:
            db.engine.execute(
                    quote_downvotes.delete(
                        db.and_(
                            quote_downvotes.c.user_id == user_id,
                            quote_downvotes.c.quote_id == self.id
                        )
                    )
            )
            self.score += 1
            vote_status = False
        db.session.commit()
        return vote_status

quote_upvotes = db.Table('quote_upvotes',
        db.Column('user_id', db.Integer, db.ForeignKey(User.id)),
        db.Column('quote_id', db.Integer, db.ForeignKey(Quote.id))
)

quote_downvotes = db.Table('quote_downvotes',
        db.Column('user_id', db.Integer, db.ForeignKey(User.id)),
        db.Column('quote_id', db.Integer, db.ForeignKey(Quote.id))
)

db.create_all()
db.session.commit()
