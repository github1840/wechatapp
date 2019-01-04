# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer
from sqlalchemy.schema import FetchedValue
from application import db


class MemberCart(db.Model):
    __tablename__ = 'member_cart'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.BigInteger, nullable=False, index=True, server_default=db.FetchedValue())
    course_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    register_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    payment_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    quantity = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())


    @property
    def payment_status_desc(self):
        payment_status_mapping = {
            "0": '未付',
            '1': '已付'
        }
        return payment_status_mapping[str(self.payment_status)]
