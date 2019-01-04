# -*- coding: utf-8 -*-
from flask import Blueprint,render_template
from flask import session
from application import app


route_index = Blueprint( 'index_page',__name__ )

@route_index.route("/")
def index():
    current_user = session.current_user
    app.logger.info(session)
    return render_template( "index/index.html" , current_user = current_user )
