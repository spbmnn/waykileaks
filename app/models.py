from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import login, db


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
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
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

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
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    speaker = db.relationship(Speaker, backref='quotes')
    speaker_id = db.Column(db.Integer, db.ForeignKey(Speaker.id))
    published = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=1)

    def __init__(self, speaker_id, body, topic, user_id):
        self.speaker_id = speaker_id
        self.body = body
        self.topic = topic
        self.user_id = user_id

    def __repr__(self):
        return '<Quote on {}>'.format(self.topic)

    def get_voter_ids(self):
        select = quote_upvotes.select(quote_upvotes.c.quote_id == self.id)
        rs = db.engine.execute(select)
        ids = rs.fetchall()
        return ids

    def has_voted(self, user_id):
        select_votes = quote_upvotes.select(
                db.and_(
                    quote_upvotes.c.user_id == user_id,
                    quote_upvotes.c.quote_id == self.id
                )
        )
        rs = db.engine.execute(select_votes)
        return False if rs.rowcount == 0 else True

    def vote(self, user_id): # big props to codelucas for this flask-reddit thing thang. i am not skilled enough to do this alone.
        already_voted = self.has_voted(user_id)
        vote_status = None
        if not already_voted:
            db.engine.execute(
                    quote_upvotes.insert(),
                    user_id = user_id,
                    quote_id = self.id
            )
            self.votes += 1
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
            self.votes -= 1
            vote_status = False
        db.session.commit()
        return vote_status

quote_upvotes = db.Table('quote_upvotes',
        db.Column('user_id', db.Integer, db.ForeignKey(User.id)),
        db.Column('thread_id', db.Integer, db.ForeignKey(Quote.id))
)

db.create_all()
db.session.commit()
