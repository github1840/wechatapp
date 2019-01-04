# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,session,request,jsonify,redirect
from common.models.course.CourseCat import CourseCat
from common.models.course.Course import Course
from common.libs.Helper import getCurrentDate,iPagination,getDictFilterField
from common.libs.UrlManager import UrlManager
from common.models.course.CourseStockChangeLog import CourseStockChangeLog
from application import app,db
from common.libs.Helper import getCurrentDate
from decimal import Decimal
from sqlalchemy import  or_


route_course = Blueprint( 'course_page',__name__ )

@route_course.route( "/index" )
def index():
    # 要把current-user传进来，用于layout 中的个人设置页面
    current_user = session.current_user
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = Course.query
    if 'mix_kw' in req:
        rule = or_(Course.name.ilike("%{0}%".format(req['mix_kw'])), Course.tags.ilike("%{0}%".format(req['mix_kw'])))
        query = query.filter(rule)

    if 'status' in req and int(req['status']) > -1:
        query = query.filter(Course.status == int(req['status']))

    if 'cat_id' in req and int(req['cat_id']) > 0:
        query = query.filter(Course.cat_id == int(req['cat_id']))

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

    cat_mapping = getDictFilterField(CourseCat, CourseCat.id, "id", [])

    search_con = req
    status_mapping = app.config['STATUS_MAPPING']
    current= 'index'
    return render_template( "course/index.html", current_user=current_user, list = list , pages=pages,search_con=search_con,status_mapping = status_mapping,
                            cat_mapping=cat_mapping,current = current)


@route_course.route( "/info" )
def info():
    current_user = session.current_user

    req = request.args
    id = int(req.get("id", 0))
    reback_url = UrlManager.buildUrl("/course/index")

    if id < 1:
        return redirect(reback_url)

    info = Course.query.filter_by(id=id).first()
    if not info:
        return redirect(reback_url)

    stock_change_list = CourseStockChangeLog.query.filter(CourseStockChangeLog.course_id == id) \
        .order_by(CourseStockChangeLog.id.desc()).all()

    current = 'index'
    return render_template("course/info.html", current_user=current_user,stock_change_list=stock_change_list,info=info,current = current)


@route_course.route("/ops",methods=["POST"])
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

    food_info = Course.query.filter_by( id = id ).first()
    if not food_info:
        resp['code'] = -1
        resp['msg'] = "指定美食不存在~~"
        return jsonify(resp)

    if act == "remove":
        food_info.status = 0
    elif act == "recover":
        food_info.status = 1

    food_info.updated_time = getCurrentDate()
    db.session.add(food_info)
    db.session.commit()
    return jsonify( resp )



