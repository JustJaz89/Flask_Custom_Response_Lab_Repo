from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Creating student_course junction table
student_course = db.Table('student_course',
                    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                    db.Column('grade', db.String(5))
                    )

# Models
class Student(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer())
    gpa = db.Column(db.Float())

class Course(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    instructor_id = db.Column(db.Integer(), db.ForeignKey('instructor.id'))
    credits = db.Column(db.Integer())
    instructor=db.relationship("Instructor")
    students = db.relationship("Student", secondary=student_course, backref='courses')

class Instructor(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    hire_date = db.Column(db.Date())



# Schemas
class StudentSchema(ma.Schema):
    # id = fields.Integer(primary_key = True)
    # first_name = fields.String(required = True)
    # last_name = fields.String(required = True)
    # year = fields.Integer()
    # gpa = fields.Float()

    class Meta:
        fields = ("id", "first_name", "last_name", "year", "gpa")

student_schema = StudentSchema()
students_schema = StudentSchema(many = True)

class StudentNameSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name")

student_name_schema = StudentNameSchema()
students_schema = StudentNameSchema(many = True)

# Resources
class StudentListResource(Resource):
    def get(self):
        all_students = Student.query.all()
        return students_schema.dump(all_students)
    
    def get(self):
        last_name_param = request.args.get("last_name")
        gpa_param = request.args.get("gpa")
        # sort = request.args.get("sort")

        query = Student.query
        if last_name_param:
            query = query.filter(Student.last_name.has(name=last_name_param))
        if gpa_param:
            query = query.filter(Student.gpa.has(name=gpa_param))
        # if sort:
        #     query = query,order_by(sort)
        students = query.all()
        return students_schema.dump(students)
    
class FullCourseDetailResource(resource):
    def get(self, course_id):

        custom_response = {}

        students = Student.query.all()

        for student in students:
            students = Student.query.filter(Student.students.has(id=student.id))

            custom_response[student.name] = {
                "number_of_students": student.number_of_students,
                "students": student_schema.dump(students)
            }

        return custom_response, 200
        
        # for student in student_data:
        #     student_info = {
        #         "number_of_students":student[]
        #         "students": student[]
        #     }
        #     response["student_info"].append(student_info)

        # return jsonify(response)

# Routes
api.add_resource(StudentListResource, '/api/students')
api.add_resource(FullCourseDetailResource, '/api/students/<int:course_id>')

