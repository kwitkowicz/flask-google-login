from flask import Blueprint
from flask import current_app as app
from flask import render_template
from flask_login import current_user

home_blueprint = Blueprint('home_blueprint', __name__, template_folder='templates', static_folder='static')


@home_blueprint.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'

