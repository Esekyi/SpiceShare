#!/usr/bin/env python3
"""
Recipe Database Population Script for SpiceShare
Generates realistic recipe entries with detailed ingredients for testing the AI nutrition calculator.
"""

from app import create_app, db
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.instruction import Instruction
from app.models.category import Category
from app.models.user import User
from app.services.nutrition_service import NutritionService
import uuid
from datetime import datetime, timezone

def create_sample_recipes():
    """Create sample recipes with realistic ingredients and instructions"""
    
    app = create_app()
    with app.app_context():
        print("🍳 SpiceShare Recipe Database Population Script")
        print("=" * 50)
        
        # User ID to use for all recipes
        user_id = "8aa58804-5a4f-4b95-ad0c-132027064e0a"
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User with ID {user_id} not found!")
            return
        
        print(f"✅ Found user: {user.username}")
        
        # Get or create categories
        categories = {}
        category_names = ["Main Dish", "Dessert", "Appetizer", "Breakfast", "Soup"]
        
        for cat_name in category_names:
            category = Category.query.filter_by(name=cat_name).first()
            if not category:
                category = Category(name=cat_name, description=f"Delicious {cat_name.lower()} recipes")
                db.session.add(category)
                db.session.flush()
            categories[cat_name] = category.id
        
        # Sample recipes with detailed ingredients
        sample_recipes = [
            {
                "title": "Classic Chicken Stir Fry",
                "description": "A delicious and healthy chicken stir fry with fresh vegetables and a savory sauce.",
                "category": "Main Dish",
                "prep_time": 15,
                "cook_time": 12,
                "servings": 4,
                "oven_temp": 0,  # No oven needed
                "ingredients": [
                    {"name": "chicken breast, boneless skinless", "quantity": 1.5, "unit": "lb"},
                    {"name": "broccoli florets", "quantity": 2, "unit": "cups"},
                    {"name": "bell peppers, sliced", "quantity": 2, "unit": "pieces"},
                    {"name": "carrots, sliced", "quantity": 2, "unit": "pieces"},
                    {"name": "garlic, minced", "quantity": 3, "unit": "cloves"},
                    {"name": "ginger, fresh minced", "quantity": 1, "unit": "tbsp"},
                    {"name": "soy sauce", "quantity": 3, "unit": "tbsp"},
                    {"name": "sesame oil", "quantity": 2, "unit": "tsp"},
                    {"name": "vegetable oil", "quantity": 2, "unit": "tbsp"},
                    {"name": "cornstarch", "quantity": 1, "unit": "tbsp"},
                    {"name": "rice, cooked", "quantity": 4, "unit": "cups"}
                ],
                "instructions": [
                    "Cut chicken into bite-sized pieces and toss with cornstarch.",
                    "Heat vegetable oil in a large wok or skillet over high heat.",
                    "Add chicken and stir-fry for 5-6 minutes until golden brown.",
                    "Add garlic and ginger, stir-fry for 30 seconds until fragrant.",
                    "Add vegetables and stir-fry for 3-4 minutes until crisp-tender.",
                    "Mix soy sauce and sesame oil, add to the pan and toss everything together.",
                    "Serve immediately over cooked rice."
                ]
            },
            {
                "title": "Chocolate Chip Cookies",
                "description": "Soft and chewy chocolate chip cookies that are perfect for any occasion.",
                "category": "Dessert",
                "prep_time": 15,
                "cook_time": 12,
                "servings": 24,
                "oven_temp": 375,
                "ingredients": [
                    {"name": "all-purpose flour", "quantity": 2.25, "unit": "cups"},
                    {"name": "butter, softened", "quantity": 1, "unit": "cup"},
                    {"name": "granulated sugar", "quantity": 0.75, "unit": "cup"},
                    {"name": "brown sugar, packed", "quantity": 0.75, "unit": "cup"},
                    {"name": "eggs, large", "quantity": 2, "unit": "pieces"},
                    {"name": "vanilla extract", "quantity": 2, "unit": "tsp"},
                    {"name": "baking soda", "quantity": 1, "unit": "tsp"},
                    {"name": "salt", "quantity": 1, "unit": "tsp"},
                    {"name": "chocolate chips", "quantity": 2, "unit": "cups"}
                ],
                "instructions": [
                    "Preheat oven to 375°F (190°C).",
                    "In a large bowl, cream together butter and both sugars until light and fluffy.",
                    "Beat in eggs one at a time, then add vanilla extract.",
                    "In a separate bowl, whisk together flour, baking soda, and salt.",
                    "Gradually mix dry ingredients into the wet ingredients until just combined.",
                    "Stir in chocolate chips.",
                    "Drop rounded tablespoons of dough onto ungreased baking sheets.",
                    "Bake for 9-11 minutes until golden brown around edges.",
                    "Cool on baking sheet for 2 minutes before transferring to wire rack."
                ]
            },
            {
                "title": "Mediterranean Quinoa Salad",
                "description": "A fresh and healthy quinoa salad packed with Mediterranean flavors and nutrients.",
                "category": "Main Dish",
                "prep_time": 20,
                "cook_time": 15,
                "servings": 6,
                "oven_temp": 0,
                "ingredients": [
                    {"name": "quinoa, uncooked", "quantity": 1.5, "unit": "cups"},
                    {"name": "cucumber, diced", "quantity": 2, "unit": "pieces"},
                    {"name": "cherry tomatoes, halved", "quantity": 2, "unit": "cups"},
                    {"name": "red onion, finely diced", "quantity": 0.5, "unit": "cup"},
                    {"name": "feta cheese, crumbled", "quantity": 1, "unit": "cup"},
                    {"name": "kalamata olives, pitted", "quantity": 0.5, "unit": "cup"},
                    {"name": "fresh parsley, chopped", "quantity": 0.5, "unit": "cup"},
                    {"name": "fresh mint, chopped", "quantity": 0.25, "unit": "cup"},
                    {"name": "olive oil, extra virgin", "quantity": 0.25, "unit": "cup"},
                    {"name": "lemon juice, fresh", "quantity": 3, "unit": "tbsp"},
                    {"name": "garlic, minced", "quantity": 2, "unit": "cloves"},
                    {"name": "salt", "quantity": 1, "unit": "tsp"},
                    {"name": "black pepper", "quantity": 0.5, "unit": "tsp"}
                ],
                "instructions": [
                    "Rinse quinoa in cold water until water runs clear.",
                    "Cook quinoa according to package directions, then let cool completely.",
                    "In a large bowl, combine cooled quinoa, cucumber, tomatoes, and red onion.",
                    "Add feta cheese, olives, parsley, and mint.",
                    "In a small bowl, whisk together olive oil, lemon juice, garlic, salt, and pepper.",
                    "Pour dressing over salad and toss gently to combine.",
                    "Refrigerate for at least 30 minutes before serving to allow flavors to meld.",
                    "Serve chilled or at room temperature."
                ]
            },
            {
                "title": "Creamy Tomato Soup",
                "description": "A rich and creamy tomato soup that's perfect for cold days, served with grilled cheese.",
                "category": "Soup",
                "prep_time": 10,
                "cook_time": 25,
                "servings": 4,
                "oven_temp": 0,
                "ingredients": [
                    {"name": "canned whole tomatoes", "quantity": 28, "unit": "oz"},
                    {"name": "yellow onion, diced", "quantity": 1, "unit": "pieces"},
                    {"name": "garlic, minced", "quantity": 4, "unit": "cloves"},
                    {"name": "vegetable broth", "quantity": 2, "unit": "cups"},
                    {"name": "heavy cream", "quantity": 0.5, "unit": "cup"},
                    {"name": "butter", "quantity": 2, "unit": "tbsp"},
                    {"name": "olive oil", "quantity": 1, "unit": "tbsp"},
                    {"name": "dried basil", "quantity": 1, "unit": "tsp"},
                    {"name": "dried oregano", "quantity": 1, "unit": "tsp"},
                    {"name": "sugar", "quantity": 1, "unit": "tsp"},
                    {"name": "salt", "quantity": 1, "unit": "tsp"},
                    {"name": "black pepper", "quantity": 0.5, "unit": "tsp"}
                ],
                "instructions": [
                    "Heat olive oil and butter in a large pot over medium heat.",
                    "Add diced onion and cook for 5 minutes until softened.",
                    "Add minced garlic and cook for 1 minute until fragrant.",
                    "Add canned tomatoes (with juice), breaking them up with a spoon.",
                    "Add vegetable broth, basil, oregano, sugar, salt, and pepper.",
                    "Bring to a boil, then reduce heat and simmer for 15 minutes.",
                    "Use an immersion blender to puree soup until smooth (or transfer to regular blender in batches).",
                    "Stir in heavy cream and heat through for 2-3 minutes.",
                    "Taste and adjust seasoning as needed.",
                    "Serve hot with grilled cheese sandwiches or crusty bread."
                ]
            },
            {
                "title": "Fluffy Pancakes",
                "description": "Light, fluffy pancakes that are perfect for weekend breakfast or brunch.",
                "category": "Breakfast",
                "prep_time": 10,
                "cook_time": 15,
                "servings": 4,
                "oven_temp": 0,
                "ingredients": [
                    {"name": "all-purpose flour", "quantity": 2, "unit": "cups"},
                    {"name": "sugar", "quantity": 2, "unit": "tbsp"},
                    {"name": "baking powder", "quantity": 2, "unit": "tsp"},
                    {"name": "salt", "quantity": 1, "unit": "tsp"},
                    {"name": "milk", "quantity": 1.75, "unit": "cups"},
                    {"name": "eggs, large", "quantity": 2, "unit": "pieces"},
                    {"name": "butter, melted", "quantity": 4, "unit": "tbsp"},
                    {"name": "vanilla extract", "quantity": 1, "unit": "tsp"},
                    {"name": "butter for cooking", "quantity": 2, "unit": "tbsp"}
                ],
                "instructions": [
                    "In a large bowl, whisk together flour, sugar, baking powder, and salt.",
                    "In another bowl, whisk together milk, eggs, melted butter, and vanilla.",
                    "Pour wet ingredients into dry ingredients and stir just until combined (lumps are okay).",
                    "Let batter rest for 5 minutes while heating the pan.",
                    "Heat a griddle or large skillet over medium heat and add a little butter.",
                    "Pour 1/4 cup of batter for each pancake onto the hot griddle.",
                    "Cook until bubbles form on surface and edges look set, about 2-3 minutes.",
                    "Flip and cook for 1-2 minutes more until golden brown.",
                    "Serve immediately with butter and maple syrup."
                ]
            }
        ]
        
        print(f"\n🎯 Creating {len(sample_recipes)} sample recipes...")
        
        created_count = 0
        for recipe_data in sample_recipes:
            try:
                # Check if recipe already exists
                existing_recipe = Recipe.query.filter_by(
                    title=recipe_data["title"], 
                    user_id=user_id
                ).first()
                
                if existing_recipe:
                    print(f"⏭️  Skipping '{recipe_data['title']}' - already exists")
                    continue
                
                # Create the recipe
                new_recipe = Recipe(
                    title=recipe_data["title"],
                    description=recipe_data["description"],
                    category_id=categories[recipe_data["category"]],
                    user_id=user_id,
                    prep_time=recipe_data["prep_time"],
                    cook_time=recipe_data["cook_time"],
                    servings=recipe_data["servings"],
                    oven_temp=recipe_data["oven_temp"],
                    image_url="",  # No image for test recipes
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                
                db.session.add(new_recipe)
                db.session.flush()  # Get the recipe ID
                
                # Add ingredients
                for ing_data in recipe_data["ingredients"]:
                    ingredient = Ingredient(
                        name=ing_data["name"],
                        quantity=ing_data["quantity"],
                        unit=ing_data["unit"],
                        recipe_id=new_recipe.id
                    )
                    db.session.add(ingredient)
                
                # Add instructions
                for i, instruction_text in enumerate(recipe_data["instructions"]):
                    instruction = Instruction(
                        step_number=i + 1,
                        name=instruction_text,
                        recipe_id=new_recipe.id
                    )
                    db.session.add(instruction)
                
                db.session.commit()
                created_count += 1
                
                print(f"✅ Created: '{recipe_data['title']}' with {len(recipe_data['ingredients'])} ingredients")
                
            except Exception as e:
                print(f"❌ Error creating '{recipe_data['title']}': {e}")
                db.session.rollback()
        
        print(f"\n🎉 Successfully created {created_count} recipes!")
        
        # Optionally trigger nutrition calculation for new recipes
        if created_count > 0:
            print(f"\n🧮 Triggering nutrition calculations...")
            
            # Get all recipes for this user
            user_recipes = Recipe.query.filter_by(user_id=user_id).all()
            
            for recipe in user_recipes:
                if not recipe.nutrition_calculated:
                    try:
                        print(f"🔬 Calculating nutrition for '{recipe.title}'...")
                        nutrition_info = NutritionService.calculate_and_store_nutrition(recipe)
                        
                        if nutrition_info:
                            print(f"  ✅ Success! {nutrition_info.calories_per_serving:.0f} cal/serving")
                        else:
                            print(f"  ⚠️  Nutrition calculation failed (API key needed)")
                            
                    except Exception as e:
                        print(f"  ❌ Error: {e}")
        
        print(f"\n🎯 Database population complete!")
        print(f"   Total recipes in database: {Recipe.query.count()}")
        print(f"   Recipes with nutrition data: {Recipe.query.filter_by(nutrition_calculated=True).count()}")


if __name__ == "__main__":
    create_sample_recipes()
