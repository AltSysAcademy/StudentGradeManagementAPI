from db import db

class StudentModel(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    course = db.Column(db.String, unique=False, nullable=False)

    # Define a many-many relationship with subjects
    subjects = db.relationship("SubjectModel", back_populates="students", secondary="subject_student", cascade='all, delete')