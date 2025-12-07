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
from ..models import UsageHelp, Criteria, SubCriteria, LocationPoint, TourType, TourList, TourDistance
from ..models import Car, CarTransmission, Division
from ..forms import UsageHelpForm, CriteriaForm, SubCriteriaForm, LocationPointForm, TourTypeForm, TourListForm, TourRecommendation1Form, TourRecommendation2Form, DistanceForm
from ..forms import CarForm, CarEditForm, DivisionForm, DivisionEditForm, CarTransmissionForm, CarTransmissionEditForm
from ..utils import check_admin, save_resized_image, process_input_list_based_on_weight


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
  datas = Car.query.filter(Car.status != 'Nonaktif').order_by(Car._updated_date.desc())
  # Use .options(joinedload(...)) to fetch the related transmission_type data
  datas = Car.query \
    .options(joinedload(Car.transmission_type)) \
    .filter(Car.status != 'Nonaktif') \
    .order_by(Car._updated_date.desc())
    
  return render_template("public/services/car/car.html", title="Daftar Wisata - Bondowoso Tourism", datas=datas)


@public_app.route("/layanan/daftar-wisata/<id>", methods=["GET", "POST"])
@login_required
def tour_list_detail(id):
  data = TourList.query.filter_by(id=id).first_or_404()
  facility = SubCriteria.query.filter_by(criteria_id=2, value=data.facility).first_or_404()
  distance = TourDistance.query.filter_by(tour_list_id=id).first_or_404()
  infrastructure = SubCriteria.query.filter_by(criteria_id=4, value=data.infrastructure).first_or_404()
  transportation_access = SubCriteria.query.filter_by(criteria_id=5, value=data.transportation_access).first_or_404()
  return render_template("public/services/tour_list/tour-list_detail.html", title=f"{data.name} - Bondowoso Tourism", data=data, distance=distance, facility=facility, infrastructure=infrastructure, transportation_access=transportation_access)


@public_app.route("/layanan/mobil/tambah", methods=["GET", "POST"])
@login_required
def create_car():
  check_admin()

  form = CarForm()
  if form.validate_on_submit():
    if form.image.data:
      image = save_resized_image(form.image.data, 1280, 720, "tour_list")
      new_car = Car(name=form.name.data, license_plate=form.license_plate.data, transmission_id=int(form.transmission_id.data.id), status="Tersedia", image=image)
      # new_tour_list = Car(name=form.name.data, license_plate=form.license_plate.data, transmission_id=form.transmission_id.data, image=image, user=current_user)
    else:
      new_car = Car(name=form.name.data, license_plate=form.license_plate.data, transmission_id=int(form.transmission_id.data.id), status="Tersedia")


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

    data.name = data.name if form.name.data is None else form.name.data
    data.license_plate = data.license_plate if form.license_plate.data is None else form.license_plate.data
    data.transmission_id = data.transmission_id if form.transmission_id.data.id is None else form.transmission_id.data.id
    data.status = data.status if form.status_label.data is None else form.status_label.data

    data._inserted_date = data._inserted_date
    data._updated_date = datetime.datetime.now()
    db.session.commit()

    flash("Data telah berhasil diedit!", "success")
    return redirect(url_for("public_app.car"))
  
  elif request.method == "GET":
    form.name.data = data.name
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

@public_app.route("/layanan/transmisi-mobil", methods=["GET", "POST"])
@login_required
def car_transmission():
  datas = CarTransmission.query.filter(CarTransmission.status != 'Nonaktif').order_by(CarTransmission.id.asc())
  return render_template("public/services/car_transmission/car-transmission.html", title="Daftar Wisata - Bondowoso Tourism", datas=datas)


@public_app.route("/layanan/transmisi-mobil/tambah", methods=["GET", "POST"])
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

@public_app.route("/layanan/transmisi-mobil/edit/<id>", methods=["GET", "POST"])
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

@public_app.route("/layanan/transmisi-mobil/hapus/<id>", methods=["GET", "POST"])
@login_required
def delete_car_transmission(id):
  check_admin()
  data = CarTransmission.query.filter_by(id=id).first_or_404()
  data.status = "Nonaktif"
  db.session.commit()

  flash("Data telah berhasil dihapus!", "success")
  return redirect(url_for("public_app.car_transmission"))


















