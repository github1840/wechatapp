# -*- coding: utf-8 -*-
SERVER_PORT = 8000
DEBUG = False
SQLALCHEMY_ECHO = False

SQLALCHEMY_DATABASE_URI = 'mysql://root:dong382008@127.0.0.1/education_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False


MINA_APP = {

    'appid':'wx11346fb4601f2af2',
    'appkey':'c0c58746636146d643229d57595e9fd4'

}

AUTH_COOKIE_NAME="mooc_food"

IGNORE_URLS = [
    "^/user/login"

]

IGNORE_CHECK_LOGIN_URLS = [
    "^/static",
    "^/favicon.ico"
]

API_IGNORE_URLS = [
    "^/api"
]

PAGE_SIZE = 50

PAGE_DISPLAY = 10

STATUS_MAPPING={

    '1':'正常',
    '0':'已删除'
}

UPLOAD = {
    'ext':['jpg','gif','bmp','jpeg','png'],
    'prefix_path':'/web/static/upload/',
    'prefix_url':'/static/upload/'


}

APP = {
    'domain': 'http://172.16.168.244:8000'

}