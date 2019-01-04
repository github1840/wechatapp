# -*- coding: utf-8 -*-
from web.controllers.api import route_api
from  flask import request,jsonify,session
from application import  app,db

from common.models.course.Course import Course
from common.models.member.MemberCart import MemberCart
from common.libs.member.CartService import CartService

from common.libs.UrlManager import UrlManager

#selectFilterObj 把数据从table中forloop 出来，并且组成一个集合
from common.libs.Helper import selectFilterObj,getDictFilterField
from common.libs.Helper import getCurrentDate

#import json 删除数据时从前方反馈回来一个json数据所以要解析json数据
import json

@route_api.route("/cart/set",methods=["POST"])
def setCart():
    resp = {'code':200, 'msg':'操作成功','data':{}}
    req = request.values
    course_id = int(req['id']) if 'id' in req else 0
    number =  int(req['number']) if 'number' in req else 0

    if course_id <1 or number <1 :
        resp['code'] = -1
        resp['msg'] = '课程注册失败'
        return jsonify(resp)

    member_info = session.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] ='会员信息加载失败'
        return jsonify(resp)

    course_info = Course.query.filter_by( id = course_id).first()
    if not course_info:
        resp['code'] = -1
        resp['msg'] ='该课程已经下架'
        return jsonify(resp)

    if course_info.stock < number:
        resp['code'] = -1
        resp['msg'] = '对不起，名额已经报满~~~'
        return jsonify(resp)

    #db
    member_id = member_info.id
    cart_info = MemberCart.query.filter_by(course_id=course_id, member_id=member_id).first()
    if cart_info:
        model_cart = cart_info
        model_cart.register_status = 1
    else:
        model_cart = MemberCart()
        model_cart.member_id = member_id
        model_cart.created_time = getCurrentDate()

    model_cart.course_id = course_id
    model_cart.quantity = number
    model_cart.updated_time = getCurrentDate()
    db.session.add(model_cart)


    #报名后计算course totoal_count
    model_course = course_info
    model_course.total_count = MemberCart.query.filter_by(course_id=course_id,register_status=1).count()

    db.session.add(model_course)


    db.session.commit()

    return jsonify(resp)

@route_api.route("/cart/index",methods=["POST","GET"])
def carIndex():
    resp = {'code':200,'msg':'展示成功','data':{}}
    member_info = session.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '获取失败未登录~~~'
        jsonify(resp)

    member_details = {
        'avatar' : member_info.avatar,
        'nickname' :member_info.nickname
    }

    cart_list = MemberCart.query.filter_by(member_id=member_info.id,register_status=1).order_by(MemberCart.id.desc()).all()
    data_cart_list = []
    if cart_list:
        course_ids = selectFilterObj(cart_list, "course_id")
        course_map = getDictFilterField(Course, Course.id, "id", course_ids)
        for item in cart_list:
            tmp_course_info = course_map[item.course_id]
            tmp_data = {
                "id": item.id,
                "number": item.quantity,
                "course_id": item.course_id,
                "payment_status":item.payment_status,
                "name": tmp_course_info.name,
                "course_date":tmp_course_info.course_date,
                "location": tmp_course_info.location,
                "price": str(tmp_course_info.price),
                "pic_url": UrlManager.buildImageUrl(tmp_course_info.main_image),
                "active": True
            }
            data_cart_list.append(tmp_data)

    resp['data']['list'] = data_cart_list
    resp['data']['member_details'] = member_details
    return jsonify(resp)


@route_api.route("/cart/del", methods=["POST"])
def delCart():
    resp = {'code': 200, 'msg': '添加购物车成功~', 'data': {}}
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None

    items = []
    if params_goods:
        items = json.loads(params_goods)
    if not items or len( items ) < 1:
        return jsonify(resp)

    member_info = session.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "删除购物车失败-1~~"
        return jsonify(resp)


    ret = CartService.deleteItem( member_id = member_info.id, items = items )
    if not ret:
        resp['code'] = -1
        resp['msg'] = "删除购物车失败-2~~"
        return jsonify(resp)
    return jsonify(resp)