@public_app.route("/layanan/rekomendasi-wisata/sub-kriteria", methods=["GET", "POST"])
@login_required
def tour_recommendation_sub_criteria():
  if not session.get("form1_filled"):
    return redirect(url_for("public_app.tour_recommendation"))

  form = TourRecommendation2Form()

  if form.validate_on_submit():
    location_point = session.get("location_point")
    tour_type = session.get("tour_type")
    ticket = str(form.ticket.data)
    facility = str(form.facility.data)
    distance = str(form.distance.data)
    infrastructure = str(form.infrastructure.data)
    transportation_access = str(form.transportation_access.data)

    criteria = Criteria.query.all()

    avg_weight = [criteria.weight for criteria in criteria]
    weight_type = [1 if criteria.attribute == "Cost" else 2 for criteria in criteria]

    tours_and_distances = db.session.query(
      TourList.id,
      TourList.name,
      TourList.ticket,
      TourList.facility,
      TourList.infrastructure,
      TourList.transportation_access,
      TourDistance.distance
    ).join(
      TourDistance,
      TourList.id == TourDistance.tour_list_id
    ).filter(
      TourList.tour_type_id == tour_type,
      TourDistance.location_point_id == location_point
    ).all()

    facility_subcriteria = SubCriteria.query.filter_by(criteria_id=2, value=facility).first()
    infrastructure_subcriteria = SubCriteria.query.filter_by(criteria_id=4, value=infrastructure).first()
    transportation_access_subcriteria = SubCriteria.query.filter_by(criteria_id=5, value=transportation_access).first()

    ticket_category = 0
    distance_category = 0

    list_ids = []
    list_names = []
    filtered_np_list = []

    for tour in tours_and_distances:
      if tour.ticket == 0:
        ticket_category = 1
      elif tour.ticket <= 5000:
        ticket_category = 2
      elif tour.ticket <= 10000:
        ticket_category = 3
      elif tour.ticket > 10000:
        ticket_category = 4

      if tour.distance <= 10:
        distance_category = 1
      elif tour.distance <= 20:
        distance_category = 2
      elif tour.distance <= 30:
        distance_category = 3
      elif tour.distance <= 40:
        distance_category = 4
      elif tour.distance <= 50:
        distance_category = 5
      elif tour.distance > 50:
        distance_category = 6

      if ticket_category > int(ticket) or tour.facility < int(facility_subcriteria.value) or int(tour.infrastructure) < int(infrastructure_subcriteria.value) or tour.transportation_access < int(transportation_access_subcriteria.value) or distance_category > int(distance):
        continue

      list_ids.append(tour.id)
      list_names.append(tour.name)
      filtered_np_list.append([
        float(ticket_category),
        float(tour.facility),
        float(distance_category),
        float(tour.infrastructure),
        float(tour.transportation_access)
      ])

    filtered_np_array = np.array(filtered_np_list)

    if filtered_np_array.size == 0:
      return render_template("public/services/tour_recommendation/tour-recommendation_result.html", title="Rekomendasi Wisata - Bondowoso Tourism", result=[], error_message="Wisata yang Anda cari tidak ditemukan.")

    if len(filtered_np_array) == 1:
      preference_metric = np.array([1.0])
    else:
      preference_metric = process_input_list_based_on_weight(filtered_np_array, np.array(avg_weight), weight_type)

    paired_list = list(zip(preference_metric, list_names, list_ids))

    sorted_paired_list = sorted(paired_list, reverse=True)

    top_3_paired_list = sorted_paired_list[:3]

    result = [{"ranking": str(rank), "score": str(int(value * 100)), "tour_object": name, "action": id} for rank, (value, name, id) in enumerate(top_3_paired_list, start=1)]

    session.pop("location_point", None)
    session.pop("ticket_price", None)
    session.pop("form1_filled", None)

    return render_template("public/services/tour_recommendation/tour-recommendation_result.html", title="Rekomendasi Wisata - Bondowoso Tourism", result=result)

  return render_template("public/services/tour_recommendation/tour-recommendation-2.html", title="Rekomendasi Wisata - Bondowoso Tourism", form=form)