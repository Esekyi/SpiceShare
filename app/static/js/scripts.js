document.addEventListener('DOMContentLoaded', function ()
{
	const flashMessages = document.querySelectorAll('.flash-message');

	flashMessages.forEach(function (flash)
	{
		setTimeout(function ()
		{
			flash.style.display = 'none';
		}, 5000); // Flash message disappears after 5 seconds
	});

	// Toggle mobile menu
	document.getElementById('mobile-menu-button').addEventListener('click', function ()
	{
		var menu = document.getElementById('mobile-menu');
		menu.classList.toggle('hidden');
	});
});
