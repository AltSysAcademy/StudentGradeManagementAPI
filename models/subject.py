from db import db

class SubjectModel(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String, unique=True, nullable=False)
    units = db.Column(db.Integer, unique=False, nullable=False)

    # Define a many-many relationship with students
    students = db.relationship("StudentModel", back_populates="subjects", secondary="subject_student", cascade='all, delete')