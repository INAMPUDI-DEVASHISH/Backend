Setting up and running the application


To configure a Flask application with Postman and MySQL, begin by ensuring Python and pip are installed. Create and activate a virtual environment in your project directory. 
Install Flask and dependencies like Flask-SQLAlchemy and Flask-JWT-Extended with pip. Set up MySQL by installing it and creating a database named 'new', then update the SQLALCHEMY_DATABASE_URI in your Flask code. 
Configure Flask environment variables for the app and development mode. Initialize the database by executing from your_script_name import db; db.create_all() in Python. Launch the Flask app with flask run. 
In Postman, installed separately, create requests to interact with your application, such as user creation or login, and use the JWT token received after logging in for protected routes. 
Test file uploads using the /upload endpoint with form-data, and manipulate tasks through their respective endpoints, ensuring that your MySQL service is running beforehand.

By Devashish and Pavan
