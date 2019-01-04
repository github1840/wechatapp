Python Flask订餐系统
=====================
##启动
* export ops_config=local|production && python manage.py runserver

##flask-sqlacodegen

        flask-sqlacodegen 'mysql://root:123456@127.0.0.1/education_db' --outfile "common/models/model.py"  --flask
        flask-sqlacodegen 'mysql://root:123456@127.0.0.1/education_db' --tables user --outfile "common/models/user.py"  --flask

        flask-sqlacodegen 'mysql://root:dong382008@127.0.0.1/education_db' --tables user --outfile "common/models/Course/Course.py"  --flask
        flask-sqlacodegen 'mysql://root:dong382008@127.0.0.1/education_db' --tables user --outfile "common/models/Course/CourseCat.py"  --flask
        flask-sqlacodegen 'mysql://root:dong382008@127.0.0.1/education_db' --tables user --outfile "common/models/Course/CourseStockChangeLog.py"  --flask