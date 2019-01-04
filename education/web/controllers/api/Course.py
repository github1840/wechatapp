# -*- coding: utf-8 -*-

from web.controllers.api import route_api
from  flask import request,jsonify,session
from application import  app,db
import requests,json


# import 获得现在时间的方法
from common.libs.Helper import getCurrentDate,getDictFilterField,selectFilterObj

#import Course db
from common.models.course.Course import Course
from common.models.course.CourseCat import CourseCat

#import 购物车db
from common.models.member.MemberCart import MemberCart

#import member相关数据库
from common.models.member.Member import Member
from common.models.member.MemberComments import MemberComments

#import UrlManager
from common.libs.UrlManager import UrlManager

#import instructor_comment db
from common.models.instructor.InstructorComment import InstructorComment


#import _or
from sqlalchemy import or_

@route_api.route('/course/index')
def courseIndex():
    resp = {'code': 200,'msg':'操作成功','data':{}}

    #类别
    cat_list=CourseCat.query.filter_by(status=1).order_by(CourseCat.weight.desc()).all()
    #数据重构是为了把'全部'这个类型加到目录中去
    data_cat_list = []
    data_cat_list.append({
        'id':0,
        'name':'全部'
    })
    if cat_list:
        for item in cat_list:
            tmp_data = {
                'id':item.id,
                'name':item.name
            }
            data_cat_list.append(tmp_data)
    resp['data']['cat_list'] = data_cat_list
    #banner
    banner_list=Course.query.filter_by(status = 1).order_by(Course.total_count.desc(),Course.id.desc()).limit(3).all()
    data_banner_list = []
    if banner_list:
        for item in banner_list:
            tmp_data={
                'id':item.id,
                'pic_url':UrlManager.buildImageUrl(item.main_image)
            }
            data_banner_list.append(tmp_data)
    resp['data']['banner_list'] = data_banner_list

    return jsonify(resp)


@route_api.route('/course/search')
def courseSearch():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    #获取前台发来的值
    req = request.values
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
      #分页相关
    p = int(req['p']) if 'p' in req else 1
    if p<1:
        p =1
    page_size = 10
    offset = (p-1)*page_size
    #通过种类和关键字进行query
    query = Course.query.filter_by(status = 1)
    if cat_id > 0:
        query = query.filter_by(cat_id = cat_id )

    if mix_kw:
        rule = or_(Course.name.ilike("%{0}%".format(mix_kw)), Course.tags.ilike("%{0}%".format(mix_kw)))
        query = query.filter(rule)
                                                                            #与分页相关的两个限定值，offset 与 limit
    course_list = query.order_by(Course.total_count.desc(),Course.id.desc()).offset(offset).limit(page_size).all()

    #组装返回的数据列表
    data_course_list = []
    if course_list:
        for item in course_list:
            tmp_data={
                'id':item.id,
                'name':item.name,
                'course_date':item.course_date,
                'location':item.location,
                'price':str(item.price),
                'pic_url':UrlManager.buildImageUrl(item.main_image)
            }
            data_course_list.append(tmp_data)

    resp['data']['list'] = data_course_list
       # 分页后判断数据是否已经没有了
    resp['data']['has_more'] = 0 if len(data_course_list) < 1 else 1
    return jsonify(resp)


#info页面
@route_api.route('/course/info')
def courseInfo():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    id = int(req['id']) if 'id' in req else 0,

    course_info = Course.query.filter_by(id = id).first()
    if not course_info or not course_info.status:
        resp['code'] = -1
        resp['msg'] = '课程已经下架'
        return jsonify(resp)


    #课程登记信息一同返回前台,计算共登记了几门课程
    member_info = session.member_info
    cart_number = 0
    if member_info:
        cart_number = MemberCart.query.filter_by(member_id=member_info.id,register_status=1).count()

    #该课有几人报名
    course_id = id
    register_number = 0
    if course_id:
        register_number = MemberCart.query.filter_by(course_id=course_id,register_status=1).count()


    resp['data']['info'] = {
        'id':course_info.id,
        'name':course_info.name,
        'course_date': course_info.course_date,
        'location': course_info.location,
        'summary':course_info.summary,
        'total_count':course_info.total_count,
        'main_image':UrlManager.buildImageUrl(course_info.main_image),
        'price':int(course_info.price),
        'stock':int(course_info.stock),
        'pics':[UrlManager.buildImageUrl(course_info.main_image)],
        'register_number':register_number
    }

    resp['data']['cart_number'] = cart_number


    return jsonify(resp)


@route_api.route('/course/comments')
def courseComment():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    course_id = req['id'] if 'id' in req else 0

    query= MemberComments.query.filter_by(course_id=course_id)

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


#addcomment
@route_api.route('/course/comment/add',methods=["POST" , "GET"])
def courseCommentAdd():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}

    req = request.values
    course_id = int(req['course_id']) if 'course_id' in req else 0
    score = int(req['score']) if 'score' in req else 0
    content = req['content'] if 'content' in req else ''

    member_info = session.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '获取信息失败，未登录'
        return jsonify(resp)

    model_comment = MemberComments()
    model_comment.member_id = member_info.id
    model_comment.course_id = course_id
    model_comment.score = score
    model_comment.content = content
    model_comment.created_time = getCurrentDate()

    db.session.add(model_comment)
    db.session.commit()

    return jsonify(resp)


@route_api.route('/course/activity')
def courseActivity():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    course_id = int(req['course_id']) if 'course_id' in req else 0

    instructor_comment_info = InstructorComment.query.filter_by(course_id = course_id).order_by(InstructorComment.id.desc()).first()

    if not instructor_comment_info:
        resp['code'] = -1
        resp['msg'] = '~~~~~该课程目前还没有新动态~~~~'
        return jsonify(resp)

    instructor_comment_id = instructor_comment_info.id
    resp['data']['instructor_comment_id'] = instructor_comment_id
    return jsonify(resp)