"""Simple blueprint to register the frontend template"""

from flask import Blueprint, render_template

frontend = Blueprint('frontend', __name__, template_folder='frontend', static_folder='frontend/dist/static')

@frontend.route('/')
def index():
    # keep the /dist to avoid template name collision w/ main app
    return render_template('dist/index.html')
