import datetime
from sqlalchemy.sql import func
from wtime_srv_db import db,\
                         User


class DB:

    error = None

    def __init__(self):
        pass

    def create_db(self):
        self.error = None
        try:
            db.create_all()
            db.session.commit()
            self.error = ''
        except Exception as e:
            self.error = '%s' % e
            print('%s' % self.error)

    @staticmethod
    def get_cols(cls):
      '''
        Return column names of the given table class name
      '''
      return [i for i in cls.__dict__.keys() if i[:1] != '_']

class Tables:

  error = None
  record = None
  records = []

  date_format = '%d/%m/%Y %H:%M'

  def str_to_date(self, str):
    if str is not None:
        return datetime.datetime.strptime(str, self.date_format)
    return None
  
  def select(self, id):
      self.record = None
      for r in self.records:
          if r.id == id:
            self.record = r
            break
      return self.record

  def update_values(self, values, skip_columns, date_columns=[]):
    try:
      for k in values.keys():
          if k in skip_columns + date_columns:
            continue
          setattr(self.record, k, values[k])
      if 'updated' in values.keys():
          self.record['updated'] = func.now()
      for dc in date_columns:
        if dc in values.keys() and self.str_to_date(values[dc]) is not None:
            setattr(self.record, dc, self.str_to_date(values[dc]))
    except Exception as e:
      self.error = '%s' % e
      print('%s' % self.error)
      raise Exception(self.error)

  def update(self, values, date_columns=[]):
    self.error = None
    try:
      skip_columns = [ 'dom_id', 'created', 'updated']
      self.update_values(values, skip_columns, date_columns)
      db.session.commit()
      self.error = ''
    except Exception as e:
      self.error = '%s' % e
      print('%s' % self.error)
      raise Exception(self.error)
    return

class User(Tables, User):

    pass
