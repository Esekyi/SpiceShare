// Function to hide the flash message after 3 seconds
setTimeout(function ()
{
	const flashMessageBox = document.getElementById('flashMessageBox');
	if (flashMessageBox)
	{
		flashMessageBox.style.opacity = '0'; // Fade out
		setTimeout(function ()
		{
			flashMessageBox.remove(); // Remove from DOM after fade out
		}, 500); // 0.5s to match the CSS transition duration
	}
}, 5000); // Display for 5 seconds

// password view toggle function
function togglePasswordVisibility(id, event)
{
	const input = document.getElementById(id);
	const button = event.target;
	if (input.type === "password")
	{
		input.type = "text";
		button.textContent = "🙈";
	} else
	{
		input.type = "password";
		button.textContent = "👁️";
	}
}

function onSubmit(token)
{
	document.querySelector('form').submit(); // Submit the form after reCAPTCHA validation
}
