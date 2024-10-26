from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app
from app.models.newsletter import Subscriber
from app.services.email_service import subscribed_to_newsletter, send_custom_email
from app import db
from flask_wtf.csrf import CSRFError
import requests
import re
import logging
from email_validator import validate_email, EmailNotValidError

email = Blueprint('email', __name__)
logger = logging.getLogger(__name__)

@email.route('/subscribe', methods=['POST'])
def subscribe():
	"""Subscribe to newsletter"""

	# Get reCaptcha secret key
	google_recaptcha_secret_key = current_app.config['RECAPTCHA_SECRETE_KEY']

	# Validate recaptcha response
	recaptcha_response = request.form.get('g-recaptcha-response')
	data = {
            'secret': google_recaptcha_secret_key,
            'response': recaptcha_response
        }
	try:
		response = requests.post(
			current_app.config['RECAPTCHA_VERIFY_URL'], data=data)
		 # Log the response for debugging
		recaptcha_result = response.json()
		print("reCAPTCHA verification result:", recaptcha_result)
		response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

		# Check if the reCaptcha request was successful
		if not response.json().get('success'):
			flash("CAPTCHA verification failed. Please try again.", "error")
			return redirect(url_for('main.index'))

	except requests.RequestException as e:
		logger.error(f"reCAPTCHA validation error: {e}")
		flash("Error verifying reCAPTCHA. Please try again later.", "error")
		return redirect(url_for('main.index'))

	try:
		email = request.form.get('email').strip().lower()

		# Validate email format using email_validator
		valid = validate_email(email)
		email = valid.email  # Normalized email

		existing_subscriber = Subscriber.query.filter_by(email=email).first()
		if existing_subscriber:
			if not existing_subscriber.is_active:
				existing_subscriber.is_active = True
				db.session.commit()
				flash("You've been re-subscribed!", "success")
			else:
				flash("You're already a subscriber!", "info")
			return redirect(url_for('main.index'))

		else:
			subscribed_to_newsletter(email)
			user = Subscriber(email=email, is_active=True)
			db.session.add(user)
			db.session.commit()
			flash("Subscription successful. Check your inbox.", "success")
			return redirect(url_for('main.index'))

	except EmailNotValidError as e:
		flash("Invalid email address. Please enter a valid email.", "error")
		return redirect(url_for('main.index'))

	except CSRFError as e:
		logger.error(f"CSRF Error: {e}")
		flash("Invalid CSRF token. Please refresh and try again.", "error")
		return redirect(url_for('main.index'))

	except Exception as e:
		logger.error(f"Subscription failed: {e}")
		db.session.rollback()
		flash(f"Failed to subscribe: {str(e)}", "error")
		return redirect(url_for('main.index'))





@email.route('/unsubscribe', methods=['GET','POST'])
def unsubscribe():
	"""Send unsubscribe email with resubscribe link"""
	email = request.args.get('email').strip().lower()
	existing_email = Subscriber.query.filter_by(email=email, is_active=True).first()
	resubscribe_url = f"{request.host_url}subscribe?email={email}"
	context = {'resubscribe_url': resubscribe_url}

	if existing_email and existing_email.is_active:
		existing_email.is_active = False
		db.session.commit()
		send_custom_email(
			subject="We're sorry to see you go",
			recipients=[email],
			template_name='email/unsubscribed_email.html',
			context=context
		)
		flash("You've been unsubscribed.", "success")
		return render_template('email/unsubscribe.html')
	else:
		flash("You were not subscribed or are already unsubscribed.", "info")
		return render_template('email/unsubscribe.html')

