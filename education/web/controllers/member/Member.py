# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,session,request,redirect, jsonify
from common.models.member.Member import Member
from common.libs.UrlManager import UrlManager
from application import app,db
from common.libs.Helper import iPagination,getCurrentDate

route_member = Blueprint( 'member_page',__name__ )

@route_member.route( "/index" )
def index():
    current_user = session.current_user
    current = "index"

    query = Member.query
    # 1.分页
    req = request.values  # 前端获取pages
    page = int(req['p']) if ('p' in req and req['p']) else 1
     #填写page参数
    page_params = {

        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }
    pages = iPagination(page_params)  # 计算出page数量
    offset = (page - 1) * app.config['PAGE_SIZE']  # 计算下一页的开头

    # 2.查询
    status_mapping = app.config['STATUS_MAPPING']
    # 2.1 关键字搜索
    if 'mix_kw' in req:
        query = query.filter(Member.nickname.ilike("%{0}".format(req['mix_kw'])))

    #2.2 类型搜索
    if 'status' in req and int(req['status']) > -1:
        query = query.filter(Member.status == int(req['status']))

    # 3.展示用户列表,取出全部的倒叙排列
    list = query.order_by(Member.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()

    return render_template( "member/index.html",current_user=current_user,pages=pages,list=list,current=current,status_mapping=status_mapping  )


@route_member.route( "/info",methods = ["GET", "POST"] )
def info():
    current_user = session.current_user
    req = request.args                  # index.html中<a href="{{ buildUrl('/member/info') }}?id={{item.id}}"> 中传过来的id
    id = int(req.get("id",0))
    reback_url = UrlManager.buildUrl("/member/index")

    if id < 1:
        return redirect(reback_url)

    info = Member.query.filter_by(id = id).first()
    if not info:
        return redirect(reback_url)


    return render_template( "member/info.html",current_user=current_user,info = info )

@route_member.route( "/set" ,methods = ["GET", "POST"])
def set():
    current_user = session.current_user

    #当方法是GET时
    if request.method =="GET":
        current = 'index'
        req = request.args
        id = int(req.get("id",0))
        reback_url = UrlManager.buildUrl("/member/index")
        #校验
        if id < 1:
            return redirect(reback_url)

        info = Member.query.filter_by(id=id).first()
        if not info:
            return redirect(reback_url)

        if info.status != 1:
            return redirect(reback_url)

        return render_template( "member/set.html",current_user=current_user,current = current,info = info)

    # 当方法是POST时，其中也会有GET方法的应用
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    id = req['id'] if 'id' in req else "0"
    nickname = req['nickname'] if 'nickname' in req else ""
    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名~~"
        return jsonify(resp)
    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "会员不存在~~"
        return jsonify(resp)
    #修改数据库
    member_info.nickname = nickname
    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()
    #跳回首页 相当redirect 但是靠ajax来实现
    return jsonify(resp)  # 当返回成功操作 code==200 , resp返回，set.js 的 ajax 中的success函数工作，window.location.href = common_ops.buildUrl("/member/index")使得返回会员首页

@route_member.route( "/comment")
def comment():

    current_user = session.current_user
    return render_template( "member/comment.html",current_user=current_user )

@route_member.route( "/ops",methods = ["POST"])
def ops():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values


    id = req['id'] if 'id' in req else 0
    act = req ['act'] if 'act' in req else ''
    #校验
    if not id :
        resp ['code'] = -1
        resp ['msg'] ="请选择要操作的账户"
        return jsonify(resp)

    if act not in ['remove','recover']:
        resp ['code'] = -1
        resp ['msg'] ="操作有误请重试"
        return jsonify(resp)
    member_info = Member.query.filter_by(id=id).first()

    if not member_info:
        resp['code'] = -1
        resp['msg'] = "账户不存在"
        return jsonify(resp)

    #操作
    if act == "remove":
        member_info.status = 0
    elif act == "recover":
        member_info.status = 1
    #更新数据库
    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)