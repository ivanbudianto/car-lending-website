# third-party imports
import numpy as np
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from wtforms import FieldList, FormField
from sqlalchemy.orm import joinedload
import datetime

# local imports
from . import public_app
from .. import db
from ..models import Car, CarTransmission, CarModel, Division, CarMaintenance
from ..forms import CarForm, CarEditForm, DivisionForm, DivisionEditForm, CarTransmissionForm, CarTransmissionEditForm, CarModelForm, CarModelEditForm, CarMaintenanceForm, CarMaintenanceEditForm
from ..utils import check_admin, save_resized_image, process_input_list_based_on_weight


def check_car_realtime_status(cars):
  now = datetime.datetime.now()
  for car in cars:
      car.realtime_status = (
          "Maintenance"
          if any(maintenance.start_date <= now <= maintenance.end_date for maintenance in car.maintenances)
          else car.status
      )
  return cars

# Homepage routes

@public_app.route("/", methods=["GET", "POST"])
def homepage():
  return render_template("public/index.html", title="Bondowoso Tourism")

# About routes

@public_app.route("/tentang", methods=["GET", "POST"])
def about():
  return render_template("public/about/about.html", title="Tentang - Bondowoso Tourism")

# Services routes

@public_app.route("/layanan", methods=["GET", "POST"])
@login_required
def services():
  return render_template("public/services/services.html", title="Layanan - Bondowoso Tourism")


# Tour List routes

@public_app.route("/layanan/mobil", methods=["GET", "POST"])
@login_required
def car():

  datas = Car.query \
    .options(joinedload(Car.transmission)) \
    .options(joinedload(Car.model)) \
    .options(joinedload(Car.maintenances)) \
    .filter(Car.status != 'Nonaktif') \
    .order_by(Car._updated_date.desc()) \
    .all()
  
  
  datas = check_car_realtime_status(datas)  
  return render_template("public/services/car/car.html", title="Daftar Wisata - Bondowoso Tourism", datas=datas)

@public_app.route("/layanan/mobil/tambah", methods=["GET", "POST"])
@login_required
def create_car():
  check_admin()

  form = CarForm()
  if form.validate_on_submit():
    if form.image.data:
      image = save_resized_image(form.image.data, 1280, 720, "tour_list")
      new_car = Car(model_id=int(form.model_id.data.id), license_plate=form.license_plate.data, transmission_id=int(form.transmission_id.data.id), status="Aktif", image=image, _updated_by=current_user.id)
      # new_tour_list = Car(name=form.name.data, license_plate=form.license_plate.data, transmission_id=form.transmission_id.data, image=image, user=current_user)
    else:
      new_car = Car(model_id=int(form.model_id.data.id), license_plate=form.license_plate.data, transmission_id=int(form.transmission_id.data.id), status="Aktif", _updated_by=current_user.id)


    db.session.add(new_car)
    db.session.commit()

    # for distance_form in form.distances:
    #   distance = TourDistance(tour_list_id=new_tour_list.id, location_point_id=distance_form.location_point.data.id, distance=distance_form.distance.data)
    #   db.session.add(distance)

    db.session.commit()

    flash("Data telah berhasil ditambahkan!", "success")
    return redirect(url_for("public_app.car"))

  return render_template("public/services/car/car_form.html", title="Tambah Daftar Wisata - Bondowoso Tourism", form=form, operation="Tambah")

