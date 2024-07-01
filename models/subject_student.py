from db import db

class SubjectStudent(db.Model):
    __tablename__ = "subject_student"

    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"))

    prelims_grade = db.Column(db.Float, nullable=True)
    midterms_grade = db.Column(db.Float, nullable=True)
    finals_grade = db.Column(db.Float, nullable=True)

    # Add a new relationship to provide us with a subject and student
    student = db.relationship('StudentModel', back_populates='subject_students', overlaps="subjects,students")
    subject = db.relationship('SubjectModel', back_populates='subject_students', overlaps="students,subjects")

    @property
    def average_grade(self):
        grades = [self.prelims_grade, self.midterms_grade, self.finals_grade]

        valid_grades = list()

        for grade in grades:
            if grade is not None:
                valid_grades.append(grade)

        if len(valid_grades) > 0:
            return round(sum(valid_grades) / len(valid_grades), 2)
        return None