@route_course.route( "/set",methods=["GET","POST"]  )
def set():
    current_user = session.current_user
    #信息的展示
    if request.method == "GET":
        #展示种类
        #没有Course数据是cat显示全部，有Course数据后只显示course的cat，在html中用if来判断
        cat_list = CourseCat.query.all()  # 如果方法是GET 展示全部内容 （1.没有选中course名称，无ID 则至展示cat的几种可能性，如果有course id那么展示该course的全部info）
        current = 'index'

        # 展示选中的课程内容
        # 在set表中显示已有数据，即修改课程
        req = request.args
        id = int(req.get('id', 0))
        info = Course.query.filter_by(id=id).first()
        if info and info.status != 1:
            return redirect(UrlManager.buildUrl('course/index'))
        return render_template("course/set.html", current_user=current_user, current=current, cat_list=cat_list,info = info)


    #信息的获取
    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values
    id = int(req['id']) if 'id' in req and req['id'] else 0
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    name = req['name'] if 'name' in req else ''
    instructor_id = int(req['instructor_id']) if 'instructor_id' in req else 0
    course_date = req['course_date'] if 'course_date' in req else ''
    location = req['location'] if 'location' in req else ''
    price = req['price'] if 'price' in req else ''
    main_image = req['main_image'] if 'main_image' in req else ''
    summary = req['summary'] if 'summary' in req else ''
    stock = int(req['stock']) if 'stock' in req else ''
    tags = req['tags'] if 'tags' in req else ''

    if cat_id < 1:
        resp['code'] = -1
        resp['msg'] = "请选择分类~~"
        return jsonify(resp)

    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的名称~~"
        return jsonify(resp)

    if instructor_id < 1:
        resp['code'] = -1
        resp['msg'] = "请输入老师ID~~"
        return jsonify(resp)

    if course_date is None or len(course_date) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入课程日期~~"
        return jsonify(resp)

    if location is None or len(location) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入开课地址~~"
        return jsonify(resp)

    if not price or len(price) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的售卖价格~~"
        return jsonify(resp)

    price = Decimal(price).quantize(Decimal('0.00'))
    if price <= 0:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的售卖价格~~"
        return jsonify(resp)

    if main_image is None or len(main_image) < 3:
        resp['code'] = -1
        resp['msg'] = "请上传封面图~~"
        return jsonify(resp)

    if summary is None or len(summary) < 3:
        resp['code'] = -1
        resp['msg'] = "请输入图书描述，并不能少于10个字符~~"
        return jsonify(resp)

    if stock < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的库存量~~"
        return jsonify(resp)

    if tags is None or len(tags) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入标签，便于搜索~~"
        return jsonify(resp)

    course_info = Course.query.filter_by(id=id).first()
    before_stock = 0
    if course_info:
        model_course = course_info
        before_stock = model_course.stock
    else:
        model_course = Course()
        model_course.status = 1
        model_course.created_time = getCurrentDate()

    # 添加课程详情
    model_course.cat_id = cat_id
    model_course.name = name
    model_course.instructor_id = instructor_id
    model_course.course_date = course_date
    model_course.location = location
    model_course.price = price
    model_course.main_image = main_image
    model_course.summary = summary
    model_course.stock = stock
    model_course.tags = tags
    model_course.updated_time = getCurrentDate()

    db.session.add(model_course)
    db.session.commit()


    return jsonify(resp)



@route_course.route( "/cat" )
def cat():
    current_user = session.current_user
    resp_data = {}
    req = request.values
    query = CourseCat.query

    if 'status' in req and int(req['status']) > -1:
        query = query.filter(CourseCat.status == int(req['status']))

    list = query.order_by(CourseCat.weight.desc(), CourseCat.id.desc()).all()
    resp_data['list'] = list
    search_con = req
    status_mapping = app.config['STATUS_MAPPING']
    current = 'cat'

    return render_template("course/cat.html", current_user=current_user, list=list, search_con=search_con,
                           current=current, status_mapping=status_mapping )

@route_course.route( "/cat-set",methods=["GET","POST"] )
def catSet():
    current_user = session.current_user
    if request.method == "GET":
        req = request.args
        id = int(req.get('id', 0))
        info = None
        if id:
            info = CourseCat.query.filter_by(id=id).first()
        current = 'cat'
        return render_template("course/cat_set.html", current_user=current_user, info=info, current=current)

    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values

    id = req['id'] if 'id' in req else 0
    name = req['name'] if 'name' in req else ''
    weight = int(req['weight']) if ('weight' in req and int(req['weight']) > 0) else 1

    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的分类名称~~"
        return jsonify(resp)

    course_cat_info = CourseCat.query.filter_by(id=id).first()
    if course_cat_info:
        model_course_cat = course_cat_info
    else:
        model_course_cat = CourseCat()
        model_course_cat.created_time = getCurrentDate()
    model_course_cat.name = name
    model_course_cat.weight = weight
    model_course_cat.updated_time = getCurrentDate()
    db.session.add(model_course_cat)
    db.session.commit()
    return jsonify(resp)


@route_course.route("/cat-ops",methods = [ "POST" ])
def catOps():
    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values

    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    if not id :
        resp['code'] = -1
        resp['msg'] = "请选择要操作的账号~~"
        return jsonify(resp)

    if  act not in [ 'remove','recover' ] :
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试~~"
        return jsonify(resp)

    course_cat_info = CourseCat.query.filter_by( id= id ).first()
    if not course_cat_info:
        resp['code'] = -1
        resp['msg'] = "指定分类不存在~~"
        return jsonify(resp)

    if act == "remove":
        course_cat_info.status = 0
    elif act == "recover":
        course_cat_info.status = 1

        course_cat_info.update_time = getCurrentDate()
    db.session.add( course_cat_info )
    db.session.commit()
    return jsonify(resp)