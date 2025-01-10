# **HabitForge: Habit Tracking API**

HabitForge is a powerful backend API designed to help users break bad habits and build better ones. Whether it's daily reading, exercise, or any personal goal, HabitForge offers a flexible, scalable, and easy-to-integrate solution for habit creation, tracking, logging, and analytics.


## **Key Features:**

- **Habit Management**: Easily create, update, delete, and reset habits.
- **Streak Tracking & Habit Statistics**: Track streaks, log history, and gather valuable analytics on your habits.
- **Customizable Endpoints**: Adjust frequency, status, and other attributes of your habits.

---

## **Technologies Used:**

- **Flask**: Lightweight web framework for building the API.
- **MongoDB Atlas**: Cloud-based NoSQL database for habit data storage.
- **Redis**: Fast data storage for JWT authentication and token blacklisting.
- **Postman**: API documentation and testing.

---


## **To get started with HabitForge in ***PRODUCTION***, interact directly with the API via Postman:**

You can explore and interact with the HabitForge API without needing to download anything. Click the link below to access the **interactive Postman collection**:

[**Postman Interactive API**](https://habitforge-4bd19d64920e.herokuapp.com/)

This will allow you to directly interact with the API endpoints, such as creating and managing habits, logging in, and more—all without setting up any local environment.

---


## To get started with HabitForge in ***DEVELOPMENT***, follow these steps:

### **Installation & Setup**


### 1. Clone the repository:

```bash
git clone https://github.com/Lafertd/HabitForge
cd HabitForge
```

### 2. Set up the virtual environment:

```bash
python3 -m venv myvenv
source myvenv/bin/activate
```

### 3. Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables:

Create a `.env` file in the root directory and add the following (replace with actual values):

```bash
MONGODB_URI=mongodb://localhost:27017 # (or use your_mongodb_atlas_connection_string)
REDIS_URL=redis://localhost:6379 # (or use redis-cloud on heroku addons)
JWT_SECRET_KEY=example_jwt_secret_key # (Use 'Secrets Library; 'https://docs.python.org/3/library/secrets.html')
```

### 5. Run the application locally:

```bash
python3 -m flask run # (--debug: option to run the API with debugger)
```

The app will be accessible at [http://localhost:5000](http://localhost:5000) by Default.

### 6. Deploy to Heroku (optional):

```bash
heroku create habitforge
heroku addons:create heroku-redis:hobby-dev # (add Redis in heroku Dashboard if command doesn't work)
git push heroku main # (if it doesn't work use 'master')
```

Once deployed, the app will be live on heroku.

---

## **API Documentation**

All API routes are documented via Postman. The API allows easy integration for [creating, updating, tracking, and analyzing your habits etc.] On your application.

## API Endpoints:

## Authentication

### **POST /auth/register**
- Registers a new user.
- Body: `{"username": "newUser", "password": "securePassword"}`

### **POST /auth/login**
- Authenticates a user and returns a JWT token.
- Body: `{"username": "newUser", "password": "securePassword"}`

### **POST /auth/logout**
- Logs out a user by blacklisting their JWT token.
- Requires Bearer Token.

---

## Habits

### **GET /habit/all**
- Retrieves all user's habits.
- Requires Bearer Token.

### **GET /habit/details**
- Retrieves details for a specific habit.
- Body: `{"habit_name": "reading"}`
- Requires Bearer Token.

### **GET /habit/status**
- Retrieves current status of a habit.
- Body: `{"habit_name": "reading"}`
- Requires Bearer Token.

### **PUT /habit/status**
- Updates habit status.
- Body: `{"habit_name": "reading", "status": "New Status"}`
- Requires Bearer Token.

### **GET /habit/statistics**
- Retrieves habit statistics.
- Body: `{"habit_name": "reading"}`
- Requires Bearer Token.

### **PUT /habit/frequency**
- Updates habit frequency.
- Body: `{"habit_name": "reading", "frequency": "weekly"}`
- Requires Bearer Token.

### **PUT /habit/rename**
- Renames a habit.
- Body: `{"habit_name": "read", "new_habit_name": "reading"}`
- Requires Bearer Token.

### **DELETE /habit/delete**
- Deletes a habit.
- Body: `{"habit_name": "reading"}`
- Requires Bearer Token.

---
  
## **Quality and Testing**

While this MVP version has been rapidly developed and rigorously tested with Postman for core functionality, unit tests are planned for future versions. The current priority is to provide fast, robust, and scalable solutions to help users develop positive habits with immediate results.

Future releases will include comprehensive testing coverage to ensure API stability and performance.

---

## **Contributing**

If you'd like to contribute to HabitForge, feel free to fork the repository and submit a pull request. Contributions are welcome for both functional improvements and bug fixes. Please ensure to follow the style guidelines when adding features.

(https://habitforge-4bd19d64920e.herokuapp.com/)

---

## **License**

HabitForge is open-source and licensed under the MIT License.

---

## **Contact**

**Author**: Lafertd  
**Project URL**: [https://github.com/](https://github.com/Lafertd)
**Email**: achrafprofessionalinfo@gmail.com

---

## **Helpful Links and Resources:**

- **Flask Documentation:**  
  [Official Flask Documentation](https://flask.palletsprojects.com/)  
  [Flask with Gunicorn Setup Guide](https://flask.palletsprojects.com/en/2.0.x/deploying/gunicorn/)

- **Gunicorn Documentation:**  
  [Official Gunicorn Documentation](https://docs.gunicorn.org/en/stable/)

- **Redis Cloud Setup:**  
  [Redis Cloud Documentation](https://redis.com/redis-enterprise-cloud/)

- **Heroku Documentation:**  
  [Official Heroku Deployment Guide](https://devcenter.heroku.com/articles/getting-started-with-python)  
  [Heroku Redis Add-On](https://devcenter.heroku.com/articles/heroku-redis)  
  [How to deploy from Git to Heroku](https://devcenter.heroku.com/articles/git)
