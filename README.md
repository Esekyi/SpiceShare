# SpiceShare🌶️

SpiceShare is a recipe-sharing platform for home cooks and food enthusiasts to share and discover recipes from around the world. Whether you're an expert or a beginner, SpiceShare connects you to a global community where food brings everyone together.

- Deployed site: [SpiceShare](https://www.spiceshare.live)
- Blog Article: [Read about SpiceShare's Development Journey](https://esekyi.medium.com/introducing-spiceshare-a-recipe-sharing-platform-63f22e078ba9)
- Author:
	- [Emmanuel Sekyi](https://linkedin.com/in/Esekyi)

## Table of Contents

1. [Introduction](#introduction)
2. [Core Features](#core-features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation️)
5. [Usage](#usage️)
6. [Learnings and Next Steps](#learnings-and-next-steps️)
7. [Contributing](#contributing)
8. [Related Projects](#related-projects)
9. [License](#license)
10. [COntact](#contact)


## Introduction📖

SpiceShare was born from the love for food and the desire to build a community where people can discover new flavors and culinary traditions. The idea started from noticing how food often brings people together, regardless of culture or background. SpiceShare aims to create that sense of togetherness online by making it easy for users to upload and share their favorite recipes.

### Challenges and Vision🚧
While developing this project, I encountered challenges with implementing image uploads for recipes, building robust user authentication, and managing dynamic ingredient lists. These hurdles taught me to think critically and apply solutions like modular architecture and database management. Looking forward, I envision further features like AI-based recipe recommendations and a mobile app version.

## Core Features🧩

- User authentication
- Recipe creation and sharing
- Search and filter recipes
- User profiles
- Favorite and save recipes (later updates)

## Prerequisites🎯
Before you begin, ensure you have met the following requirements:

- Node.js (v14.x or later)
- npm (v6.x or later)

--- this is only used to build tailwind css

## Installation⚙️

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

4. Create a .env file in the root directory and add these variables
	```
	S3_BUCKET_NAME='AWS_S3_bucketName' # for uploads to AWS S3, add your bucket name here
	AWS_ACCESS_KEY_ID='' # AWS Access key
	AWS_SECRET_ACCESS_KEY='' # AWS secrete key
	AWS_REGION='' # AWS region for the S3

	DATABASE_URL='postgresql://postgres:localhost' # Postgress db url
	SECRET_KEY='WQioiUU-TWIQ-To-Much_TO-6ue22' # Secrete key for Flask and Flsk-WTF

	# Flask-mail variables
	MAIL_SERVER ='smtp.gmail.com'  # SMTP server address
	MAIL_PORT =587  # Usually, 465 for SSL or 587 for TLS
	MAIL_USE_TLS =True  # If you are using port 587 (for TLS), set to True
	MAIL_USERNAME =''  # Your email address
	MAIL_PASSWORD =''  # Your email password
	MAIL_DEFAULT_SENDER ='Your name <your_name@example.com>'
	```

5. Install dependencies:
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

6. Set up the database:
	```
	flask db upgrade
	```

7. Run the application
	```
	flask db upgrade
	```

Your local SpiceShare app will now be running at http://127.0.0.1:5000/.


## Usage🍽️

### Create Your First Recipe:
SpiceShare is easy to use. Here are the core features:
- Register an account.
- Upload your first recipe by filling in the form with name, ingredients, and instructions.
- Browse recipes shared by others and give feedback theough comments.

### Explore Features:
- Search Recipes by category or ingredient.
- Add Ingredients Dynamically using a user-friendly form.


## Learnings and Next Steps⏭️

### What I Learned
Through the development of SpiceShare, I gained valuable insights into full-stack development, database management, and UI/UX design. I also deepened my understanding of Flask and how to build modular, scalable web applications.

### Next Iteration
Moving forward, I plan to:
- Add user profiles and recipe ratings.
- Implement an advanced search/filter feature for recipes.
- Implement JWT authentication for API expansion.


## Contributing🤝

Contributions to SpiceShare are welcome! Please follow these steps:

1. Fork the repository
2. Create a new feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request to the main branch

Please make sure to adhere to the project's coding standards.

## Related Projects🔗
If you're interested in recipe-sharing or similar projects, you may also enjoy:
- [AllRecipes](https://www.allrecipes.com/)
- [CookBook](https://cookbookmanager.com/)

## License📜

This project is licensed under the [MIT License](LICENSE).

## Contact📧

If you have any questions or feedback, please open an issue on GitHub or contact the maintainer at me@esekyi.tech.
