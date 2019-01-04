# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,session,request,jsonify,redirect
from common.models.course.CourseCat import CourseCat
from common.models.course.Course import Course
from common.models.instructor.InstructorComment import InstructorComment
from common.models.member.MemberCart import MemberCart
from common.models.member.Member import Member


from common.libs.Helper import getCurrentDate,iPagination,getDictFilterField
from common.libs.UrlManager import UrlManager
from common.models.course.CourseStockChangeLog import CourseStockChangeLog
from application import app,db
from common.libs.Helper import getCurrentDate

from decimal import Decimal
from sqlalchemy import  or_

#selectFilterObj 把数据从table中forloop 出来，并且组成一个集合
from common.libs.Helper import selectFilterObj,getDictFilterField

route_instructor = Blueprint( 'instructor_page',__name__ )

@route_instructor.route( "/index" ,methods=["GET","POST"]  )
def index():
    # 要把current-user传进来，用于layout 中的个人设置页面
    current_user = session.current_user
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = Course.query

    if 'instructor_id' in req and int(req['instructor_id']) > 0:
        query = query.filter(Course.instructor_id == int(req['instructor_id']))

    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    list = query.order_by(Course.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()

    search_con = req
    current = 'index'
    return render_template("instructor/index.html", current_user=current_user, list=list, pages=pages, current=current,search_con=search_con,)

@route_instructor.route( "/info" ,methods=["GET","POST"] )
def info():
    current_user = session.current_user
    req = request.values
    id = int(req['id']) if 'id' in req else 0
    print(id)
    if request.method == "GET":
        reback_url = UrlManager.buildUrl("/instructor/index")

        if id < 1:
            return redirect(reback_url)
        #course 的信息
        info = Course.query.filter_by(id=id).first()
        if not info:
            return redirect(reback_url)
        #已报名用户的信息
        data_cart_list = []
        cart_list = MemberCart.query.filter_by(course_id=id).order_by(MemberCart.id.desc()).all()
        if cart_list:
            member_ids = selectFilterObj(cart_list, "member_id")
            member_map = getDictFilterField(Member, Member.id, "id", member_ids)


        for item in cart_list:
            tmp_member_info = member_map[item.member_id]
            tmp_data = {
                "id": item.id,
                "register_status": item.register_status,
                "payment_status": item.payment_status,
                "member_avatar": tmp_member_info.avatar,
                "member_name": tmp_member_info.reg_ip,
                "member_sex": tmp_member_info.sex,

            }
            data_cart_list.append(tmp_data)

        list =  data_cart_list

        return render_template("instructor/info.html", current_user=current_user, info=info,list =list)
    #课程掠影部分数据的录入

    # 信息的获取
    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values

    title = req['title'] if 'title' in req else ''
    summary = req['summary'] if 'summary' in req else ''
    main_image = req['main_image'] if 'main_image' in req else ''

    if title is None or len(title) < 3:
        resp['code'] = -1
        resp['msg'] = "请输入封面标题，并不能少于5个字符~~"
        return jsonify(resp)

    if summary is None or len(summary) < 3:
        resp['code'] = -1
        resp['msg'] = "请输入课程掠影，并不能少于10个字符~~"
        return jsonify(resp)

    if main_image is None or len(main_image) < 3:
        resp['code'] = -1
        resp['msg'] = "请上传封面图~~"
        return jsonify(resp)

    model_instructor = InstructorComment()
    model_instructor.instructor_id = current_user.uid
    model_instructor.course_id = id
    model_instructor.title = title
    model_instructor.main_image = main_image
    model_instructor.instructor_course_summary = summary
    model_instructor.updated_time = getCurrentDate()

    db.session.add(model_instructor)
    db.session.commit()

    return jsonify(resp)


@route_instructor.route("/ops",methods=["POST"])
def ops():
    resp = { 'code':200,'msg':'操作成功~~','data':{} }
    req = request.values

    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''

    if not id :
        resp['code'] = -1
        resp['msg'] = "请选择要操作的账号~~"
        return jsonify(resp)

    if act not in [ 'remove','recover' ]:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试~~"
        return jsonify(resp)

    MemberCart_info = MemberCart.query.filter_by( id = id ).first()
    if not MemberCart_info:
        resp['code'] = -1
        resp['msg'] = "会员不存在了~~"
        return jsonify(resp)

    if act == "recover":
        MemberCart_info.payment_status = 0
    elif act == "remove":
        MemberCart_info.payment_status = 1

    MemberCart_info.updated_time = getCurrentDate()
    db.session.add(MemberCart_info)
    db.session.commit()
    return jsonify( resp )