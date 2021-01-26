from newswriter.forms import NewUserForm
from newswriter.models.security import User, Permission, Role
from newswriter.models.content import Article, Board
from newswriter.permissions import admin_perm
from newswriter import db
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_login import current_user, login_required
from flask import url_for, redirect, request


class MyAdminIndexView(AdminIndexView):
    
    @expose('/')
    @login_required
    @admin_perm.require(http_exception=403)
    def index(self):
        if current_user.is_authenticated is False:
            return redirect(
                url_for('users.login', next=request.url))

        return super(MyAdminIndexView, self).index()


class MySecureModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated and admin_perm.can()


class UserView(MySecureModelView):
    column_exclude_list = ('password_hash',)
    form_excluded_columns = ('password_hash', )

    def __init__(self):
        super().__init__(User, db.session, category='Securiry')

    @expose('/new/', methods=['GET', 'POST'])
    def create_view(self):
        form = NewUserForm()

        if form.validate_on_submit():
            u = User()
            u.username = form.username.data
            u.name = form.name.data
            u.email = form.email.data
            u.set_password(form.password1.data)
            db.session.add(u)
            db.session.commit()
            if '_add_another' in request.form:
                return redirect(url_for('user.create_view'))
            else:
                return redirect(url_for('user.index_view'))


        return self.render('users/create_user.html', form=form)


class RoleView(MySecureModelView):
    inline_models = (Permission,)

    def __init__(self):
        super().__init__(Role, db.session, category='Securiry')


class PermissionView(MySecureModelView):

    def __init__(self):
        super().__init__(Permission, db.session, category='Securiry')


class BoardsAdminView(MySecureModelView):
    column_display_pk = True
    form_columns = ('name', )

    def __init__(self):
        super().__init__(
            Board, db.session, category='Content')


class ArticleAdminView(MySecureModelView):

    def __init__(self):
        super().__init__(Article, db.session, category='Content')
