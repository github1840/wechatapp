# -*- coding: utf-8 -*-

import hashlib,requests,random,string,json
from application import app

class MemberService():

    @staticmethod
    def geneAuthCode(member_info = None ):
        m = hashlib.md5()
        str = "%s-%s-%s" % (member_info.id,member_info.salt,member_info.status)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def geneSalt( length = 16 ):
        keylist = [ random.choice( ( string.ascii_letters + string.digits ) ) for i in range( length ) ]
        return ( "".join( keylist ) )

    @staticmethod
    def getWeChatOpenId(code):
        url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code" \
               .format(app.config['MINA_APP']['appid'],app.config['MINA_APP']['appkey'],code)  #向腾讯服务器发送appid 和 appkey并获取他提供的OpenID
        r = requests.get(url)         #获取腾讯服务器的data
        res = json.loads(r.text)
        openid = None
        if 'openid' in res:
            openid= res['openid']         #将openID拿出来

        return openid