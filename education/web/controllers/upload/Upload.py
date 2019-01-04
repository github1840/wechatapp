# -*- coding: utf-8 -*-
from flask import Blueprint,request,jsonify
from application import  app
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.models.Image import Image
import re,json

route_upload = Blueprint( 'upload_page',__name__ )

@route_upload.route("/ueditor", methods = ['GET','POST'])
def ueditor():
    req = request.values
    action = req['action'] if 'action' in req else ''

    if action == "config":
        root_path = app.root_path
        config_path = "{0}/web/static/plugins/ueditor/upload_config.json".format(root_path)
        with open(config_path, encoding="utf-8") as fp:
            try:
                config_data = json.loads(re.sub(r'\/\*.*\*/', '', fp.read()))
            except:
                config_data = {}
        return jsonify(config_data)

    if action == "uploadimage":
        return uploadImage()   #👇 函数

    if action == "listimage":
        return listImage()

    return "upload"



#ueditor 内部用于保存和展示照片的函数
def uploadImage():
    resp={'state':'SUCCESS','url':'','title':'','original':''}
    file_target = request.files                                          #可以通过 app.logger.info(file_target)来看看到底上传的文件是啥
    upfile = file_target['upfile'] if 'upfile' in file_target else None  #upfile来自set.html中

    if upfile is None:
        resp['state'] = '上传失败'
        return jsonify(resp)

    ret = UploadService.uploadByFile(upfile)                             #UploadService() 函数在common.libs中
    if ret['code'] !=200:
        resp['state'] = '上传失败：' + "ret['msg']"
        return jsonify(resp)

    resp['url'] = UrlManager.buildImageUrl(ret['data']['file_key'])        #UrlManager.buildImageUrl函数在common.libs中

    return jsonify(resp)                                                   # 因为有POST方法所以会返回前台resp与js没有关系

def listImage():
    resp = {'state':'SUCCESS', 'list':[],'start':0,'total':0}

    #========点击在线管理会返回一个response，里面需要statue list 开始点和total ，需要把这些东西从request中取出并赋值再发回去

    #取值
    req = request.values

    start = int(req['start']) if 'start' in req else 0
    page_size = int(req['size']) if 'size' in req else 20


    #数据库中读取，每一页为一个单位读取 （分页）
    query = Image.query
    if start > 0:
        query = query.filter(Image.id < start )

    list = query.order_by(Image.id.desc()).limit(page_size).all()
    images = []

      #组成list
    if list:
        for item in list:
            images.append({'url': UrlManager.buildImageUrl(item.file_key)})
            start = item.id

    resp['list'] = images
    resp['start'] = start
    resp['total'] = len(images)

    return jsonify(resp)


#用于封面上传
#food/set.html中的form中的action指到这里
#相关文件，food/set.html（iframe，food/set.js（上传封面函数）
@route_upload.route("/pic", methods = ['GET','POST'])
def uploadPic():
    file_target = request.files
    upfile = file_target['pic'] if 'pic' in file_target else None  # pic 是来自于set.html中的52行form中的input的name

    #===========👇的返回方法与uploadImage 中的resp完全不同，返回的是js这个事件=============

    callback_target = 'window.parent.upload'
    if upfile is None:
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target, "上传失败")

    ret = UploadService.uploadByFile(upfile)   #上传图片
    if ret['code'] != 200:
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target, "上传失败：" + ret['msg'])

    return "<script type='text/javascript'>{0}.success('{1}')</script>".format(callback_target, ret['data']['file_key'])