@public_app.route("/layanan/mobil/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_car(id):
  check_admin()
  data = Car.query.filter_by(id=id).first_or_404()
  form = CarEditForm()

  if form.validate_on_submit():

    if form.image.data:
      image = save_resized_image(form.image.data, 1280, 720, "tour_list")
      data.image = image

    data.model_id = data.model_id if form.model_id.data.id is None else form.model_id.data.id
    data.license_plate = data.license_plate if form.license_plate.data is None else form.license_plate.data
    data.transmission_id = data.transmission_id if form.transmission_id.data.id is None else form.transmission_id.data.id
    data.status = data.status if form.status_label.data is None else form.status_label.data

    data._inserted_date = data._inserted_date
    data._updated_date = datetime.datetime.now()
    db.session.commit()

    flash("Data telah berhasil diedit!", "success")
    return redirect(url_for("public_app.car"))
  
  elif request.method == "GET":
    form.model_id.data = CarModel.query.filter_by(id=data.model_id).first_or_404()
    form.license_plate.data = data.license_plate
    form.transmission_id.data = CarTransmission.query.filter_by(id=data.transmission_id).first_or_404()
    form.status_label.data = data.status
    form.old_license_plate.data = data.license_plate

  return render_template("public/services/car/car_edit-form.html", title="Edit Daftar Wisata - Bondowoso Tourism", form=form, operation="Edit")

@public_app.route("/layanan/mobil/hapus/<id>", methods=["GET", "POST"])
@login_required
def delete_tour_list(id):
  check_admin()
  data = Car.query.filter_by(id=id).first_or_404()
  data.status = "Nonaktif"
  db.session.commit()

  flash("Data telah berhasil dihapus!", "success")
  return redirect(url_for("public_app.car"))






# Divisions Routes

@public_app.route("/layanan/seksi", methods=["GET", "POST"])
@login_required
def division():
  datas = Division.query.filter(Division.status != 'Nonaktif').order_by(Division.id.asc())
  # Use .options(joinedload(...)) to fetch the related transmission_type data
  return render_template("public/services/division/division.html", title="Daftar Wisata - Bondowoso Tourism", datas=datas)


@public_app.route("/layanan/seksi/tambah", methods=["GET", "POST"])
@login_required
def create_division():
  check_admin()

  form = DivisionForm()
  if form.validate_on_submit():
    new_division = Division(code=form.code.data, name=form.name.data, status="Aktif")

    db.session.add(new_division)
    db.session.commit()

    flash("Data telah berhasil ditambahkan!", "success")
    return redirect(url_for("public_app.division"))

  return render_template("public/services/division/division_form.html", title="Tambah Daftar Wisata - Bondowoso Tourism", form=form, operation="Tambah")

@public_app.route("/layanan/seksi/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_division(id):
  check_admin()
  data = Division.query.filter_by(id=id).first_or_404()

  form = DivisionEditForm()

  if form.validate_on_submit():

    data.code = data.code if form.code.data is None else form.code.data
    data.name = data.name if form.name.data is None else form.name.data

    data._inserted_date = data._inserted_date
    data._updated_date = datetime.datetime.now()
    db.session.commit()

    flash("Data telah berhasil diedit!", "success")
    return redirect(url_for("public_app.division"))
  
  elif request.method == "GET":
    form.code.data = data.code
    form.name.data = data.name
    
    form.old_code.data = data.code
    form.old_name.data = data.name

  return render_template("public/services/division/division_edit-form.html", title="Edit Daftar Wisata - Bondowoso Tourism", form=form, operation="Edit")

@public_app.route("/layanan/seksi/hapus/<id>", methods=["GET", "POST"])
@login_required
def delete_division(id):
  check_admin()
  data = Division.query.filter_by(id=id).first_or_404()
  data.status = "Nonaktif"
  db.session.commit()

  flash("Data telah berhasil dihapus!", "success")
  return redirect(url_for("public_app.division"))



# Car Transmissions Routes

@public_app.route("/layanan/tipe-mobil", methods=["GET", "POST"])
@login_required
def car_transmission():
  datas = CarTransmission.query.filter(CarTransmission.status != 'Nonaktif').order_by(CarTransmission.id.asc())
  return render_template("public/services/car_transmission/car-transmission.html", title="Daftar Wisata - Bondowoso Tourism", datas=datas)


@public_app.route("/layanan/tipe-mobil/tambah", methods=["GET", "POST"])
@login_required
def create_car_transmission():
  check_admin()

  form = CarTransmissionForm()
  if form.validate_on_submit():
    new_car_transmission = CarTransmission(name=form.name.data, status="Aktif")

    db.session.add(new_car_transmission)
    db.session.commit()

    flash("Data telah berhasil ditambahkan!", "success")
    return redirect(url_for("public_app.car_transmission"))

  return render_template("public/services/car_transmission/car-transmission_form.html", title="Tambah Daftar Wisata - Bondowoso Tourism", form=form, operation="Tambah")

@public_app.route("/layanan/tipe-mobil/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_car_transmission(id):
  check_admin()
  data = CarTransmission.query.filter_by(id=id).first_or_404()
  form = CarTransmissionEditForm()

  if form.validate_on_submit():
    data.name = data.name if form.name.data is None else form.name.data

    data._inserted_date = data._inserted_date
    data._updated_date = datetime.datetime.now()
    db.session.commit()

    flash("Data telah berhasil diedit!", "success")
    return redirect(url_for("public_app.car_transmission"))
  
  elif request.method == "GET":
    form.name.data = data.name
    form.old_name.data = data.name

  return render_template("public/services/car_transmission/car-transmission_edit-form.html", title="Edit Daftar Wisata - Bondowoso Tourism", form=form, operation="Edit")

@public_app.route("/layanan/tipe-mobil/hapus/<id>", methods=["GET", "POST"])
@login_required
def delete_car_transmission(id):
  check_admin()
  data = CarTransmission.query.filter_by(id=id).first_or_404()
  data.status = "Nonaktif"
  db.session.commit()

  flash("Data telah berhasil dihapus!", "success")
  return redirect(url_for("public_app.car_transmission"))



# Car Types Routes

@public_app.route("/layanan/jenis-mobil", methods=["GET", "POST"])
@login_required
def car_model():
  datas = CarModel.query.filter(CarModel.status != 'Nonaktif').order_by(CarModel.id.asc())
  return render_template("public/services/car_model/car-model.html", title="Daftar Wisata - Bondowoso Tourism", datas=datas)


@public_app.route("/layanan/jenis-mobil/tambah", methods=["GET", "POST"])
@login_required
def create_car_model():
  check_admin()

  form = CarModelForm()
  if form.validate_on_submit():
    new_car_model = CarModel(name=form.name.data, status="Aktif", _updated_by=current_user.id)

    db.session.add(new_car_model)
    db.session.commit()

    flash("Data telah berhasil ditambahkan!", "success")
    return redirect(url_for("public_app.car_model"))

  return render_template("public/services/car_model/car-model_form.html", title="Tambah Daftar Wisata - Bondowoso Tourism", form=form, operation="Tambah")

@public_app.route("/layanan/jenis-mobil/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_car_model(id):
  check_admin()
  data = CarModel.query.filter_by(id=id).first_or_404()
  form = CarModelEditForm()

  if form.validate_on_submit():
    data.name = data.name if form.name.data is None else form.name.data

    data._inserted_date = data._inserted_date
    data._updated_date = datetime.datetime.now()
    db.session.commit()

    flash("Data telah berhasil diedit!", "success")
    return redirect(url_for("public_app.car_model"))
  
  elif request.method == "GET":
    form.name.data = data.name
    form.old_name.data = data.name

  return render_template("public/services/car_model/car-model_edit-form.html", title="Edit Daftar Wisata - Bondowoso Tourism", form=form, operation="Edit")

@public_app.route("/layanan/jenis-mobil/hapus/<id>", methods=["GET", "POST"])
@login_required
def delete_car_model(id):
  check_admin()
  data = CarModel.query.filter_by(id=id).first_or_404()
  data.status = "Nonaktif"
  db.session.commit()

  flash("Data telah berhasil dihapus!", "success")
  return redirect(url_for("public_app.car_model"))


@public_app.route("/layanan/maintenance-mobil", methods=["GET", "POST"])
@login_required
def car_maintenance():
  check_admin()

  datas = (
    CarMaintenance.query
        .options(
            joinedload(CarMaintenance.car).joinedload(Car.transmission),
            joinedload(CarMaintenance.car).joinedload(Car.model),
        )
        .join(CarMaintenance.car)
        .filter(Car.status != 'Nonaktif')
        .order_by(Car._updated_date.desc())
    )
  
  return render_template("public/services/car_maintenance/car-maintenance.html", title="Daftar Wisata - Bondowoso Tourism", datas=datas)

@public_app.route("/layanan/maintenance-mobil/tambah", methods=["GET", "POST"])
@login_required
def create_car_maintenance():
  check_admin()

  form = CarMaintenanceForm()

  cars = Car.query \
    .options(joinedload(Car.transmission)) \
    .options(joinedload(Car.model)) \
    .filter(Car.status != 'Nonaktif') \
    .order_by(Car._updated_date.desc())
  form.set_car_choices(cars)


  if form.validate_on_submit():
    new_car_maintenance = CarMaintenance(car_id=int(form.car.data), start_date=form.start_date.data, end_date=form.end_date.data, status="Aktif", _updated_by=current_user.id)

    db.session.add(new_car_maintenance)
    db.session.commit()

    flash("Data telah berhasil ditambahkan!", "success")
    return redirect(url_for("public_app.car"))

  return render_template("public/services/car_maintenance/car-maintenance_form.html", title="Tambah Daftar Wisata - Bondowoso Tourism", form=form, operation="Tambah")


@public_app.route("/layanan/maintenance-mobil/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_car_maintenance(id):
  check_admin()
  data = CarMaintenance.query.filter_by(id=id).first_or_404()
  form = CarMaintenanceEditForm()

  cars = Car.query \
    .options(joinedload(Car.transmission)) \
    .options(joinedload(Car.model)) \
    .filter(Car.status != 'Nonaktif') \
    .order_by(Car._updated_date.desc()) \
    .all()
  form.set_car_choices(cars)

  if form.validate_on_submit():

    data.car_id = data.car_id if form.car.data is None else form.car.data
    data.start_date = data.start_date if form.start_date.data is None else form.start_date.data
    data.end_date = data.end_date if form.end_date.data is None else form.end_date.data
    db.session.commit()

    flash("Data telah berhasil diedit!", "success")
    return redirect(url_for("public_app.car_maintenance"))
  
  elif request.method == "GET":
    form.car.data = data.car_id
    form.start_date.data = data.start_date
    form.end_date.data = data.end_date

  return render_template("public/services/car_maintenance/car-maintenance_edit-form.html", title="Tambah Daftar Wisata - Bondowoso Tourism", form=form, operation="Edit")


