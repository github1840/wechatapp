# -*- coding: utf-8 -*-
from werkzeug.utils import secure_filename
from application import app,db
from common.libs.Helper import getCurrentDate
from common.models.Image import Image
import datetime
import os,stat,uuid


class UploadService():
    @staticmethod
    def uploadByFile(file):

        resp = {'code':200,'msg':'上传成功','data':{}}


        filename = secure_filename(file.filename)   #获得安全的文件名
        ext = filename.rsplit('.',1)[1]             #截取文件名的拓展名，格式
        config_upload = app.config['UPLOAD']        #获取app 中格式要求
        if ext not in config_upload['ext']:
            resp['code'] = -1
            resp['msg'] = '不允许扩展类型文件'
            return resp


        root_path = app.root_path + config_upload['prefix_path']      #文件储存的路径存在了static中的upload文件夹里
        file_dir = datetime.datetime.now().strftime("%Y%m%d")           #设置存储文件名称，用时间命名
        save_dir = root_path + file_dir                                 #完整的文件路径
        if not os.path.exists(save_dir):                                #判断是否有该路径
            os.mkdir(save_dir)                                          #如果没有就生成一个
            os.chmod(save_dir,stat.S_IRWXU|stat.S_IRGRP|stat.S_IRWXO)   #赋予权限

        file_name = str(uuid.uuid4()).replace("-","") + "." + ext       #file名，uuid用来生成文件名，用时间和硬件名
        file.save("{0}/{1}".format(save_dir,file_name))                 #存储文件

        # ======= 上传的图片存入数据库 =========

        model_image = Image()
        model_image.file_key = file_dir + '/' + file_name
        model_image.created_time = getCurrentDate()
        db.session.add(model_image)
        db.session.commit()


        resp['data'] = {
            'file_key': file_dir + '/' + file_name
        }

        return resp