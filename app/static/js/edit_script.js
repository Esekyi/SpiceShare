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
});


// handle upload
document.addEventListener('DOMContentLoaded', function ()
{
	document.getElementById('add-photo-btn').addEventListener('click', function (event)
	{
		event.preventDefault(); // Prevent default button action
		document.getElementById('image-input').click();
	});

	document.getElementById('image-input').addEventListener('change', function (event)
	{
		const file = event.target.files[0];
		if (file)
		{
			const reader = new FileReader();
			reader.onload = function (e)
			{
				const imagePreview = document.getElementById('image-preview');
				console.log('Image data URL:', e.target.result); // Debugging
				imagePreview.src = e.target.result;
				imagePreview.style.display = 'block'; // Show the image preview
			};
			reader.readAsDataURL(file);
		}
	});

});

// handle form drop down - not using select input
function toggleDropdown()
{
	const dropdownMenu = document.getElementById('dropdownMenu');
	dropdownMenu.classList.toggle('show');
}

function selectCategory(categoryName, categoryId)
{
	const categoryInput = document.getElementById('categoryInput');
	const categoryIdInput = document.getElementById('categoryIdInput');

	// Set the selected category name in the visible input
	categoryInput.value = categoryName;
	// Set the selected category ID in the hidden input
	categoryIdInput.value = categoryId;
	toggleDropdown();
}

// Close dropdown if clicked outside
document.addEventListener('click', function (event)
{
	const dropdownMenu = document.getElementById('dropdownMenu');
	const categoryInput = document.getElementById('categoryInput');
	if (!categoryInput.contains(event.target) && !dropdownMenu.contains(event.target))
	{
		dropdownMenu.classList.remove('show');
	}
});

function updateStepNumbers()
{
	const directionCards = document.querySelectorAll('.direction-card .step-number');
	directionCards.forEach((step, index) =>
	{
		step.textContent = index + 1;
	});
}

function addIngredient()
{
	const ingredientCard = document.createElement('div');
	ingredientCard.className = 'recipe-card';
	ingredientCard.innerHTML = `
		<div class="input-group ingredient-card overflow-hidden whitespace-nowrap">
			<input type="text" name="ingredients[]" class="w-full overflow-ellipsis p-2 border border-gray-300 rounded"
						placeholder="Add new ingredient">
			<button type="button" class="text-red-500 hover:text-red-700" onclick="removeIngredient(this)">×</button>
		</div>
    `;
	document.getElementById('ingredients-list').appendChild(ingredientCard);
}

function removeIngredient(element)
{
	element.closest('.recipe-card').remove();
}

function addDirection()
{
	const directionCard = document.createElement('div');
	directionCard.className = 'recipe-card mb-2';
	directionCard.innerHTML = `
		<div class="input-group direction-card overflow-hidden whitespace-nowrap">
			<span class="step-number">{{ loop.index }}</span>
			<input type="text" name="instructions[]" class="w-full p-2 border border-gray-300 rounded overflow-ellipsis"
						" placeholder="Add new instruction" required>
			<button type="button" class="text-red-500 hover:text-red-700" onclick="removeDirection(this)">×</button>
		</div>
    `;
	document.getElementById('directions-list').appendChild(directionCard);
	updateStepNumbers()
}

function removeDirection(element)
{
	element.closest('.recipe-card').remove();
	updateStepNumbers()
}

function initializeSortable()
{
	new Sortable(document.getElementById('ingredients-list'), {
		animation: 150,
		ghostClass: 'bg-yellow-100',
		onEnd: function ()
		{
			updateStepNumbers();  // Update step numbers after sorting
		}
	});

	new Sortable(document.getElementById('directions-list'), {
		animation: 150,
		ghostClass: 'bg-yellow-100'
	});
}

document.addEventListener('DOMContentLoaded', function ()
{
	initializeSortable()
	updateStepNumbers();
	// Handle form submission and log to console
	document.getElementById('recipe-form').addEventListener('submit', function (event)
	{
		//event.preventDefault(); // Prevent form from submitting

		// Get all ingredients
		const ingredients = Array.from(document.querySelectorAll('.ingredient-card input')).map(
			input => input.value).filter(value => value.trim() != '');

		// Get all directions
		const directions = Array.from(document.querySelectorAll('.direction-card input')).map(
			input => input.value).filter(value => value.trim() != '');

		// Log the data to the console
		console.log('Ingredients:', ingredients);
		console.log('Directions:', directions);

		// You can remove or comment out this part when you want to submit to the backend
		this.submit();  // Uncomment to submit the form to the backend after testing
	});
});




