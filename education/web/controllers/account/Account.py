# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,session,request,redirect,jsonify
from common.models.User import User
from common.libs.UrlManager import UrlManager
from common.libs.user.UserService import UserService  # 用于pwd的加密
from common.libs.Helper import iPagination,getCurrentDate
from application import app,db
from sqlalchemy import or_



route_account = Blueprint( 'account_page',__name__ )



@route_account.route( "/index" )
def index():
    #本页就是简单的list展示和分页功能

    #要把current-user传进来，用于layout 中的个人设置页面
    current_user = session.current_user

    #1.分页
    req = request.values  #前端获取pages
    page = int(req['p']) if ('p' in req and req['p']) else 1
    page_params = {

        'total': User.query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace( "&p={}".format(page),"" )
    }
    pages = iPagination(page_params) #计算出page数量
    offset = (page-1)*app.config['PAGE_SIZE'] #计算下一页的开头
    limit = app.config['PAGE_SIZE'] * page


    # 2. 搜索 复杂查询用到or_()
    query = User.query  # 在3中如果没有进行2的搜索功能那么3是无法显示的因为没有User的信息，所以这里先query一下User中全部的信息。以备没有2的数据可用

    if 'mix_kw' in req:
        rule = or_(User.nickname.ilike("%{0}%".format(req['mix_kw'])),
                   User.mobile.ilike("%{0}%".format(req['mix_kw'])))  # 复合查询
        query = User.query.filter(rule)

    if 'status' in req and int(req['status']) > -1:
        query = User.query.filter(User.status == int(req['status']))


    #3.展示用户列表,取出全部的倒叙排列 注意这里没有用User.query !!!! 而是从第2步中获得
    list = query.order_by(User.uid.desc()).all()[offset:limit]
    #4 删除用户

    # 前端有index.html 有两种数据传输方法，一个是是传到python中一个是传到js中
    #< a class ="m-l" href="{{ buildUrl('/account/set')}}?id={{ item.uid  }}" >
    #<a class ="m-l remove" href="javascript:void(0);" data="{{item.uid}}" >



    return render_template( "account/index.html",current_user=current_user,list=list,pages=pages)




@route_account.route( "/info" )
def info():
    # 要把current-user传进来，用于layout 中的个人设置页面
    current_user = session.current_user

    req = request.args                            #request.args 方法只获得GET方法获得的值，并且可以用req.get直接获取
    uid = int(req.get('id',0))                    #用get直接获取GET方法获得的值，同时设置一个初始值为0
    return_url = UrlManager.buildUrl("/account/index")
    if uid < 1 :
        return redirect(return_url)               #如果没有该用户则跳转到用户栏首页

    info = User.query.filter_by(uid = uid).first() #查一下是否在数据库中有该用户
    if not info:
        return redirect(return_url)               #如果没有该数据那就直接跳回用户栏首页


    return render_template( "account/info.html",current_user=current_user,info = info)

@route_account.route( "/set",methods=["GET","POST"] )
def set():
    default_pwd = "******" #用于后面的判断是否对密码进行了修改
    # 要把current-user传进来，用于layout 中的个人设置页面
    current_user = session.current_user
    #如果方法是GET就直接展示页面,同时获取uid，用于识别要编辑的用户id，注意与current_user是两码事
    if request.method == "GET":
        req = request.args
        uid = int(req.get("id",0))
        info = None
        if uid :
            info = User.query.filter_by(uid = uid).first()  #通过uid我们可以获取到该用户信息然后显示在页面上，用于修改
        return render_template("account/set.html",current_user=current_user ,info = info)


    #如果方法是POST,那么获取数据，数据来自于set.js，这里省去了之前用过的form形式的收集数据的方法
    resp = {'code': 200,'msg': '操作成功','data' : {} }
    req= request.values#参数较多是用values, 参数少时用args

    id = req['id'] if 'id' in req else 0
    nickname = req['nickname'] if 'nickname' in req else ''
    mobile = req['mobile'] if 'mobile' in req  else''
    email = req['email'] if 'email' in req else''
    login_name = req['login_name'] if 'login_name' in req else''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''
    #校验一下数据
    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名~~"
        return jsonify(resp)

    if mobile is None or len(mobile) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的手机号码~~"
        return jsonify(resp)

    if email is None or len(email) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的邮箱~~"
        return jsonify(resp)

    if login_name is None or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的登录用户名~~"
        return jsonify(resp)

    if login_pwd is None or len(email) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的登录密码~~"
        return jsonify(resp)

    #查看是否已经重复，同时User.uid != id 是兼顾修改时用的。因为修改时是可能出现重复的，比如用户并没有修改登录名称
    has_in = User.query.filter(User.login_name == login_name, User.uid != id).first()
    if has_in:
        resp['code'] = -1
        resp['msg'] = "该登录名已存在，请换一个试试~~"
        return jsonify(resp)
    user_info = User.query.filter_by(uid=id).first()
    if user_info:
        model_user = user_info
    else:
        model_user = User()
        model_user.created_time = getCurrentDate()
        model_user.login_salt = UserService.geneSalt()
    #如果数据通过验证，则存入数据库
    model_user.nickname = nickname
    model_user.mobile = mobile
    model_user.email = email
    model_user.login_name = login_name
    if login_pwd != default_pwd:
        model_user.login_pwd = UserService.genePwd(login_pwd,model_user.login_salt)
    model_user.updated_time = getCurrentDate()

    db.session.add(model_user)
    db.session.commit()
    return jsonify(resp)


#用于删除账号
@route_account.route("/ops",methods = [ "POST" ])
def ops():
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

    user_info = User.query.filter_by(uid=id).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "指定账号不存在~~"
        return jsonify(resp)

    if act == "remove":
        user_info.status = 0
    elif act == "recover":
        user_info.status = 1

    if user_info and user_info.uid == 1:
        resp['code'] = -1
        resp['msg'] = "该用户是演示账号，不准操作账号~~"
        return jsonify(resp)

    user_info.update_time = getCurrentDate()
    db.session.add(user_info)
    db.session.commit()
    return jsonify(resp)



