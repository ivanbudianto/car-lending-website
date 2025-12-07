# third-party imports
import os, secrets, math
import numpy as np
from PIL import Image
from flask import url_for, abort, current_app
from flask_mail import Message
from flask_login import current_user


# local imports
from . import mail
from .models import User


# function to check if the user is an admin
def check_admin():
  if not current_user.role.lower() == "admin":
    abort(403)

# function to send a password reset message via email
def send_password_reset(user):
  token = user.get_reset_token()
  message = Message("Password reset request", sender="intellicrop@gmail.com", recipients=[user.email])
  message.body = f'''Hello, {user.name}\n \nTo reset your password, visit the following link:\n{url_for("control_panel_app.reset_password", token=token, _external=True)}\n \nIf you did not make this request, please disregard this email, and no changes will be made.'''
  mail.send(message)

# function to save a resized image in a directory
def save_resized_image(input, width, height, path):
  if input:
    upload_dir = os.path.join(current_app.root_path, "static/media/uploads", path)
    if not os.path.exists(upload_dir):
      os.makedirs(upload_dir)

    random_hex = secrets.token_hex(8)
    _, image_ext = os.path.splitext(input.filename)
    image_fn = f"{random_hex}{image_ext}"
    image_path = os.path.join(upload_dir, image_fn)

    image = Image.open(input)
    image.thumbnail((width, height))
    image.save(image_path)

    return image_fn

def process_input_list_based_on_weight(input_data, avg_weight, weight_type):
  # count the length for further process
  len_options = len(input_data)
  len_criteria = len(input_data[0])

  # get the powered input
  powered_input_data = [
    [input_data[row][col] ** 2 for col in range(len_criteria)]
    for row in range(len_options)
  ]

  # get the transposed data for denom
  transposed_data = zip(*powered_input_data)
  denominator_ex = [np.round(math.sqrt(sum(column)), 5) for column in transposed_data]

  # normalize the input
  normalized_input_data = [
    [np.round(input_data[row][col] / denominator_ex[col], 5) for col in range(len_criteria)]
    for row in range(len_options)
  ]

  # times the normalized data with the weight
  weighted_normalized_input_data = [
    [np.round(normalized_input_data[row][col] * avg_weight[col], 5) for col in range(len_criteria)]
    for row in range(len_options)
  ]

  # transpose the value
  transposed_weighted_normalized_input_data = np.transpose(weighted_normalized_input_data)

  # get the minmax value of the columns
  min_values_per_column = []
  max_values_per_column = []

  for row in range(len(transposed_weighted_normalized_input_data)):
    min_val = np.min(transposed_weighted_normalized_input_data[row])
    max_val = np.max(transposed_weighted_normalized_input_data[row])

    if weight_type[row] == 1:
      max_values_per_column.append(min_val)
      min_values_per_column.append(max_val)

    elif weight_type[row] == 2:
      max_values_per_column.append(max_val)
      min_values_per_column.append(min_val)

  # power the value after substracting and adding the value
  powered_min_value = [
    [round(((max_values_per_column[col] - weighted_normalized_input_data[row][col]) ** 2), 5) for col in range(len_criteria)]
    for row in range(len_options)
  ]

  powered_max_value = [
    [round(((weighted_normalized_input_data[row][col] - min_values_per_column[col]) ** 2), 5) for col in range(len_criteria)]
    for row in range(len_options)
  ]

  # get the di+ and di- score
  di_plus_points = [np.round(math.sqrt(sum(column)) ,5) for column in powered_min_value]
  di_minus_points = [np.round(math.sqrt(sum(column)) ,5) for column in powered_max_value]

  # calculate the preference list
  preference_list = [np.round(di_minus_points[i] / (di_minus_points[i] + di_plus_points[i]) ,2) for i in range(len_options)]

  return preference_list