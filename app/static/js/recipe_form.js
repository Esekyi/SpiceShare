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



// Add ingredient functionality
function addIngredient()
{
	const ingredientCard = document.createElement('div');
	ingredientCard.className = 'recipe-card';
	ingredientCard.innerHTML = `
		<div class="ingredient-card bg-gray-50 p-3 rounded-lg">
			<div class="grid grid-cols-12 gap-2 items-center">
				<div class="col-span-2">
					<input type="number" step="0.25" name="ingredient_quantities[]"
						   class="w-full p-2 border border-gray-300 rounded text-sm"
						   placeholder="1" min="0">
					<label class="text-xs text-gray-500">Quantity</label>
				</div>
				<div class="col-span-2">
					<select name="ingredient_units[]" class="w-full p-2 border border-gray-300 rounded text-sm">
						<option value="">Unit</option>
						<option value="cup">cup</option>
						<option value="cups">cups</option>
						<option value="tbsp">tbsp</option>
						<option value="tsp">tsp</option>
						<option value="oz">oz</option>
						<option value="lb">lb</option>
						<option value="g">g</option>
						<option value="kg">kg</option>
						<option value="ml">ml</option>
						<option value="l">l</option>
						<option value="piece">piece</option>
						<option value="pieces">pieces</option>
						<option value="clove">clove</option>
						<option value="cloves">cloves</option>
						<option value="slice">slice</option>
						<option value="slices">slices</option>
					</select>
					<label class="text-xs text-gray-500">Unit</label>
				</div>
				<div class="col-span-7">
					<input type="text" name="ingredients[]"
						   class="w-full p-2 border border-gray-300 rounded"
						   placeholder="ingredient name" required>
					<label class="text-xs text-gray-500">Ingredient</label>
				</div>
				<div class="col-span-1 text-center">
					<button type="button" class="text-red-500 hover:text-red-700 text-xl"
							onclick="removeIngredient(this)" title="Remove ingredient">×</button>
				</div>
			</div>
		</div>
    `;
	document.getElementById('ingredients-list').appendChild(ingredientCard);
}

function removeIngredient(element)
{
	element.closest('.recipe-card').remove();
}

// Add direction functionality
function addDirection()
{
	const directionCard = document.createElement('div');
	directionCard.className = 'recipe-card';
	directionCard.innerHTML = `
                <div class="input-group direction-card mt-2">
                    <input type="text" name="instructions[]" class="w-full p-2 border border-gray-300 rounded" placeholder="Add new Instruction">
                    <button type="button" class="text-red-500 hover:text-red-700" onclick="removeDirection(this)">×</button>
                </div>
            `;
	document.getElementById('directions-list').appendChild(directionCard);
}

function removeDirection(element)
{
	element.closest('.recipe-card').remove();
}

//SortableJS Script for Drag-and-Drop
// Enable sorting for ingredients and directions
new Sortable(document.getElementById('ingredients-list'), {
	animation: 150,
	ghostClass: 'bg-yellow-100'
});
new Sortable(document.getElementById('directions-list'), {
	animation: 150,
	ghostClass: 'bg-yellow-100'
});



document.addEventListener('DOMContentLoaded', function ()
{
	// Handle form submission and log to console
	document.getElementById('recipe-form').addEventListener('submit', function (event)
	{
		// event.preventDefault(); // Prevent form from submitting
	
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
