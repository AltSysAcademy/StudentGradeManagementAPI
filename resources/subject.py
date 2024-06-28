from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt

from db import db
from models import SubjectModel
from schemas import SubjectSchema
from sqlalchemy.exc import SQLAlchemyError

from passlib.hash import pbkdf2_sha256


blp = Blueprint("subjects", __file__, description="Operations on subjects."
)

'''
@jwt_required(is_admin=True)
/subjects - GET ALL SUBJECTS
/subject/ - POST (CREATE SUBJECT)
/subject/<id> - GET (GET SUBJECT BY ID)
/subject/<id> - DELETE (DELETE SUBJECT BY ID)
/subject/<id>/students

/subject/<id>/student - GET (Get enrolled students on a subject)
'''