from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt

from db import db
from models import SubjectModel
from schemas import SubjectSchema, PlainSubjectSchema
from sqlalchemy.exc import SQLAlchemyError

from passlib.hash import pbkdf2_sha256


blp = Blueprint("subjects", __file__, description="Operations on subjects."
)

'''
@jwt_required(is_admin=True)
✅ /subjects - GET ALL SUBJECTS
✅ /subject/ - POST (CREATE SUBJECT)

✅ /subject/<id> - GET (GET SUBJECT BY ID)
✅ /subject/<id> - DELETE (DELETE SUBJECT BY ID)

   /subject/<id>/student - GET (Get enrolled students on a subject)
'''
@blp.route("/subject/<int:subject_id>")
class Subjects(MethodView):
    @blp.response(200, SubjectSchema)
    def get(self, subject_id):
        subject = SubjectModel.query.get_or_404(subject_id)
        return subject
    
    def delete(self, subject_id):
        subject = SubjectModel.query.get_or_404(subject_id)


        try:
            db.session.delete(subject)
            db.session.commit()
        except:
            return {"message": "The subject is currently in use by other students."}

        return {"message": "The subject has been successfully deleted."}
    

@blp.route("/subjects")
class GetSubjects(MethodView):
    @blp.response(200, SubjectSchema(many=True))
    def get(self):
        return SubjectModel.query.all()
                  
                  
@blp.route("/subject")
class CreateSubject(MethodView):
    @blp.arguments(SubjectSchema)
    @blp.response(201, SubjectSchema)
    def post(self, new_subject_info):
        new_subj = SubjectModel(**new_subject_info)

        try:
            db.session.add(new_subj)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error has occured while creating an item.")
        
        return new_subj