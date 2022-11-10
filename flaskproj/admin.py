import os.path as op
import os
import random

from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from flask_admin import form

from flaskproj import app, db

from .models import Orderuser, Product, UserPosts, Userprofile
from .views import current_user


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass
    


admin = Admin(
    app,
    name="",
    template_mode="bootstrap3",
    index_view=MyAdminIndexView(name="Админка",menu_icon_type='glyph', menu_icon_value='glyphicon-home'),
)


class AnalyticsView(BaseView):
    @expose("/")
    def index(self):
        user_amount = Userprofile.query.all()
        return self.render("admin/analytics_index.html", user_amount=len(user_amount))

    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


class UserprofileView(ModelView):
    column_searchable_list = ["name", "mail"]
    column_filters = ["data_registered", "confirmed"]
    column_sortable_list = ["data_registered", "name"]
    column_editable_list = ["admin", "confirmed"]
    column_labels = dict(
        name="логин",
        psw="пароль",
        data_registered="дата регистрации",
        admin="права админа",
        confirmed="подтверждение почты",
        mail="почта",
        user_bascet="корзина",
        user_order="заказы",
        user_post="сообщения",
    )
    create_modal = True
    edit_modal = True
 

    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


class UserPostsView(ModelView):
    column_labels = dict(
        title="Заголовок", body="Текст", date="Дата", user_name="Автор"
    )
    column_searchable_list = ["user_name"]
    column_filters = ["user_name"]
    column_editable_list = ["title", "body"]
    create_modal = True
    edit_modal = True
    column_descriptions = dict(user_name="автор отправитель")
  

    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


class ProductView(ModelView):
    column_labels = dict(
        name="товар",
        image="изображение",
        price="цена",
        product_story="описание",
        amount="количество",
    )
    column_descriptions = dict(image="хранятся в /static/")
    column_searchable_list = ["name", "product_story", "price"]
    column_filter = ["name", "amount", "price"]
    column_editable_list = ["price"]
    create_modal = True
    edit_modal = True
    path = op.abspath(os.getcwd()+ '/flaskproj/static')
    form_extra_fields = {
        'image': form.ImageUploadField('изображение',base_path=path)
    }
   
    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


class OrderuserView(ModelView):
    column_display_pk = True
    column_descriptions = dict(
        list_product="один список - одна позиция: [товар, цена, количество]"
    )
    column_searchable_list = ["order_price"]
    column_sortable_list = ["order_price"]
    column_labels = dict(
        date="дата исполнения",
        list_product="данные заказа",
        order_price="сумма",
        invoice_id="идентификатор оплаты",
    )

    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass



path = op.join(op.dirname(__file__), "static/")
admin.add_view(AnalyticsView(name="Аналитика", endpoint="analytics",menu_icon_type='glyph', menu_icon_value='glyphicon-eye-open'))
admin.add_view(FileAdmin(path, "/static/", name="Загрузка файлов",menu_icon_type='glyph', menu_icon_value='glyphicon-circle-arrow-down'))
admin.add_view(UserprofileView(Userprofile, db.session, name="Пользователи",menu_icon_type='glyph', menu_icon_value='glyphicon-user'))
admin.add_view(ProductView(Product, db.session, name="Товары"))
admin.add_view(OrderuserView(Orderuser, db.session, name="Заказы"))
admin.add_view(UserPostsView(UserPosts, db.session, name="Обратная связь"))

