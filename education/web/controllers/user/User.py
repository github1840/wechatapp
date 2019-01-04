# -*- coding: utf-8 -*-
#import 基本的工具
from flask import Blueprint,render_template,request,jsonify,redirect,url_for,make_response,session
import json


# import db 中的 User table 下面才有正式的引入db，是用于db.session 用的
from common.models.User import User
# import pwd maker 以及用于登录态，主要是用于制造一些加密的编码
from common.libs.user.UserService import UserService


#用于引入app中的config中的base_setting中的cookie的名字
#引入db，用于db.session 用的
from application import app, db

#用于logout
from common.libs.UrlManager import UrlManager



route_user = Blueprint( 'user_page',__name__ )



@route_user.route( "/login" , methods = ["GET","POST"])
def login():
    if request.method == "GET": # 1判断是获取还是发出信息，获取是GET， 发送给服务器是post  1
        return render_template( "user/login.html" )

    resp = {'code':200, 'msg':'Welcome!','data':{}} #设置一个jason的初始值，与小程序的思路很像

    # 2发出一个get请求获得前端的数据（填写的用户名和密码）
    req = request.values  #页面中全部的data都被存到变量req中， 下面再找出需要的data，比如loginname password 2
    login_name = req['login_name'] if 'login_name'in req else'' #在下面就可以直接用login_name 和 pwd 了
    login_pwd = req['login_pwd'] if 'login_pwd'in req else''

    # 3 username and pwd valification 用来过滤那些账号长度不符合要的
    if login_name is None or len(login_name)<1: #如果账户不对，则返回 json文件中的值 4
        resp['code']=-1
        resp['msg']="Please input correct username~~"
        return jsonify(resp)


    if login_pwd is None or len(login_pwd)<1: #如果账户不对，则返回 json文件中的值  4
        resp['code']=-1
        resp['msg']="Please input correct password~~"
        return jsonify(resp)


    # username and pwd valification 与数据库进行比对
    user_info = User.query.filter_by(login_name=login_name).first() # 比对数据库中的login_name是否和输入的一样 5
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "请输入正确的登陆名或密码 "
        return jsonify(resp)

    #验证密码时，需要三个信息都正确
    if user_info.login_pwd != UserService.genePwd(login_pwd,user_info.login_salt): #user_info.login_pwd 因为前面已经filter by username了，所以这里直接用该username的pwd 和 salt
        resp['code'] = -1
        resp['msg'] = "请输入正确的登陆名或密码 "
        return jsonify(resp)

    #用户状态的比对，如果用户已经被删除那就不能登陆了
    if user_info.status != 1 :
        resp['code'] = -1
        resp['msg'] = "账号异常：已被禁用 "
        return jsonify(resp)


    #4登录态 建立一个cookies，用于web.intercaptors.Authinterceptor 验证是否已经登陆用的，在里面的 check_login()函数里可以看到
    response = make_response(json.dumps({'code': 200, 'msg': '登录成功~~'}))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], '%s#%s' % (
        UserService.geneAuthCode(user_info), user_info.uid), 60 * 60 * 24 * 120)  # 保存120天
    return response



@route_user.route( "/edit" ,methods = ["GET","POST"])
def edit():
    current_user = session.current_user

    if request.method == 'GET':  #如果方法是 GET则用于页面的展示
        return render_template( "user/edit.html",current_user=current_user,current="edit" ) # current 参数修改 tab的选中提示的，参数在common/tab_user.html里面

    #if request.methods == 'POST': 如果方法是 POST则进行数据的获得
    resp = {'code':200 , 'msg':'操作成功','data':{}}
    req = request.values
    nickname = req['nickname'] if 'nickname' in req else ''
    email = req ['email'] if 'email' in req else ''


    #用于合规验证
    if nickname is None or len(nickname)<1:
        resp['code'] = -1
        resp['msg'] = '请输入规范的用户名~~~'
        return jsonify(resp)

    if email is None or len(email)<1:
        resp['code'] = -1
        resp['msg'] = '请输入规范的邮箱地址~~~'
        return jsonify(resp)

    # 数据获得后进行db.seesion， 因为前面current_user已经有了，所以直接用


    current_user.nickname = nickname  #后面的都数据 nickname and email 是来自POST方法
    current_user.email = email
    db.session.add(current_user)
    db.session.commit()
    return jsonify(resp)


@route_user.route( "/reset-pwd" ,methods = ["GET","POST"])
def resetPwd():
    current_user = session.current_user
    user_info = current_user
    if request.method == "GET":
        return render_template("user/reset_pwd.html", current_user=current_user,current="reset-pwd" )

    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values

    old_password = req['old_password'] if 'old_password' in req else ''
    new_password = req['new_password'] if 'new_password' in req else ''

    if old_password is None or len(old_password) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的原密码~~"
        return jsonify(resp)

    if new_password is None or len(new_password) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的新密码~~"
        return jsonify(resp)

    if old_password == new_password:
        resp['code'] = -1
        resp['msg'] = "请重新输入一个吧，新密码和原密码不能相同哦~~"
        return jsonify(resp)

    if user_info.uid == 1:
        resp['code'] = -1
        resp['msg'] = "该用户是演示账号，不准修改密码和登录用户名~~"
        return jsonify(resp)

    user_info.login_pwd = UserService.genePwd(new_password, user_info.login_salt)

    db.session.add(user_info)
    db.session.commit()


    #之所以需要这一步，是因为密码修改了 cookes已经修改了，这样就是无法通过验证，所以要更新cookies
    response = make_response(json.dumps(resp))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], '%s#%s' % (
        UserService.geneAuthCode(user_info), user_info.uid), 60 * 60 * 24 * 120)  # 保存120天
    return response




#logout的方法很简单，就是链接到登陆的界面同时删除你的cookies
@route_user.route("/logout")
def logout():
    response = make_response(redirect(UrlManager.buildUrl("/user/login")))
    response.delete_cookie(app.config['AUTH_COOKIE_NAME'])
    return response