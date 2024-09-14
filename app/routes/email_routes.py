from flask import Blueprint, request, flash, redirect, url_for, render_template
from app.models.newsletter import Subscriber
from app.services.email_service import subscribed_to_newsletter, send_custom_email
from app import db

email = Blueprint('email', __name__)

@email.route('/subscribe', methods=['POST'])
def subscribe():
	email = request.form.get('email').strip().lower()

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
		try:
			user = Subscriber(email=email, is_active=True)
			db.session.add(user)
			db.session.commit()
			flash("Subscription successful. Check your inbox.", "success")
			return redirect(url_for('main.index'))

		except Exception as e:
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

