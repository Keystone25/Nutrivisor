# Nutrivisor 🍎🏋️‍♂️

Nutrivisor is an AI-powered nutrition and fitness web application designed to help users build healthier eating habits through intelligent food recommendations, calorie tracking, diabetic-aware meal analysis, and exercise guidance.

The system combines AI food recognition, nutrition analysis, glycemic index monitoring, personalized meal recommendations, and fitness tracking into a single responsive healthcare platform.

---

# Features

## 🍽 AI Food Detection

* Detects food items using a trained deep learning model
* Displays nutrition information instantly
* Live food scanning support

## 🩺 Diabetes-Aware Recommendation System

* Supports:

  * Type 1 Diabetes
  * Type 2 Diabetes
  * Prediabetes
  * Gestational Diabetes
* Filters unsafe foods based on:

  * Glycemic Index (GI)
  * Glycemic Load (GL)

## 📊 Nutrition Tracking

* Tracks:

  * Calories
  * Protein
  * Carbohydrates
  * Fat
  * Fiber
* Daily meal logging system

## 🥗 Smart Diet Recommendation

* Personalized food recommendations
* Allergy-aware filtering
* Calorie-aware food suggestions
* Meal-time based recommendations

## 💪 Exercise & Fitness Tracking

* Exercise recommendation system
* Burned calorie tracking
* Net calorie calculation
* Exercise detail pages

## 📈 Analytics Dashboard

* Daily calorie analysis
* Weekly calorie trends
* Monthly calorie reports
* Interactive charts

## 👤 User Management

* User authentication system
* Profile management
* Fitness goal tracking
* Body type & activity analysis

## 🛠 Admin Features

* Add/Edit/Delete foods
* User management
* Exercise management
* Feedback management

---

# Tech Stack

| Technology          | Usage                     |
| ------------------- | ------------------------- |
| Python              | Backend                   |
| Flask               | Web Framework             |
| SQLAlchemy          | ORM                       |
| SQLite              | Database                  |
| TensorFlow/Keras    | AI Model                  |
| OpenCV              | Camera & Image Processing |
| HTML/CSS/JavaScript | Frontend                  |
| Jinja2              | Templating                |

---

# Frontend Technologies Used
* HTML5
* CSS3
* JavaScript
* Jinja2 Templating Engine
* Responsive UI Design

# Database Models

* User
* Menu
* Nutrition
* Daily2
* MealLog
* Exercise
* Feed
* LogSession

---

# Installation

## 1. Clone Repository

```bash
git clone <repository-url>
cd Nutrivisor
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Additional Requirement for AI Detection

# ⚠️ The food detection system requires the trained AI model file:

food_detect_model.hdf5

This file is necessary for the live food recognition feature to function correctly.

Place the model file in the project root directory:

```bash
Nutrivisor/
│
├── food_detect_model.hdf5
├── app.py
├── calorie_data.csv
└── ...
```

Without this model file:

Camera detection will not work
Food prediction will fail
Live scanning features will be disabled

---

# Run Application

```bash
python app.py
```

Application runs on:

```bash
http://127.0.0.1:5200
```

---

# 📂 Project Structure

```text
Nutri_Final/
│
├── .vscode/
│
├── __pycache__/
│
├── instance/
│
├── model.savedmodel/
│
├── static/
│
├── templates/
│
├── calorie_data.csv
├── calorie_data.xlsx
├── data.xlsx
│
├── newmenu1.db
├── pythonsqlite.db
│
├── python3.py
├── requirements.txt
├── saved_model.pb
├── style.css
│
├── .gitignore
└── README.md
```

---

# Future Improvements

* Cloud deployment
* Mobile application
* Real-time nutrition chatbot
* Voice assistant integration
* Advanced AI meal prediction
* Wearable device integration

---


# Contributors

* Surya Krishna H

---

# License

This project is developed for educational and research purposes.
