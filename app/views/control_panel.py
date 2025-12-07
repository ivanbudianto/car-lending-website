# third-party imports
from flask import render_template, redirect, url_for, abort, flash, request
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.orm import joinedload
import datetime

# local imports
from . import control_panel_app
from .. import db, bcrypt
from ..models import User, Division
from ..forms import RegisterForm, LoginForm, UserEditForm, UserEditPasswordForm
from ..utils import send_password_reset, check_admin


@control_panel_app.route("/daftar", methods=["GET", "POST"])
def register():
  # if current_user.is_authenticated:
  #   return redirect(url_for("public_app.homepage"))

  form = RegisterForm()

  print(form.nip.data, form.name.data, form.division.data, form.password.data)

  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

    new_user = User(nip=form.nip.data, name=form.name.data, status="Active", division=form.division.data, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    flash(f"Akun baru dengan NIP {form.nip.data} telah berhasil dibuat.", "success")
    return redirect(url_for("control_panel_app.register"))
  else:
    print(form.nip.data, form.name.data)

  return render_template("control_panel/auth/register.html", title="Daftar - Development", form=form)

@control_panel_app.route("/masuk", methods=["GET", "POST"])
def login():
  if current_user.is_authenticated:
    return redirect(url_for("public_app.homepage"))

  form = LoginForm()

  if form.validate_on_submit():
    user = User.query.filter_by(nip=form.nip.data).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
      login_user(user)

      flash("Selamat Datang kembali. Anda telah berhasil masuk.", "success")
      return redirect(url_for("public_app.homepage"))
    else:
      flash("Anda gagal masuk. Periksa kembali kombinasi NIP dan password Anda.", "error")

  return render_template("control_panel/auth/login.html", title="Masuk - Development", form=form)


@control_panel_app.route("/lupa-password/<token>", methods=["GET", "POST"])
def reset_password(token):
  if current_user.is_authenticated:
    return redirect(url_for("public_app.homepage"))

  user = User.verify_reset_token(token)

  if user is None:
    flash("Token Anda tidak valid atau telah kedaluwarsa.")
    return redirect(url_for("control_panel_app.forgot_password"))

  form = ResetPasswordForm()

  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
    user.password = hashed_password

    db.session.commit()

    flash("Password Anda telah berhasil diperbarui. Harap ingat untuk menggunakannya untuk masuk berikutnya.")
    return redirect(url_for("control_panel_app.login"))

  return render_template("control_panel/auth/reset-password.html", title="Pengaturan Ulang Password - Development", form=form)



@control_panel_app.route("/pengguna", methods=["GET", "POST"])
@login_required
def user():
  check_admin()

  datas = User.query \
    .options(joinedload(User.division)) \
    .filter(User.status != 'Nonaktif') \
    .order_by(User._updated_date.desc())
  
  return render_template("control_panel/user/user.html", title="Daftar Wisata - Bondowoso Tourism", datas=datas)


@control_panel_app.route("/pengguna/<id>", methods=["GET", "POST"])
def profile(id):
  user = User.query.filter_by(id=id).first_or_404()
  return render_template("control_panel/account/profile_form.html", title=f"{user.name} - Development", user=user)


@control_panel_app.route("/pengguna/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_user(id):
  check_admin()
  user = User.query.filter_by(id=id).first_or_404()
  form = UserEditForm()

  if form.validate_on_submit():
    user.nip = form.nip.data
    user.name = form.name.data
    user.division_id = form.division_id.data.id

    user._inserted_date = user._inserted_date
    user._updated_date = datetime.datetime.now()

    db.session.commit()

    flash("Data pengguna telah berhasil diedit.", "success")
    return redirect(url_for("control_panel_app.user", id=current_user.id))
    
  
  elif request.method == "GET":
    form.name.data = user.name
    form.nip.data = user.nip
    form.division_id.data = Division.query.filter_by(id=user.division_id).first_or_404()


  return render_template("control_panel/user/user_edit-form-admin.html", title="Edit Profile - Development", user=user, form=form)


@control_panel_app.route("/pengguna/ubah-kata-sandi/<id>", methods=["GET", "POST"])
@login_required
def edit_password(id):
  
  user = User.query.filter_by(id=id).first_or_404()
  if current_user.is_anonymous or str(current_user.id) != str(id):
    abort(403)
  
  form = UserEditPasswordForm()

  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
    user.password = hashed_password

    db.session.commit()

    flash("Kata sandi berhasil diubah.")
    return redirect(url_for("public_app.homepage", id=current_user.id))
  
  elif request.method == "GET":
    form.old_id.data = current_user.id

  return render_template("control_panel/user/user_edit-password-form.html", title="Edit Profile - Development", user=user, form=form)
    


@control_panel_app.route("/keluar")
@login_required
def logout():
  logout_user()

  flash("Anda telah berhasil keluar. Selamat tinggal dan sampai jumpa lagi!", "success")
  return redirect(url_for("control_panel_app.login"))