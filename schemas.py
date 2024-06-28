from marshmallow import Schema, fields

class PlainStudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    course = fields.Str(required=True)

class StudentLoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class PlainSubjectSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    units = fields.Float(required=True)

class StudentSchema(PlainStudentSchema):
    subjects = fields.List(fields.Nested(PlainSubjectSchema()), dump_only=True)

class SubjectSchema(PlainSubjectSchema):
    students = fields.List(fields.Nested(PlainStudentSchema()), dump_only=True)

# Used when unenrolling a subject to a student
class SubjectAndStudentSchema(Schema):
    message = fields.Str()
    student = fields.Nested(StudentSchema())
    subject = fields.Nested(SubjectSchema())

class GradeSchema(Schema):
    subject = fields.Nested(PlainSubjectSchema(), dump_only=True)
    prelims_grade = fields.Float(required=False)
    midterms_grade = fields.Float(required=False)
    finals_grade = fields.Float(required=False)
    average_grade = fields.Float(required=False)

'''
login user 1

/student/subject/1/grade
{
    "subject": {
        "name": "Philo101",
        "description": "Introduction to Philosophy",
        "units": 3
    },
    "prelims_grade": 50,
    "midterms_grade": None,
    "finals_grade": None,
    "average_grade": 50
}
'''

