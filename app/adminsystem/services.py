from ninja.errors import HttpError
from http import HTTPStatus
from app.microtiks.models import Microtik


def view_all_microtik():
    return Microtik.objects.select_related("users").all()

