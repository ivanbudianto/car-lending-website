from flask import Blueprint

control_panel_app = Blueprint("control_panel_app", __name__)
public_app = Blueprint("public_app", __name__)

from . import control_panel, public