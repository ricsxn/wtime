import json
import re
from wtime_srv import db
from sqlalchemy.sql import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

#
# wtime_src common DB class
#

class wtime_srv_db:

    def __repr__(self):
        record = {
        }
        for col in [ r for r in dir(self) if not re.search('__', r) and not callable(getattr(self,r))]:
            record[col] = getattr(self,col)
        return json.dumps(record)

#
# Users Class
#

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(128),nullable=True)
    lastname = db.Column(db.String(128),nullable=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    hash = db.Column(db.String(256), nullable=False)
    created = db.Column(db.DateTime(), default=func.now())
    updated = db.Column(db.DateTime(), default=func.now(), onupdate=func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  

#
# wtime_srv Schema
#

class Badge(db.Model, wtime_srv_db):
    __tablename__ = 'badge'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), nullable=False, unique=True)
    created = db.Column(db.DateTime(), default=func.now())
    kind = db.Column(db.String(5), nullable=False, unique=True)
