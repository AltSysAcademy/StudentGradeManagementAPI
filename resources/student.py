from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt

from db import db
from models import StudentModel, BlocklistModel
from schemas import StudentSchema, StudentLoginSchema, GradeSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

from passlib.hash import pbkdf2_sha256
from blocklist import BLOCKLIST


blp = Blueprint("students", __file__, description="Operations on students."
)

'''
/login     - POST   (Generate access, refresh)
/logout    - POST   (Revoke access token)
/refresh   - POST   (Generate non-fresh token)
/register  - POST   (Create a new student model)

/student - GET (Student info)
/student - DELETE (Delete account)

/student/subject/<id> - GET (Get subject info by ID)
/student/subject/<id> - POST (Enroll to a subject by ID)
/student/subject/<id> - DELETE (Unenroll to a subject by ID)

/student/subjects         - GET (GET ALL SUBJECTS)
/student/subjects/average - GET (GET AVERAGE FROM ALL SUBJECTS)
'''


@blp.route('/register')
class StudentRegister(MethodView):
    @blp.arguments(StudentSchema)
    @blp.response(200, StudentSchema)
    def post(self, student_info):
        if StudentModel.query.filter(
            StudentModel.email == student_info["email"]
        ).first():
            abort(400, message="A student with that email already exists.")
        
        student = StudentModel(
            name=student_info["name"],
            email=student_info["email"],
            password=pbkdf2_sha256.hash(student_info["password"],
            course=student_info["course"])
        )

        db.session.add(student)
        db.session.commit()

        return student

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(StudentLoginSchema)
    def post(self, login_cred):
        student = StudentModel.query.filter(
            StudentModel.email == login_cred["email"]
        ).first()

        if student and pbkdf2_sha256.verify(login_cred["password"], student.password):
            # Create access token
            access_token = create_access_token(identity=student.id, fresh=True)
            refresh_token = create_refresh_token(identity=student.id)
            return {"access_token": access_token, "refresh_token": refresh_token}
        
        abort(401, message="Invalid credentials.")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        # GET JTI
        jwt_jti = get_jwt()["jti"]

        new_blocked_jti = BlocklistModel(jti=jwt_jti)
        db.session.add(new_blocked_jti)
        db.session.commit()

        return {"message": "Successfully logged out."}

@blp.route("/refresh")
class TokenRefresh(MethodView):
    # Only accepts refresh tokens
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt()["sub"]

        # Create a new non-fresh access token
        new_token = create_access_token(identity=current_user, fresh=False)

        return {"access_token": new_token}