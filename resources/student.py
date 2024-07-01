from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jti

from db import db
from models import StudentModel, BlocklistModel, SubjectModel, SubjectStudent
from schemas import StudentSchema, StudentLoginSchema, GradeSchema, PlainSubjectSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

from passlib.hash import pbkdf2_sha256


blp = Blueprint("students", __file__, description="Operations on students."
)

'''

✅ /login     - POST   (Generate access, refresh)
✅ /logout    - POST   (Revoke access token)
✅ /refresh   - POST   (Generate non-fresh token)
✅ /register  - POST   (Create a new student model)

JWT Based - Identity (user.id)
✅ /student - GET (Student info)
✅ /student - DELETE (Delete account)


/students - GET (Get all students)

✅ /student/subject/<id> - GET (Get subject info by ID)
✅ /student/subject/<id> - POST (Enroll to a subject by ID)
✅ /student/subject/<id> - DELETE (Unenroll to a subject by ID)

✅ /student/subject/<id>/grades - GET (Get grades from a single subject)
✅ /student/subject/<id>/grades - PUT (Edit Grades)
✅ /student/subjects/grades - GET ALL SUBJECTS AND THEIR GRADES


✅ /student/subjects         - GET (GET ALL SUBJECTS)
✅ /student/average - GET (GET AVERAGE FROM ALL SUBJECTS)


'''

@blp.route("/student/average")
class StudentAverage(MethodView):
    @jwt_required()
    def get(self):
        grades = StudentModel.query.get_or_404(get_jwt_identity()).subject_students
        average = [85.0, 91.0, 88.0, 88.67]
        for grade in grades:
            average.append(grade.average_grade)

        return {"average": sum(average)/len(average)}

@blp.route("/students")
class Students(MethodView):
    @blp.response(200, StudentSchema(many=True))
    def get(self):
        return StudentModel.query.all()

@blp.route("/student/subjects/grades")
class AllSubjectsGrades(MethodView):
    @jwt_required()
    @blp.response(200, GradeSchema(many=True))
    def get(self):
        return StudentModel.query.get_or_404(get_jwt_identity()).subject_students

@blp.route("/student/subject/<int:subject_id>/grades")
class SubjectGrades(MethodView):
    @jwt_required()
    @blp.response(200, GradeSchema)
    def get(self, subject_id):
        student = StudentModel.query.get_or_404(get_jwt_identity()) # 1
        subject = SubjectModel.query.get_or_404(subject_id)         # 1

        if subject not in student.subjects:
            abort(400, message="Student not enrolled in that subject")
        
        grades = SubjectStudent.query.filter(
            SubjectStudent.student_id == student.id,
            SubjectStudent.subject_id == subject.id
        ).first()

        return grades
    
    @jwt_required()
    @blp.arguments(GradeSchema)
    @blp.response(200, GradeSchema)
    def put(self, grade_data, subject_id):
        student = StudentModel.query.get_or_404(get_jwt_identity()) # 1
        subject = SubjectModel.query.get_or_404(subject_id)         # 1

        if subject not in student.subjects:
            abort(400, message="Student not enrolled in that subject")
        
        grades = SubjectStudent.query.filter(
            SubjectStudent.student_id == student.id,
            SubjectStudent.subject_id == subject.id
        ).first()

        if 'prelims_grade' in grade_data:
            grades.prelims_grade = grade_data['prelims_grade']
        if 'midterms_grade' in grade_data:
            grades.midterms_grade = grade_data['midterms_grade']
        if 'finals_grade' in grade_data:
            grades.finals_grade = grade_data['finals_grade']

        db.session.add(grades)
        db.session.commit()

        return grades
        
@blp.route("/student/subjects")
class EnrolledSubjects(MethodView):
    @jwt_required()
    @blp.response(200, PlainSubjectSchema(many=True))
    def get(self):
        student = StudentModel.query.get_or_404(get_jwt_identity())
        
        return student.subjects

@blp.route("/student/subject/<int:subject_id>")
class EnrolledSubject(MethodView):
    @jwt_required()
    @blp.response(200, PlainSubjectSchema)
    def get(self, subject_id):
        student = StudentModel.query.get_or_404(get_jwt_identity())
        subject = SubjectModel.query.get_or_404(subject_id)

        if subject not in student.subjects:
            abort(400, message="Student not enrolled in the subject.")

        return subject

    @jwt_required()
    @blp.response(201, PlainSubjectSchema)
    def post(self, subject_id):
        student = StudentModel.query.get_or_404(get_jwt_identity())
        subject = SubjectModel.query.get_or_404(subject_id)

        # Before linking, make sure that the item and the tag is inside the same store
        if subject in student.subjects:
            abort(400, message="You are already enrolled in that subject.")

        student.subjects.append(subject)
    
        try:
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while enrolling on the subject.")
        
        return subject
    
    @jwt_required()
    def delete(self, subject_id):
        student = StudentModel.query.get_or_404(get_jwt_identity())
        subject = SubjectModel.query.get_or_404(subject_id)

        if subject not in student.subjects:
            abort(400, message="You are not enrolled on that subject.")
        
        student.subjects.remove(subject)

        try:
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while unenrolling from the subject.")

        return {"message": "Subject was successfully unenrolled."}


@blp.route("/student")
class Student(MethodView):
    @jwt_required()
    @blp.response(200, StudentSchema)
    def get(self):
        student_id = get_jwt_identity()
        student = StudentModel.query.get_or_404(student_id)
        return student
    
    @jwt_required(fresh=True)
    def delete(self):
        student_id = get_jwt_identity()
        student = StudentModel.query.get_or_404(student_id)
        
        db.session.delete(student)
        db.session.commit()

        return {"message": "Your account has been successfully deleted."}


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
            password=pbkdf2_sha256.hash(student_info["password"]),
            course=student_info["course"]
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
        jwt_jti = get_jti()
        new_blocked_jti = BlocklistModel(jti=jwt_jti)
        db.session.add(new_blocked_jti)
        db.session.commit()

        return {"message": "Successfully logged out."}

@blp.route("/refresh")
class TokenRefresh(MethodView):
    # Only accepts refresh tokens
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()

        # Create a new non-fresh access token
        new_token = create_access_token(identity=current_user, fresh=False)

        return {"access_token": new_token}