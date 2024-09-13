from app import mail
from flask_mail import Message
from flask import render_template, current_app, url_for, request
from flask_limiter import Limiter
from threading import Thread
import smtplib

# Rate Limiter setup (10 emails per minute)
limiter = Limiter(key_func=lambda: request.remote_addr,
                  default_limits=["10 per minute"])

# Function to send email asynchronously
def send_async_email(app, msg):
	"""Function to send email asynchronously"""
	with app.app_context():
		try:
			mail.send(msg)
			app.logger.info(f"Email sent to {msg.recipients}")
		except smtplib.SMTPException as e:
			app.logger.error(f"Failed to send email: {str(e)}")
			print(f"Failed to send email: {str(e)}")

# Function to send email with threading
def send_email(subject, recipients, template):
	"""Function to send email with threading"""
	app = current_app._get_current_object()
	msg = Message(subject, recipients=recipients)
	msg.html = template
	try:
		Thread(target=send_async_email, args=(app, msg)).start()
		current_app.logger.info(f"Email send initiated for {recipients}")  # Log successful send
	except Exception as e:
		# Log the error or handle it as needed
		current_app.logger.error(f"Failed to send email: {e}")
		print(f"Failed to send email: {e}")
		return False
	return True


# Rate-limited function to send newsletter subscription email
@limiter.limit("5 per minute")
def subscribed_to_newsletter(email):
	"""Send newsletter subscription email"""
	html_body = render_template(
		'email/subscribed_email.html',
		unsubscribe_url = url_for('email.unsubscribe', email=email, _external=True)
	)
	return send_email(
		subject='Welcome to SpiceShare',
		recipients=[email],
		template=html_body
	)


@limiter.limit("5 per minute")
def send_newsletter_email(user, recipe, recipe_link, unsubscribe_link=None):
	"""Send newsletter email"""
	unsubscribe_url = url_for('email.unsubscribe', email=user.email, _external=True)
	html_body = render_template(
		'email/newsletter.html',
		recipe_title=recipe.title,
		recipe_link=recipe_link,
		unsubscribe_link=unsubscribe_link or unsubscribe_url,
		description = recipe.description,
		recipe_image=recipe.image_url
	)
	return send_email(
		subject='New Recipe Alert!',
		recipients=[user.email],
		template=html_body
	)


@limiter.limit("5 per minute")
def send_custom_email(subject, recipients, template_name, context):
	"""
	a flexible function that can be used to send any type of email by specifying a template and providing the necessary context.
	Rate-limited function to send newsletter email
	Example: limit this function to 5 emails per minute per IP
	
	Args:
        subject (str): The subject for the email.
        recipients (list): The recipients of the email.
		template_name (filename): the html file for the email
		context (list- keyworded): specify other variables to pass to html file eg, email=email

    Returns:
        dict: A dictionary containing paginated recipes and pagination info.
	"""
	html_body = render_template(template_name, **context)
	return send_email(
		subject=subject,
		recipients=recipients,
		template=html_body
	)




