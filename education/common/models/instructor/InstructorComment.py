from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.schema import FetchedValue
from application import db


class InstructorComment(db.Model):
    __tablename__ = 'instructor_comment'

    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    course_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    title = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue())
    main_image = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    instructor_course_summary = db.Column(db.String(2000), nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())


