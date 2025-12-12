# third-party imports
from flask import current_app
from flask_login import UserMixin, current_user
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# local imports
from . import db, login_manager


# set up user_loader
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


class User(UserMixin, db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  nip = db.Column(db.String(20), nullable=False)
  division_id = db.Column(db.Integer, db.ForeignKey('divisions.id'), nullable=False)
  status = db.Column(db.String(30), nullable=False)
  role = db.Column(db.String(20), nullable=False, default="user")
  password = db.Column(db.String(128), nullable=False)
  _inserted_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  _updated_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

  def get_reset_token(self, expires_sec=1800):
    serial = Serializer(current_app.config["SECRET_KEY"], expires_sec)
    return serial.dumps({"user_id": self.id}).decode("utf-8")

  @staticmethod
  def verify_reset_token(token):
    serial = Serializer(current_app.config["SECRET_KEY"])
    try:
      user_id = serial.loads(token)["user_id"]
    except:
      return None
    return User.query.get(user_id)

  def __repr__(self):
    return f"{self.id}"
  

class Division(UserMixin, db.Model):
  __tablename__ = "divisions"

  id = db.Column(db.Integer, primary_key=True)
  code = db.Column(db.String(30), nullable=False)
  name = db.Column(db.String(100), nullable=False)
  status = db.Column(db.String(30), nullable=False)
  _inserted_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  _updated_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

  users = db.relationship('User', backref='division', lazy=True)

  def __repr__(self):
    return f"{self.id}"
  

class Car(db.Model):
  __tablename__ = "cars"

  id = db.Column(db.Integer, primary_key=True)
  model_id = db.Column(db.Integer, db.ForeignKey('car_models.id'), nullable=False)
  license_plate = db.Column(db.String(15), nullable=False)
  transmission_id = db.Column(db.Integer, db.ForeignKey('car_transmissions.id'), nullable=False)
  image = db.Column(db.String(128), nullable=True)
  status = db.Column(db.String(30), nullable=False)
  _inserted_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  _updated_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  _updated_by = db.Column(db.Integer, nullable=False, default=999)

  car_maintenances = db.relationship('CarMaintenance', backref='car', lazy=True)

  # transmission = db.relationship("CarTransmission", back_populates="car_transmission")
  # distances = db.relationship("TourDistance", backref="tour_list", lazy=True) # relationship to distances

  def __repr__(self):
    return f"{self.id}"
  

class CarTransmission(db.Model):
  __tablename__ = "car_transmissions"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  status = db.Column(db.String(30), nullable=False)
  _inserted_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  _updated_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

  cars = db.relationship('Car', backref='transmission', lazy=True)

  # tour_type = db.relationship("TourType", back_populates="tour_list")
  # distances = db.relationship("TourDistance", backref="tour_list", lazy=True) # relationship to distances

  def __repr__(self):
    return f"{self.id}"
  

class CarModel(db.Model):
  __tablename__ = "car_models"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  status = db.Column(db.String(30), nullable=False)
  _inserted_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  _updated_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  _updated_by = db.Column(db.Integer, nullable=False, default=999)

  cars = db.relationship('Car', backref='model', lazy=True)

  # tour_type = db.relationship("TourType", back_populates="tour_list")
  # distances = db.relationship("TourDistance", backref="tour_list", lazy=True) # relationship to distances

  def __repr__(self):
    return f"{self.id}"


class CarMaintenance(db.Model):
  __tablename__ = "car_maintenances"

  id = db.Column(db.Integer, primary_key=True)
  car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
  start_date = db.Column(db.DateTime, nullable=False)
  end_date = db.Column(db.DateTime, nullable=False)
  status = db.Column(db.String(30), nullable=False)
  _inserted_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  _updated_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  _updated_by = db.Column(db.Integer, nullable=False, default=999)

  car_maintenances = db.relationship('Car', backref='maintenances', lazy=True)

  # transmission = db.relationship("CarTransmission", back_populates="car_transmission")
  # distances = db.relationship("TourDistance", backref="tour_list", lazy=True) # relationship to distances