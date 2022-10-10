import os.path as op
from flaskproj import app, db
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from .models import Orderuser, Product, Usercard, Userprofile, UserPosts
from .views import current_user


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        try:
            if current_user.name == 'admin' and current_user.psw == 'admin':
                return True 
        except:
            pass

admin = Admin(app, name='shop', template_mode='bootstrap4',index_view=MyAdminIndexView())


class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        user_amount = Userprofile.query.all()
        return self.render('admin/analytics_index.html',user_amount=len(user_amount))


path = op.join(op.dirname(__file__),'static')
admin.add_view(FileAdmin(path,'/static/',name='Static Files'))
admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
admin.add_view(ModelView(Userprofile, db.session))
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Orderuser, db.session))
admin.add_view(ModelView(Usercard, db.session))
admin.add_view(ModelView(UserPosts, db.session))

