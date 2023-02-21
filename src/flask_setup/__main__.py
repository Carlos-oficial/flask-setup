import os
from flask_setup import lib, files

pkg_path = os.path.dirname(__file__)
cwd = os.getcwd()
valid = False

while not valid:
    app_name = input("What's your app called? :")
    valid = lib.validate_app_name(app_name)
    if not valid:
        print("invalid app name")
    if os.path.exists(app_name):
        print("./" + app_name + " already exists")
        valid = False

app_path = os.path.join(cwd, app_name)
lib.mkdir_p(app_path)
os.chdir(app_path)
lib.mkdirs("templates", "static", "db", "lib")
lib.mkdirs("static/icons", "static/scripts")
lib.parse_and_replace(
    files.BASE_HTML,
    os.path.join(app_path, "templates", "base.html"),
    r"{{$APP_NAME}}",
    app_name,
)
print("templates and static paths created")
create_auth_bp = valid = False
while not valid:
    auth_bp = input(
        "Would you like to include an auth blueprint? (visit https://flask.palletsprojects.com/en/2.2.x/blueprints/ for blueprint documentation) y/n"
    )
    valid = auth_bp in ["Y", "N", "y", "n"]
    create_auth_bp = auth_bp in ["Y", "y"]
    if not valid:
        print("y/n?")

with open("__init__.py", "w") as f:
    f.write(files.init_py(auth=create_auth_bp))

with open("routes.py", "w") as f:
    f.write(files.ROUTES_PY)

with open("api.py", "w") as f:
    f.write(files.API_PY)


with open("db/db.py", "w") as f:
    f.write(files.DB_PY)

with open("db/schema.sql",'w') as _: pass
if create_auth_bp:
    with open("auth.py", "w") as f:
        f.write(files.AUTH_PY)
    with open("db/schema.sql",'w') as f:
        f.write(files.AUTH_TABLE)
    os.mkdir('templates/auth')
    with open('templates/auth/base_form.html','w') as f: f.write(files.BASE_FORM_HTML)
    with open('templates/auth/login.html','w') as f: f.write(files.LOGIN_HTML)
    with open('templates/auth/register.html','w') as f: f.write(files.REGISTER_HTML)
