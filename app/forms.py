# third-party imports
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_ckeditor import CKEditorField
from wtforms import StringField, SelectField, EmailField, PasswordField, IntegerField, FloatField, TextAreaField, FieldList, FormField, SubmitField, HiddenField
from wtforms.validators import DataRequired, InputRequired, Email, Length, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField, QueryRadioField
from flask_login import current_user
import re
from sqlalchemy import func, or_

# local imports
from .models import User
from .models import Car, CarTransmission, Division
from . import bcrypt


class RegisterForm(FlaskForm):
  name = StringField("Nama Lengkap", validators=[DataRequired(), Length(min=1, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  nip = StringField("Nomor Induk Pegawai", validators=[DataRequired(), Length(min=1, max=10, message="Kolom harus diisi 9 hingga 10 karakter.")])
  division_id = QuerySelectField("Seksi", validators=[DataRequired()], query_factory=lambda: Division.query.filter(Division.status!='Nonaktif'), get_label="name", allow_blank=True, blank_text="Pilih Seksi")
  password = PasswordField("Kata Sandi", validators=[DataRequired(), Length(min=1, max=128, message="Kata sandi harus memiliki panjang setidaknya 8 karakter.")])
  confirm = PasswordField("Konfirmasi Kata Sandi", validators=[DataRequired(), Length(min=1, max=128), EqualTo("password", message="Konfirmasi kata sandi tidak cocok.")])
  submit = SubmitField("Daftar")


  #  id = db.Column(db.Integer, primary_key=True)
  # status = db.Column(db.String(30), nullable=False)
  # role = db.Column(db.String(20), nullable=False, default="user")
  # _inserted_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  # _updated_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

  def validate_nip(self, nip):
    if len(nip.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
    cleaned_nip = re.sub(r"\s+", "", self.nip.data).lower()
    
    cleaned_db_nip = func.lower(func.replace(User.nip, " ", ""))
    user_obj = User.query.filter(
          cleaned_db_nip == cleaned_nip.lower().replace(" ", ""),
          User.status != "Nonaktif"
        ).first()
    if user_obj:
      raise ValidationError("NIP ini telah terdaftar pada sistem.")
    
  def validate_name(self, name):
    if len(name.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
  def validate_password(self, password):
    if len(password.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
  def validate_confirm(self, confirm):
    if len(confirm.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")

class LoginForm(FlaskForm):
  nip = StringField("Nomor Induk Pegawai (NIP)", validators=[DataRequired(), Length(min=9, max=10, message="NIP yang Anda masukkan tidak valid.")], render_kw={"placeholder": "Masukkan NIP Anda disini"})
  password = PasswordField("",validators=[DataRequired(), Length(min=8, max=128)], render_kw={"placeholder": "Masukkan kata sandi Anda"})
  submit = SubmitField("Masuk")


class UserEditForm(FlaskForm):
  name = StringField("Nama Lengkap", validators=[DataRequired(), Length(min=1, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  nip = StringField("Nomor Induk Pegawai", validators=[DataRequired(), Length(min=9, max=10, message="Kolom harus diisi 9 hingga 10 karakter.")])
  division_id = QuerySelectField("Seksi", validators=[DataRequired()], query_factory=lambda: Division.query.filter(Division.status!='Nonaktif'), get_label="name", allow_blank=True, blank_text="Pilih Seksi")

  submit = SubmitField("Daftar")

  def validate_name(self, name):
    if len(name.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")

class UserEditPasswordForm(FlaskForm):
  old_id = HiddenField()
  password = PasswordField("Kata Sandi Lama", validators=[DataRequired(), Length(min=8, max=128)])
  new_password = PasswordField("Kata Sandi Baru", validators=[DataRequired(), Length(min=8, max=128)])
  new_password_confirm = PasswordField("Konfirmasi Kata Sandi Baru", validators=[DataRequired(), Length(min=8, max=128), EqualTo("new_password", message="Konfirmasi password baru tidak cocok.")])

  submit = SubmitField("Daftar")

  def validate_password(self, password):
    user = User.query.filter(User.id==current_user.id, User.status != "Nonaktif").first()
    print(user.password)
    print(password.data)
    if not bcrypt.check_password_hash(user.password, '12341234'):
    # if bcrypt.check_password_hash(user.password, str(password.data)):
      raise ValidationError("Kata sandi lama salah.")






class CarForm(FlaskForm):
  name = StringField("Nama/Jenis Mobil", validators=[DataRequired(), Length(min=1, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  license_plate = StringField("Plat Nomor", validators=[DataRequired(), Length(min=1, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  transmission_id = QuerySelectField("Tipe Mobil", validators=[DataRequired()], query_factory=lambda: CarTransmission.query.filter(CarTransmission.status!='Nonaktif'), get_label="name", allow_blank=True, blank_text="Pilih Tipe Mobil")

  image = FileField("Gambar", validators=[FileAllowed(["jpg", "jpeg", "png"], message="File yang Anda unggah tidak diperbolehkan. Silakan unggah file dalam format .jpg, .jpeg, atau .png.")])
  submit = SubmitField("Daftar")

  def validate_name(self, name):
    if len(name.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
    # cleaned_name = re.sub(r"\s+", "", self.name.data).lower()
    
    # cleaned_db_name = func.lower(func.replace(Car.name, " ", ""))
    # car_obj = Car.query.filter(
    #       cleaned_db_name == cleaned_name.lower().replace(" ", ""),
    #       Car.status != "Nonaktif"
    #     ).first()
    # if car_obj:
    #   raise ValidationError("Plat nomor ini telah terdaftar pada sistem.")

    
  def validate_license_plate(self, license_plate):
    if len(license_plate.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
    cleaned_license_plate = re.sub(r"\s+", "", self.license_plate.data).lower()
    
    cleaned_db_license_plate = func.lower(func.replace(Car.license_plate, " ", ""))
    car_obj = Car.query.filter(
          cleaned_db_license_plate == cleaned_license_plate.lower().replace(" ", ""),
          Car.status != "Nonaktif"
        ).first()
    if car_obj:
      raise ValidationError("Plat nomor ini telah terdaftar pada sistem.")


class CarEditForm(FlaskForm):
  old_license_plate = HiddenField()
  name = StringField("Nama/Jenis Mobil", validators=[DataRequired(), Length(min=1, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  license_plate = StringField("Plat Nomor", validators=[DataRequired(), Length(min=1, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  transmission_id = QuerySelectField("Tipe Mobil", validators=[DataRequired()], query_factory=lambda: CarTransmission.query.filter(CarTransmission.status!='Nonaktif'), get_label="name", allow_blank=True, blank_text="Pilih Tipe Mobil")

  status_label = SelectField(
        'Status Mobil', 
        
        validators=[DataRequired()],
        choices=[
            ('Tersedia', 'Tersedia'),
            ('Perbaikan', 'Perbaikan'),
            ('Efisiensi', 'Efisiensi'),
            ('Dipinjam', 'Dipinjam'),
            ('Telah Dikembalikan', 'Telah Dikembalikan'),
        ]
    )
  
  image = FileField("Gambar", validators=[FileAllowed(["jpg", "jpeg", "png"], message="File yang Anda unggah tidak diperbolehkan. Silakan unggah file dalam format .jpg, .jpeg, atau .png.")])
  submit = SubmitField("Edit Data")


  def validate_name(self, name):
    if len(name.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")

  def validate_license_plate(self, license_plate):
    if len(license_plate.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
    cleaned_license_plate = re.sub(r"\s+", "", self.license_plate.data).lower()
    cleaned_old_license_plate = re.sub(r"\s+", "", self.old_license_plate.data).lower()
    cleaned_db_license_plate = func.lower(func.replace(Car.license_plate, " ", ""))

    car_obj = Car.query.filter(
        cleaned_db_license_plate == cleaned_license_plate.lower().replace(" ", ""),
        Car.status != "Nonaktif"
        ).first()
    if car_obj and (cleaned_license_plate == car_obj.license_plate.lower().replace(" ", "") and cleaned_old_license_plate != cleaned_license_plate):
      print(cleaned_license_plate, cleaned_old_license_plate, car_obj.license_plate.lower().replace(" ", ""))
      raise ValidationError("Plat nomor telah terdaftar pada sistem.")
  

class CarTransmissionForm(FlaskForm):
  name = StringField("Tipe Mobil", validators=[DataRequired(), Length(min=1, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  submit = SubmitField("Tambahkan Data")

  def validate_name(self, name):
    if len(name.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
    cleaned_name = re.sub(r"\s+", "", self.name.data).lower()
    
    cleaned_db_name = func.lower(func.replace(CarTransmission.name, " ", ""))
    car_transmission_obj = CarTransmission.query.filter(
          cleaned_db_name == cleaned_name.lower().replace(" ", ""),
          CarTransmission.status != "Nonaktif"
        ).first()
    if car_transmission_obj:
      raise ValidationError("Tipe ini telah terdaftar pada sistem.")
    


class CarTransmissionEditForm(FlaskForm):
  old_name = HiddenField()
  name = StringField("Tipe Mobil", validators=[DataRequired(), Length(min=1, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  submit = SubmitField("Edit Data")

  def validate_name(self, name):
    if len(name.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
    cleaned_name = re.sub(r"\s+", "", self.name.data).lower()
    cleaned_old_name = re.sub(r"\s+", "", self.old_name.data).lower()
    cleaned_db_name = func.lower(func.replace(CarTransmission.name, " ", ""))

    car_transmission_obj = CarTransmission.query.filter(
        cleaned_db_name == cleaned_name.lower().replace(" ", ""),
        CarTransmission.status != "Nonaktif"
        ).first()
    if car_transmission_obj and (cleaned_name == car_transmission_obj.name.lower().replace(" ", "") and cleaned_old_name != cleaned_name):
      raise ValidationError("Tipe mobil telah terdaftar pada sistem.")
      


class DivisionForm(FlaskForm):
  code = StringField("Nama Seksi (Kode)", validators=[DataRequired(), Length(min=1, max=50, message="Kolom harus diisi 4 hingga 50 karakter.")])
  name = StringField("Nama Seksi (Resmi)", validators=[DataRequired(), Length(min=1, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  submit = SubmitField("Tambahkan Data")

  def validate_name(self, name):
    if len(name.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
    cleaned_name = re.sub(r"\s+", "", self.name.data).lower()

    cleaned_db_name = func.lower(func.replace(Division.name, " ", ""))
    division_obj = Division.query.filter(
          cleaned_db_name == cleaned_name.lower().replace(" ", ""),
          Division.status != "Nonaktif"
        ).first()
    if division_obj:
      raise ValidationError("Nama seksi telah terdaftar pada sistem.")
    
  def validate_code(self, code):
    if len(code.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
    cleaned_code = re.sub(r"\s+", "", self.code.data).lower()
    
    cleaned_db_code = func.lower(func.replace(Division.code, " ", ""))
    division_obj = Division.query.filter(
          cleaned_db_code == cleaned_code.lower().replace(" ", ""),
          Division.status != "Nonaktif"
        ).first()
    if division_obj:
      raise ValidationError("Nama seksi telah terdaftar pada sistem.")




class DivisionEditForm(FlaskForm):
  old_code = HiddenField()
  old_name = HiddenField()
  code = StringField("Nama Seksi (Kode)", validators=[DataRequired(), Length(min=1, max=50, message="Kolom harus diisi 4 hingga 50 karakter.")])
  name = StringField("Nama Seksi (Resmi)", validators=[DataRequired(), Length(min=1, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  submit = SubmitField("Edit Data")


  def validate_code(self, code):
    if len(code.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")

    cleaned_code = re.sub(r"\s+", "", self.code.data).lower()
    cleaned_old_code = re.sub(r"\s+", "", self.old_code.data).lower()
    cleaned_db_code = func.lower(func.replace(Division.code, " ", ""))

    division_obj = Division.query.filter(
        cleaned_db_code == cleaned_code.lower().replace(" ", ""),
        Division.status != "Nonaktif"
        ).first()
    if division_obj and (cleaned_code == division_obj.code.lower().replace(" ", "") and cleaned_old_code != cleaned_code):
      print(cleaned_code, cleaned_old_code, division_obj.code.lower().replace(" ", ""))
      raise ValidationError("Kode seksi telah terdaftar pada sistem.")

  def validate_name(self, name):
    if len(name.data) < 4:
      raise ValidationError("Kolom ini diisi minimal 4 karakter.")
    
    cleaned_name = re.sub(r"\s+", "", self.name.data).lower()
    cleaned_old_name = re.sub(r"\s+", "", self.old_name.data).lower()
    cleaned_db_name = func.lower(func.replace(Division.name, " ", ""))

    division_obj = Division.query.filter(
        cleaned_db_name == cleaned_name.lower().replace(" ", ""),
        Division.status != "Nonaktif"
        ).first()
    if division_obj and (cleaned_name == division_obj.name.lower().replace(" ", "") and cleaned_old_name != cleaned_name):
      print(cleaned_name, cleaned_old_name, division_obj.name.lower().replace(" ", ""))
      raise ValidationError("Kode seksi telah terdaftar pada sistem.")
    
