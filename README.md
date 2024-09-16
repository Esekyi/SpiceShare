# SpiceShare - A recipe-sharing web app

SpiceShare is a web application that allows users to share and discover recipes from around the world.


## Introduction

Welcome to SpiceShare! SpiceShare is a recipe-sharing platform where users can explore, share, and comment on a variety of recipes. From home cooks to professional chefs, this platform brings together a community passionate about food. Whether you're looking to discover new dishes or share your culinary creations, SpiceShare is the go-to platform.

- Deployed site: [SpiceShare](https://www.spiceshare.live)
- Final Blog Article: [Read about SpiceShare's Development Journey](https://linkedin.com)
- Author(s):
	* [Emmanuel Sekyi](https://linkedin.com/in/Esekyi)

## Features

- User authentication
- Recipe creation and sharing
- Search and filter recipes
- User profiles
- Favorite and save recipes (later updates)

## Prerequisites
Before you begin, ensure you have met the following requirements:

- Node.js (v14.x or later)
- npm (v6.x or later)

--- this is only used to build tailwind css

## Installation

To run SpiceShare locally, follow these steps:

1. Clone the repository:
   ```
    https://github.com/Esekyi/SpiceShare.git
   ```

2. Navigate to the project directory:
	```
	cd spiceshare
	```

3. Create and activate a virtual environment:
	```
	python -m venv .venv
	source .venv/bin/activate  # On Windows: .venv\Scripts\activate
	```

4. Install dependencies:
	python and flask
	```
	python3 -m pip install -r requirements.txt
	```
	Node for tailwind css build
	```
	npm install
	# or
	yarn install
	```

5. Set up the database:
	```
	flask db upgrade
	```

6. Run the application
	```
	flask db upgrade
	```

Your local SpiceShare app will now be running at http://127.0.0.1:5000/.


## Usage
SpiceShare is easy to use. Here are the core features:
- Explore Recipes: View recipes from a variety of categories, including detailed instructions and ingredient lists.
- Create & Share Recipes: Registered users can create and share their own recipes.
- User Authentication: Sign up and log in to access personalized features, such as creating recipes or commenting on others' recipes.
- Comment & Interact: Engage with the community by leaving comments and feedback on recipes.

## Challenges Overcome

1. Dynamic Ingredient Input
The goal was to allow users to dynamically add ingredients, and this required building a custom input field that could store each ingredient in the database as a list. Achieving this functionality pushed us to think outside the box and refine my knowledge of Flask and dynamic form handling.

2. User Authentication
Securing user-specific actions (such as editing or deleting recipes) was challenging. Using Flask-Login, I implemented route protection to prevent unauthorized users from accessing certain pages. I also introduced helpful flash messages to guide users through errors or authentication problems.


## Learnings and Next Steps
### What I Learned
Through the development of SpiceShare, I gained valuable insights into full-stack development, database management, and UI/UX design. I also deepened my understanding of Flask and how to build modular, scalable web applications.

### Next Iteration
Moving forward, I plan to:
- Add user profiles and recipe ratings.
- Implement an advanced search/filter feature for recipes.
- Implement JWT authentication for API expansion.


## Contributing

Contributions to SpiceShare are welcome! Please follow these steps:

1. Fork the repository
2. Create a new feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request to the main branch

Please make sure to adhere to the project's coding standards.

## Related Projects
If you're interested in recipe-sharing or similar projects, you may also enjoy:
- [AllRecipes](https://www.allrecipes.com/)
- [CookBook](https://cookbookmanager.com/)

## License

[MIT License](LICENSE)

## Contact

If you have any questions or feedback, please open an issue on GitHub or contact the maintainer at me@esekyi.tech.
