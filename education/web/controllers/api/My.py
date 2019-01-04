# -*- coding: utf-8 -*-
from web.controllers.api import route_api
from  flask import request,jsonify,session
from application import  app,db

from common.models.course.Course import Course
from common.models.instructor.InstructorComment import InstructorComment
from common.models.member.MemberComments import MemberComments
from common.models.member.Member import Member
#import 购物车db
from common.models.member.MemberCart import MemberCart

from common.libs.UrlManager import UrlManager

#selectFilterObj 把数据从table中forloop 出来，并且组成一个集合
from common.libs.Helper import selectFilterObj,getDictFilterField

#import json 删除数据时从前方反馈回来一个json数据所以要解析json数据
import json

# import 获得现在时间的方法
from common.libs.Helper import getCurrentDate


@route_api.route("/my/index",methods=["POST"])
def myIndex():
    resp = {'code':200,'msg':'展示成功','data':{}}
    comment_list = InstructorComment.query.order_by(InstructorComment.id.desc()).all()
    data_comment_list = []
    if comment_list:
        course_ids = selectFilterObj(comment_list, "course_id")
        course_map = getDictFilterField(Course, Course.id, "id", course_ids)
        for item in comment_list:
            tmp_course_info = course_map[item.course_id]
            tmp_data = {
                #comment表中的数据
                "id": item.id,
                "instructor_id": item.instructor_id,
                "title":item.title,
                "instructor_course_summary":item.instructor_course_summary,
                "updated_date":item.updated_time.strftime("%Y-%m-%d"),
                "pic_url": UrlManager.buildImageUrl(item.main_image),
                #mapping到course表中的数据
                "name": tmp_course_info.name,
                "course_date":tmp_course_info.course_date,
                "tags": tmp_course_info.tags,
                "active": True
            }
            data_comment_list.append(tmp_data)

    resp['data']['list'] = data_comment_list
    return jsonify(resp)


#info页面
@route_api.route('/my/info',methods=["POST"])
def myInfo():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    id = int(req['id']) if 'id' in req else 0

    comment_info = InstructorComment.query.filter_by(id = id).first()
    if not comment_info:
        resp['code'] = -1
        resp['msg'] = '没有老师评论'
        return jsonify(resp)

    course_info = Course.query.filter_by(id = comment_info.course_id).first()

    course_id = comment_info.course_id
    register_number = 0
    if course_id:
        register_number = MemberCart.query.filter_by(course_id=course_id).count()

    resp['data']['info']={
        # comment表中的数据
        "id": comment_info.id,
        "instructor_id": comment_info.instructor_id,
        "course_id": comment_info.course_id,
        "title": comment_info.title,
        "instructor_course_summary": comment_info.instructor_course_summary,
        "updated_date": comment_info.updated_time.strftime("%Y-%m-%d"),
        "pic_url": UrlManager.buildImageUrl(comment_info.main_image),

        # mapping到course表中的数据
        "name": course_info.name,
        "price":str(course_info.price),
        "course_date": course_info.course_date,
        "tags": course_info.tags,
        "active": True,

        #MemberCart 的数据，本课程一共几个人报名
        'register_number': register_number
    }

    # 课程登记信息一同返回前台,计算共登记了几门课程
    member_info = session.member_info
    cart_number = 0
    if member_info:
        cart_number = MemberCart.query.filter_by(member_id=member_info.id).count()


    resp['data']['course_id'] = comment_info.course_id
    resp['data']['cart_number'] = cart_number

    return jsonify(resp)

#comment
@route_api.route('/my/comment/add',methods=["POST" , "GET"])
def myCommentAdd():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}

    req = request.values
    instructor_comment_id = int(req['instructor_comment_id']) if 'instructor_comment_id' in req else 0
    score = int(req['score']) if 'score' in req else 0
    content = req['content'] if 'content' in req else ''

    member_info = session.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '获取信息失败，未登录'
        return jsonify(resp)

    model_comment = MemberComments()
    model_comment.member_id = member_info.id
    model_comment.instructor_comment_id = instructor_comment_id
    model_comment.score = score
    model_comment.content = content
    model_comment.created_time = getCurrentDate()

    db.session.add(model_comment)
    db.session.commit()

    return jsonify(resp)


@route_api.route('/my/comments')
def myComment():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    instructor_comment_id = req['id'] if 'id' in req else 0

    query= MemberComments.query.filter_by(instructor_comment_id=instructor_comment_id)

    list = query.order_by(MemberComments.id.desc()).limit(5).all()
    data_list=[]
    if list:
        member_map = getDictFilterField(Member,Member.id,"id",selectFilterObj(list,'member_id'))
        for item in list:
            if item.member_id not in member_map:
                continue
            tmp_member_info = member_map[item.member_id]
            tmp_data = {
                'score':item.score_desc,
                'date':item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                'content':item.content,
                'user':{
                    'nickname':tmp_member_info.nickname,
                    'avatar_url':tmp_member_info.avatar
                }
            }
            data_list.append(tmp_data)

    resp['data']['list'] = data_list
    resp['data']['count'] = query.count()
    return jsonify(resp)