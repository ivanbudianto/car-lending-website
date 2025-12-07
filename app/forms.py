# third-party imports
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_ckeditor import CKEditorField
from wtforms import StringField, SelectField, EmailField, PasswordField, IntegerField, FloatField, TextAreaField, FieldList, FormField, SubmitField, HiddenField
from wtforms.validators import DataRequired, InputRequired, Email, Length, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField, QueryRadioField
from flask_login import current_user
import re

# local imports
from .models import User
from .models import Car, CarTransmission, Division
from . import bcrypt


class RegisterForm(FlaskForm):
  name = StringField("Nama Lengkap", validators=[DataRequired(), Length(min=4, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  nip = StringField("Nomor Induk Pegawai", validators=[DataRequired(), Length(min=9, max=10, message="Kolom harus diisi 9 hingga 10 karakter.")])


  division = SelectField(
        'Seksi',  # This is the Label text SUKI, 
        choices=[
            ('1', 'Subbagian Umum dan Kepegawaian Internal'),
            ('2', 'Pengawas 1'),
            ('3', 'Pengawas 2'),
            ('4', 'Pengawas 3'),
            ('5', 'Pengawas 4'),
            ('6', 'Pengawas 5'),
            ('7', 'Pengawas 6'),
            ('8', 'Penjamin Kualitas Data'),
            ('9', 'Finance & Accounting'),
            ('10', 'Fungsional Pemeriksa Pajak 1'),
            ('11', 'Fungsional Pemeriksa Pajak 2'),
            ('12', 'Fungsional Pemeriksa Pajak 3'),
            ('13', 'Pemeriksaan, Penilaian, dan Penagihan'),
            ('14', 'Lainnya')
        ],
        validators=[DataRequired()]
    )

  password = PasswordField("Kata Sandi", validators=[DataRequired(), Length(min=8, max=128, message="Kata sandi harus memiliki panjang setidaknya 8 karakter.")])
  confirm = PasswordField("Konfirmasi Kata Sandi", validators=[DataRequired(), Length(min=8, max=128), EqualTo("password", message="Konfirmasi kata sandi tidak cocok.")])
  submit = SubmitField("Daftar")


  #  id = db.Column(db.Integer, primary_key=True)
  # status = db.Column(db.String(30), nullable=False)
  # role = db.Column(db.String(20), nullable=False, default="user")
  # _inserted_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
  # _updated_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

  def validate_nip(self, nip):
    user = User.query.filter_by(nip=nip.data).first()
    if user:
      raise ValidationError("NIP telah terdaftar pada sistem.")

class LoginForm(FlaskForm):
  nip = StringField("Nomor Induk Pegawai (NIP)", validators=[DataRequired(), Length(min=9, max=10, message="NIP yang Anda masukkan tidak valid.")], render_kw={"placeholder": "Masukkan NIP Anda disini"})
  password = PasswordField("",validators=[DataRequired(), Length(min=8, max=128)], render_kw={"placeholder": "Masukkan kata sandi Anda"})
  submit = SubmitField("Masuk")


class UserEditForm(FlaskForm):
  name = StringField("Nama Lengkap", validators=[DataRequired(), Length(min=4, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  nip = StringField("Nomor Induk Pegawai", validators=[DataRequired(), Length(min=9, max=10, message="Kolom harus diisi 9 hingga 10 karakter.")])
  division_id = QuerySelectField("Seksi", validators=[DataRequired()], query_factory=lambda: Division.query.all(), get_label="name", allow_blank=True, blank_text="Pilih Seksi")

  submit = SubmitField("Daftar")

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
  name = StringField("Nama/Jenis Mobil", validators=[DataRequired(), Length(min=4, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  license_plate = StringField("Plat Nomor", validators=[DataRequired(), Length(min=4, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  transmission_id = QuerySelectField("Jenis Transmisi", validators=[DataRequired()], query_factory=lambda: CarTransmission.query.all(), get_label="name", allow_blank=True, blank_text="Pilih Tipe Transmisi")

  image = FileField("Gambar", validators=[FileAllowed(["jpg", "jpeg", "png"], message="File yang Anda unggah tidak diperbolehkan. Silakan unggah file dalam format .jpg, .jpeg, atau .png.")])
  submit = SubmitField("Daftar")


class CarEditForm(FlaskForm):
  old_license_plate = HiddenField()
  name = StringField("Nama/Jenis Mobil", validators=[DataRequired(), Length(min=4, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  license_plate = StringField("Plat Nomor", validators=[DataRequired(), Length(min=4, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  transmission_id = QuerySelectField("Jenis Transmisi", validators=[DataRequired()], query_factory=lambda: CarTransmission.query.all(), get_label="name", allow_blank=True, blank_text="Pilih Tipe Transmisi")

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

  def validate_license_plate(self, license_plate):
    car = Car.query.filter(Car.license_plate==license_plate.data, Car.status != "Nonaktif").first()

    if car:
      cleaned_old_license_plate = re.sub(r"\s+", "", self.old_license_plate.data)
      cleaned_license_plate = re.sub(r"\s+", "", car.license_plate)

      if car and cleaned_license_plate != cleaned_old_license_plate:
        raise ValidationError("Plat nomor telah terdaftar pada sistem.")
  

class CarTransmissionForm(FlaskForm):
  name = StringField("Nama/Jenis Transmisi", validators=[DataRequired(), Length(min=4, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  submit = SubmitField("Tambahkan Data")

class CarTransmissionEditForm(FlaskForm):
  old_name = HiddenField()
  name = StringField("Nama Seksi (Resmi)", validators=[DataRequired(), Length(min=4, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  submit = SubmitField("Edit Data")

  def validate_name(self, name):
    transmission_obj = CarTransmission.query.filter(CarTransmission.name==name.data, CarTransmission.status != "Nonaktif").first()
    if transmission_obj:
      cleaned_old_name = re.sub(r"\s+", "", self.old_name.data)
      cleaned_name = re.sub(r"\s+", "", transmission_obj.name)
      if cleaned_name != cleaned_old_name:
        raise ValidationError("Nama/Jenis Transmisi telah terdaftar pada sistem.")
      


class DivisionForm(FlaskForm):
  code = StringField("Nama Seksi (Kode)", validators=[DataRequired(), Length(min=4, max=50, message="Kolom harus diisi 4 hingga 50 karakter.")])
  name = StringField("Nama Seksi (Resmi)", validators=[DataRequired(), Length(min=4, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  submit = SubmitField("Tambahkan Data")


class DivisionEditForm(FlaskForm):
  old_code = HiddenField()
  old_name = HiddenField()
  code = StringField("Nama Seksi (Kode)", validators=[DataRequired(), Length(min=4, max=50, message="Kolom harus diisi 4 hingga 50 karakter.")])
  name = StringField("Nama Seksi (Resmi)", validators=[DataRequired(), Length(min=4, max=100, message="Kolom harus diisi 4 hingga 100 karakter.")])
  submit = SubmitField("Edit Data")


  def validate_code(self, code):
    division_obj = Division.query.filter(Division.code==code.data, Division.status != "Nonaktif").first()
    if division_obj and division_obj.code != self.old_code.data:
      raise ValidationError("Kode seksi telah terdaftar pada sistem.")


  def validate_name(self, name):
    division_obj = Division.query.filter(Division.name==name.data, Division.status != "Nonaktif").first()

    if division_obj:
      cleaned_old_name = re.sub(r"\s+", "", self.old_name.data)
      cleaned_name = re.sub(r"\s+", "", division_obj.name)

      if division_obj and cleaned_name != cleaned_old_name:
        raise ValidationError("Nama seksi telah terdaftar pada sistem.")
    
