import typing

from app.admin.views import (
    AdminCurrentView, 
    AdminLoginView, 
    AdminListView,
    AdminAddView,
    Index,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


# BASE_DIR = os.path.dirname (os.path.dirname (os.path.abspath (__ file__))) # путь к проекту
# STATIC_DIR = os.path.join (BASE_DIR, 'static') # статический путь к файлу
# TEMPLATE_DIR = os.path.join (BASE_DIR, 'template') # шаблон HTML-путь   


def setup_routes(app: "Application"):

    app.router.add_view("/", Index, name = "Index")
    app.router.add_view("/login", AdminLoginView, name = "AdminLoginView")
    app.router.add_view("/admins", AdminListView, name = "AdminListView")
    app.router.add_view("/admins.add", AdminAddView, name = "AdminAddView")


    #app.router.add_get("/register", register) #так назначаются функции ответа на запрос
    #app.router.add_get("/login", login)



    app.router.add_static("/static/", path="static", name='static')