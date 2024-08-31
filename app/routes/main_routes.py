from flask import Blueprint, render_template, flash

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
	return render_template('index.html')