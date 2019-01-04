# -*- coding: utf-8 -*-

from web.controllers.api import route_api
from  flask import request,jsonify,session
from application import  app,db
import requests,json

#import database
from common.models.member.Member import Member
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.course.WxShareHistory import  WxShareHistory


# import 获得现在时间的方法
from common.libs.Helper import getCurrentDate


#import lib里面的方法，有salt方法，有给腾讯服务器发请求的方法获取openid，有geneAuthCode方法用来制造token,
from common.libs.member.MemberService import MemberService





@route_api.route("/member/login",methods = [ "GET","POST" ]) #  1 GET 方法接受小程序发来的code和一些用户信息，比如nickname 等等
def login():
    resp = {'code':200,'msg':'success','data':{}} #建立一个空临时数据库
    req = request.values                          #获取又小程序发来的数据
    code = req['code'] if 'code' in req else ''   #把code从数据中摘出
    if not code or len(code)<1:                   #判断一下code的有效性
        resp['code'] =-1
        resp['msg'] = 'need code'
        return jsonify(resp)
    nickname = req['nickName'] if 'nickName' in req else ''    #提取出来用户的数据用于第三步的database 数据录入
    sex = req['gender'] if 'gender' in req else 0
    avatar = req['avatarUrl'] if 'avatarUrl' in req else ''
    #app.logger.info(nickname, sex, avatar)


    # 2 发送上面的code和小程序自己的ID和key到腾讯服务器去获得OpenID
    #url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code"\
    #    .format(app.config['MINA_APP']['appid'],app.config['MINA_APP']['appkey'],code)  #向腾讯服务器发送appid 和 appkey并获取他提供的OpenID
    #r = requests.get(url)         #获取腾讯服务器的data
    #res = json.loads(r.text)
    #openid= res['openid']         #将openID拿出来
    #app.logger.info(openid)
    #上面方法由于重复利用已经被搬到 common.libs.member.MemberService中了
    openid = MemberService.getWeChatOpenId(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = 'no openid'
        return jsonify(resp)

    #3 获取了openid ，用于本地数据库的注册，提前在common/models/member中建立了数据库
    bind_info = OauthMemberBind.query.filter_by(openid = openid , type =1 ).first() #查找用户是否已经注册
    #app.logger.info(bind_info)
    # 如果有注册
    if bind_info == None:
        # 如果没有注册
        model_member = Member()
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        model_member.salt = MemberService.geneSalt() #在lib里导入的方法
        model_member.update_time = model_member.create_time = getCurrentDate()
        db.session.add(model_member)
        db.session.commit()

        model_bind = OauthMemberBind()
        model_bind.member_id = model_member.id  #两个表share same memberId
        model_bind.type = 1
        model_bind.openid = openid
        model_bind.extra = ''
        model_bind.update_time = model_bind.create_time = getCurrentDate()
        db.session.add(model_bind)
        db.session.commit()
        resp['data'] = {'nikename': nickname}

        bind_info = model_bind #防止出现NoneType没有.member_id的属性的问题，因为两个表都有member_id,而且都是一样的

    #4 反馈前方的token值
    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    token = "%s#%s" % (MemberService.geneAuthCode(member_info), member_info.id)
    resp['data'] = {'token': token}
    return jsonify(resp)



@route_api.route("/member/check-reg", methods = [ "GET","POST" ])
def checkReg():
    # 1 获取前端发来信息并提出code
    resp = {'code': 200, 'msg': 'check-reg success', 'data': {}}      # 建立一个空临时数据库,用来返回给前端信息，相当于短信的作用
    req = request.values                                    # 获取又小程序发来的数据
    #app.logger.info("code " + req['code'])
    code = req['code'] if 'code' in req else ''             # 把code从数据中摘出
    if not code or len(code) < 1:                           # 判断一下code的有效性
        resp['code'] = -1
        resp['msg'] = 'need code'
        return jsonify(resp)                                #如果是这里成立，那么下面的最终return 的jsonify(resp) 就是这里的jsonify(resp)

    # 2 与微信服务器联系，得到openId
    openid = MemberService.getWeChatOpenId(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = 'no openid'
        return jsonify(resp)
    #app.logger.info("openid " + openid)


    # 3 当获取了openid我们判断是否绑定了我们的membership
    bind_info = OauthMemberBind.query.filter_by(openid=openid,type=1).first() #查看是否绑定了我们的账号
    if bind_info == None:                                      #如果没有绑定即没注册，回馈前台的如下信息
        resp['code'] = -1
        resp['msg'] = 'not bind'
        return jsonify(resp)

    member_info = Member.query.filter_by(id=bind_info.member_id).first()     #查看我们的member表里是否有这个信息
    if member_info == None:                                      #如果没有绑定即没注册，回馈前台的如下信息
        resp['code'] = -1
        resp['msg'] = 'not member'
        return jsonify(resp)

    #4 查询完毕后给前台返回一个加密的信息：token，因为我们这些私人信息我们用不到，只是为了验证。所以返回一个校验码就好了
    token = "%s#%s" % (MemberService.geneAuthCode(member_info), member_info.id)
    resp['data'] = {'token': token}
    return jsonify(resp)


@route_api.route("/member/share", methods = ["POST"])
def memberShare():
    resp = {'code': 200, 'msg': 'success', 'data': {}}


#获取网络传过来的值
    req = request.values
    url = req['url'] if 'url' in req else ''

    #从全局变量里获取member_info 是从拦截器里来的ApiInterceptor
    member_info = session.member_info

    #数据库初始化
    model_share = WxShareHistory()
    if member_info:
        model_share.member_id = member_info.id
    model_share.share_url = url
    model_share.created_time = getCurrentDate()
    db.session.add(model_share)
    db.session.commit()

    return jsonify(resp)

@route_api.route("/member/mobile", methods = ["POST","GET"])
def memberMobile():
    resp = {'code': 200, 'msg': 'success', 'data': {}}

    req = request.values
    mobile = int(req['mobile']) if 'mobile' in req else ''

    member_info = session.member_info

    if member_info == None:
        resp['code'] = -1
        resp['msg'] = '请登录~~'
        return jsonify(resp)

    model_member = Member.query.filter_by(id = member_info.id).first()
    if model_member.mobile == mobile:
        return jsonify(resp)
    model_member.mobile = mobile
    db.session.add(model_member)
    db.session.commit()
    return jsonify(resp)


@route_api.route("/member/name", methods = ["POST","GET"])
def memberName():
    resp = {'code': 200, 'msg': 'success', 'data': {}}

    req = request.values
    name = req['name'] if 'name' in req else ''

    member_info = session.member_info

    if member_info == None:
        resp['code'] = -1
        resp['msg'] = '请登录~~'
        return jsonify(resp)

    model_member = Member.query.filter_by(id = member_info.id).first()
    if model_member.reg_ip == name:
        return jsonify(resp)
    model_member.reg_ip = name
    db.session.add(model_member)
    db.session.commit()
    return jsonify(resp)