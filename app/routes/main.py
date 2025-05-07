# app/routes/main.py
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page."""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')