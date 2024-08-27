document.addEventListener('DOMContentLoaded', function ()
{
	const ingredientsList = document.getElementById('ingredients-list');
	const addIngredientBtn = document.getElementById('add-ingredient-btn');
	const directionsList = document.getElementById('directions-list');
	const addDirectionBtn = document.getElementById('add-direction-btn');

	addIngredientBtn.addEventListener('click', function ()
	{
		const ingredientRow = document.createElement('div');
		ingredientRow.classList.add('ingredient-row');

		ingredientRow.innerHTML = `
            <input type="text" name="ingredients[]" class="ingredient-input" placeholder="Enter ingredient" required />
            <button type="button" class="remove-ingredient-btn">X</button>
        `;

		ingredientsList.appendChild(ingredientRow);

		// Add event listener to the remove button
		ingredientRow.querySelector('.remove-ingredient-btn').addEventListener('click', function ()
		{
			ingredientsList.removeChild(ingredientRow);
		});
	});

	addDirectionBtn.addEventListener('click', function ()
	{
		const directionCount = directionsList.children.length + 1;
		const directionRow = document.createElement('div');
		directionRow.classList.add('direction-row');

		directionRow.innerHTML = `
            <div class="direction-step-number">${directionCount}</div>
            <textarea name="directions[]" class="direction-input" placeholder="Enter instruction..." required></textarea>
            <button type="button" class="remove-direction-btn">X</button>
        `;

		directionsList.appendChild(directionRow);

		// Add event listener to the remove button
		directionRow.querySelector('.remove-direction-btn').addEventListener('click', function ()
		{
			directionsList.removeChild(directionRow);
			updateStepNumbers();
		});
	});

	function updateStepNumbers()
	{
		document.querySelectorAll('.direction-step-number').forEach((step, index) =>
		{
			step.textContent = index + 1;
		});
	}
});
