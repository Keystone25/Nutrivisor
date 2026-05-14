from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, update, Column, Integer, String
from fitness_tools.meals.meal_maker import MakeMeal
from flask import Blueprint
from flask_login import UserMixin, current_user, login_user
from flask_login import LoginManager, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, Response, request, flash, redirect, url_for
import cv2
import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import time
from tensorflow.keras.models import load_model
import glob
from PIL import Image
import pandas as pd
from keras.utils import img_to_array
import numpy as np
from datetime import datetime
from pytz import timezone
import re


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'newmenu1.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "random string"
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'C:/Users/mail4/OneDrive/Desktop/Nutrivisor/Nutrivisor-V1/Nutri_Final/static/upload/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



auth = Blueprint('auth', __name__)
app.register_blueprint(auth)
main = Blueprint('main', __name__)
app.register_blueprint(main)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(u_id):
    return db.session.get(User, int(u_id))





class User(UserMixin,db.Model):
     id = db.Column('u_id', db.Integer, primary_key=True)
     fname = db.Column(db.String(100))
     lname = db.Column(db.String(100))
     email = db.Column(db.String(50), nullable=False,unique=True)
     utype = db.Column(db.String(20), default='user')
     phone = db.Column(db.String(20))
     dob = db.Column(db.String(20))
     password = db.Column(db.String(50),nullable=False)
     weight = db.Column(db.Integer())
     height = db.Column(db.Integer())
     age = db.Column(db.String(10))
     gender = db.Column(db.String(10))
     bodytype = db.Column(db.String(10))
     activity = db.Column(db.String(20))
     goal = db.Column(db.String(20))
     diabetes_type = db.Column(db.String(20), default='none')
     gi_preference = db.Column(db.String(10), default='medium') 
     allergy1 = db.Column(db.String(100), default='')
     allergy2 = db.Column(db.String(100), default='')
     cal = db.Column(db.Float())
     fat = db.Column(db.Float())
     protein = db.Column(db.Float())
     carbs = db.Column(db.Float())



class logsession(db.Model):
    id = db.Column('session_id', db.Integer, primary_key=True)
    log_date = db.Column(db.String(50))
    log_time = db.Column(db.String(50))

class menu(db.Model):  #this is a table named menu inside the menu database for user and admin but only viewing for user
    id = db.Column('menu_id', db.Integer, primary_key=True)
    item = db.Column(db.String(50))
    cal = db.Column(db.String(50))
    stdwt = db.Column(db.String(50))
    cal100 = db.Column(db.String(50))
    meal = db.Column(db.String(50))
    allergen1 = db.Column(db.String(50), default='')
    allergen2 = db.Column(db.String(50), default='')
    glycemic_index = db.Column(db.Integer, default=50)
    carbs = db.Column(db.Float, default=0.0) 
    imgpath = db.Column(db.String(100), default='')
    quantity = db.Column(db.String(50))

class MealLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    food_name = db.Column(db.String(100))
    calories = db.Column(db.Float)
    meal_type = db.Column(db.String(20))  # breakfast/lunch/dinner/snack
    time = db.Column(db.String(20))       # "08:30 AM"
    date = db.Column(db.String(20))



class daily2(db.Model):

    id = db.Column('daily_id', db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.u_id')
    )

    date = db.Column(db.String(20))

    usr_cal = db.Column(db.Float)

    # BREAKFAST
    br_item = db.Column(db.String(200), default='')
    br_cal = db.Column(db.Float, default=0.0)

    # ELEVENSES
    el_item = db.Column(db.String(200), default='')
    el_cal = db.Column(db.Float, default=0.0)

    # LUNCH
    lu_item = db.Column(db.String(200), default='')
    lu_cal = db.Column(db.Float, default=0.0)

    # SNACKS
    sn_item = db.Column(db.String(200), default='')
    sn_cal = db.Column(db.Float, default=0.0)

    # DINNER
    di_item = db.Column(db.String(200), default='')
    di_cal = db.Column(db.Float, default=0.0)

    burned_cal = db.Column(db.Float, default=0.0)


class Nutrition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(100), unique=True)
    quantity = db.Column(db.String(50))
    calories = db.Column(db.Float)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)
    fiber = db.Column(db.Float)
    glycemic_i = db.Column(db.Integer)
    category = db.Column(db.String(20))
    suggestion = db.Column(db.String(200))


class Feed(db.Model):
    id = db.Column('feed_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    message = db.Column(db.String(600))
    timestamp = db.Column(db.String(50))

class Exercise(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    calories_burn = db.Column(db.Integer)
    duration = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    steps = db.Column(db.Text)
    image = db.Column(db.String(200))


# =========================
# Helper Function for capturing today and alos to give proper date formats
# =========================

def get_today():
    return datetime.now().strftime('%Y-%m-%d')

def parse_date(date_str):

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            pass

    return None

# =========================
# Helper Function for diabetic staus in live capture.
# =========================

def get_diabetic_status(food_name, user):

    def calculate_gl(gi, carbs):
        return (gi * carbs) / 100

    # Diabetes thresholds
    limits = {
        "type2": (55, 20),
        "type1": (60, 25),
        "prediabetes": (50, 15),
        "gestational": (45, 10),
        "none": (100, 100)
    }

    gi_limit, gl_limit = limits.get(user.diabetes_type, (100, 100))

    # Get food from DB
    food = Nutrition.query.filter(Nutrition.food_name.ilike(f"%{food_name}%")).first()

    if not food:
        return {
            "status": "unknown",
            "message": "No data available"
        }

    gi = food.glycemic_i or 50
    carbs = food.carbs or 0
    gl = calculate_gl(gi, carbs)

    # =========================
    # BASE HEALTH LOGIC (FOR EVERYONE)
    # =========================
    if gl > 20:
        status = "avoid"
        message = "High glycemic load"

    elif gl > 10:
        status = "moderate"
        message = "Consume in moderation"

    else:
        status = "safe"
        message = "Good choice"

    # =========================
    # DIABETIC STRICT RULE
    # =========================
    if user.diabetes_type != "none":
        if gl > gl_limit or gi > gi_limit:
            status = "avoid"
            message = "Not recommended for diabetic patients"

    # =========================
    # RETURN EVERYTHING 
    # =========================
    return {
        "status": status,
        "message": message,
        "gi": gi,
        "gl": round(gl, 2)
    }


# =========================
# CAMERA + AI MODEL
# =========================
camera = None

food_label = ''
captured_frame = None
detection_done = False
last_capture_time = 0

COOLDOWN = 3


model = load_model('C:/Users/mail4/OneDrive/Desktop/Nutrivisor/Nutrivisor-V1/Nutri_Final/food_detect_model.hdf5', compile=False)

df = pd.read_csv('C:/Users/mail4/OneDrive/Desktop/Nutrivisor/Nutrivisor-V1/Nutri_Final/calorie_data.csv')
labels = list(df['categories'].values)


def gen_frames():
    global camera, food_label, captured_frame, detection_done, last_capture_time

    frame_count = 0  #  for skipping frames

    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        print("Camera initialized")
    while True:
        success, frame = camera.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        frame_count += 1

        #  FREEZE FRAME AFTER DETECTION
        if detection_done:
            if captured_frame is not None:
                ret, buffer = cv2.imencode('.jpg', captured_frame)
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            continue

        # =========================
        #  FRAME SKIPPING (KEY FOR PERFORMANCE)
        # =========================
        if frame_count % 5 != 0:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            continue

        # =========================
        # PREPROCESS (LIGHTWEIGHT)
        # =========================
        roi = cv2.resize(frame, (224, 224))

        # Convert BGR → RGB (CRITICAL)
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

        roi = roi.astype(np.float32)

        # Teachable Machine normalization
        roi = (roi / 127.5) - 1

        roi = np.expand_dims(roi, axis=0)

        # =========================
        # MODEL PREDICTION
        # =========================
        pred = model.predict(roi, verbose=0)
        ind = np.argmax(pred)
        confidence = float(np.max(pred))
        print("Confidence:", confidence)

        print("Prediction shape:", pred.shape)
        print("Labels count:", len(labels)) 
        print("Predicted index:", ind)

        # SAFE CHECK
        if ind >= len(labels):
            print(f"[ERROR] Index {ind} out of range for labels")
            continue

        label_text = f"{labels[ind]} ({confidence:.2f})"

        # =========================
        # AUTO CAPTURE
        # =========================
        if confidence > 0.60 and not detection_done:
            captured_frame = frame.copy()
            food_label = labels[ind]
            detection_done = True
            last_capture_time = time.time()

            print(f"[CAPTURED] {food_label} - {confidence:.2f}")

        # =========================
        # STREAM FRAME
        # =========================
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
# =========================
# ROUTES
# =========================


@app.route('/')
@app.route('/U_Landing_Page')
def U_Landing_Page():
    return render_template('U_Landing_Page.html')



@app.route('/U_Home_page')
@login_required
def U_Home_page():

    msg = request.args.get("msg")
    filter_type = request.args.get("filter", "daily")

    selected_year = request.args.get(
        "year",
        str(datetime.now().year)
    )

    selected_year = int(selected_year)

    today = datetime.now()

    quota = daily2.query.filter_by(
        user_id=current_user.id
    ).first()

    if not quota:

        quota = daily2(
            user_id=current_user.id,
            date=today.strftime('%Y-%m-%d'),

            br_item='',
            br_cal=0,

            el_item='',
            el_cal=0,

            lu_item='',
            lu_cal=0,

            sn_item='',
            sn_cal=0,

            di_item='',
            di_cal=0
        )

        db.session.add(quota)
        db.session.commit()

    # RESET DAILY DATA
    if quota.date != today.strftime('%Y-%m-%d'):

        quota.date = today.strftime('%Y-%m-%d')

        quota.br_item = ''
        quota.br_cal = 0

        quota.el_item = ''
        quota.el_cal = 0

        quota.lu_item = ''
        quota.lu_cal = 0

        quota.sn_item = ''
        quota.sn_cal = 0

        quota.di_item = ''
        quota.di_cal = 0

        quota.burned_cal = 0

        db.session.commit()

    # UPDATED TOTAL
    consumed = (
        (quota.br_cal or 0) +
        (quota.el_cal or 0) +
        (quota.lu_cal or 0) +
        (quota.sn_cal or 0) +
        (quota.di_cal or 0)
    )

    burned = quota.burned_cal or 0

    total = consumed - burned

    all_logs = MealLog.query.filter_by(
        user_id=current_user.id
    ).all()

    logs = []

    chart_labels = []
    chart_values = []
    chart_type = "bar"

    # ================= DAILY =================
    if filter_type == "daily":

        today_str = today.strftime('%Y-%m-%d')

        logs = MealLog.query.filter_by(
            user_id=current_user.id,
            date=today_str
        ).all()

        breakfast = 0
        elevenses = 0
        lunch = 0
        snacks = 0
        dinner = 0

        for log in logs:

            meal = log.meal_type.lower()

            if meal == "breakfast":
                breakfast += log.calories

            elif meal == "elevenses":
                elevenses += log.calories

            elif meal == "lunch":
                lunch += log.calories

            elif meal == "snacks":
                snacks += log.calories

            elif meal == "dinner":
                dinner += log.calories

        chart_labels = [
            "Breakfast",
            "Elevenses",
            "Lunch",
            "Snacks",
            "Dinner"
        ]

        chart_values = [
            breakfast,
            elevenses,
            lunch,
            snacks,
            dinner
        ]

        chart_type = "bar"

    # ================= WEEKLY =================
    elif filter_type == "weekly":

        chart_type = "line"

        weekly_data = {}

        for log in all_logs:

            dt = parse_date(log.date)

            if not dt:
                continue

            diff = (today.date() - dt.date()).days

            if 0 <= diff <= 6:

                day = dt.strftime("%a")

                if day not in weekly_data:
                    weekly_data[day] = 0

                weekly_data[day] += log.calories
                logs.append(log)

        sorted_days = sorted(
            weekly_data.items(),
            key=lambda x: datetime.strptime(
                x[0],
                "%a"
            ).weekday()
        )

        chart_labels = [x[0] for x in sorted_days]
        chart_values = [x[1] for x in sorted_days]

    # ================= MONTHLY =================
    elif filter_type == "monthly":

        chart_type = "line"

        monthly_data = {}

        for log in all_logs:

            dt = parse_date(log.date)

            if not dt:
                continue

            if dt.year != selected_year:
                continue

            month = dt.strftime("%b")

            if month not in monthly_data:
                monthly_data[month] = 0

            monthly_data[month] += log.calories

            logs.append(log)

        month_order = [
            "Jan", "Feb", "Mar", "Apr",
            "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"
        ]

        sorted_month = sorted(
            monthly_data.items(),
            key=lambda x: month_order.index(x[0])
        )

        chart_labels = [x[0] for x in sorted_month]
        chart_values = [x[1] for x in sorted_month]

    available_years = sorted(
        list(set(
            parse_date(log.date).year
            for log in all_logs
            if parse_date(log.date)
        )),
        reverse=True
    )

    suggested = []

    if total > current_user.cal:

        extra = total - current_user.cal

        suggested = Exercise.query.order_by(
            db.func.abs(
                Exercise.calories_burn - extra
            )
        ).limit(4).all()

    return render_template(
        'U_Home_page_1.html',
        daily=quota,
        total=total,
        target=current_user.cal,
        logs=logs,
        msg=msg,
        filter_type=filter_type,
        chart_labels=chart_labels,
        chart_values=chart_values,
        chart_type=chart_type,
        selected_year=selected_year,
        available_years=available_years,
        suggested=suggested,
        consumed=consumed,
        burned=burned
    )



@app.route('/U_Diet_Recommender')
@login_required
def U_Diet_recommender():

    def calculate_gl(gi, carbs):
        return (gi * carbs) / 100

    limits = {
        "type2": (55, 20),
        "type1": (60, 25),
        "prediabetes": (50, 15),
        "gestational": (45, 10),
        "none": (100, 100)
    }

    gi_limit, gl_limit = limits.get(
        current_user.diabetes_type,
        (100, 100)
    )

    quota = daily2.query.filter_by(
        user_id=current_user.id
    ).first()

    total_cal = (
        (quota.br_cal or 0) +
        (quota.el_cal or 0) +
        (quota.lu_cal or 0) +
        (quota.sn_cal or 0) +
        (quota.di_cal or 0)
    )

    remaining_calories = (
        current_user.cal or 0
    ) - total_cal

    foods = menu.query.all()

    filtered_foods = []

    def calculate_score(food):

        gi = food.glycemic_index or 50
        carbs = food.carbs or 0
        cal = float(food.cal or 0)

        gl = calculate_gl(gi, carbs)

        score = (
            (gl * 0.4) +
            (carbs * 0.25) +
            (gi * 0.2) +
            (cal * 0.15)
        )

        if remaining_calories < 300:
            score += cal * 0.2

        return score

    for food in foods:

        if current_user.allergy1 and food.allergen1:
            if current_user.allergy1.lower() in food.allergen1.lower():
                continue

        if current_user.allergy2 and food.allergen2:
            if current_user.allergy2.lower() in food.allergen2.lower():
                continue

        gi = food.glycemic_index or 50
        carbs = food.carbs or 0

        gl = calculate_gl(gi, carbs)

        if current_user.diabetes_type != "none" and gi > gi_limit:
            continue

        if current_user.diabetes_type != "none" and gl > gl_limit:
            continue

        score = calculate_score(food)

        filtered_foods.append({
            "food": food,
            "gi": gi,
            "gl": gl,
            "score": score
        })

    filtered_foods.sort(
        key=lambda x: x["score"]
    )

    return render_template(
        "select_food1.html",
        menu=filtered_foods,
        daily=quota
    )

@app.route('/U_Discover')
@login_required
def U_Discover():
    return render_template('U_Discover.html',menu=menu.query.all(), users=User.query.all(), daily2=daily2.query.all())

@app.route('/U_Exercises')
@login_required
def U_Exercises():

    exercises = Exercise.query.all()

    excess = 0

    today = datetime.now().strftime('%Y-%m-%d')

    quota = daily2.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()

    if quota:

        consumed = (
        (quota.br_cal or 0) +
        (quota.lu_cal or 0) +
        (quota.di_cal or 0)
    )

    burned = quota.burned_cal or 0

    net_total = consumed - burned

    excess = max(0, net_total - current_user.cal)

    suggested = []

    if excess < 0:

        suggested = Exercise.query.filter(
            Exercise.calories_burn >= excess / 2
        ).all()

    return render_template(
        'U_Exercises.html',
        exercises=exercises,
        excess=excess,
        suggested=suggested
    )

@app.route('/exercise/<int:id>')
@login_required
def exercise_detail(id):

    exercise = Exercise.query.get_or_404(id)

    return render_template(
        'exercise_detail.html',
        exercise=exercise
    )

@app.route('/burn_exercise/<int:id>')
@login_required
def burn_exercise(id):

    exercise = Exercise.query.get_or_404(id)

    today = datetime.now().strftime('%Y-%m-%d')

    quota = daily2.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()

    if quota:

        burned = exercise.calories_burn or 0

        quota.burned_cal = (
            quota.burned_cal or 0
        ) + burned

        consumed = (
            (quota.br_cal or 0) +
            (quota.el_cal or 0) +
            (quota.lu_cal or 0) +
            (quota.sn_cal or 0) +
            (quota.di_cal or 0)
        )

        quota.usr_cal = (
            consumed - quota.burned_cal
        )

        db.session.commit()

    return redirect(
        url_for(
            'U_Home_page',
            msg='burned'
        )
    )

@app.route('/U_Select_food', methods=['GET', 'POST'])
@login_required
def U_Select_food():

    if request.method == 'POST':
     feed = Feed(name=request.form['name'], message=request.form['message'], timestamp=str(datetime.now()))
     db.session.add(feed)
     db.session.commit()
    
    return render_template('U_Select_food.html',menu=menu.query.all(), users=User.query.all(), daily2=daily2.query.all())

@app.route('/U_Settings', methods=['GET', 'POST'])
@login_required
def U_Settings():
    
    if request.method == 'POST':
     feed = Feed(name=request.form['name'], message=request.form['message'], timestamp=str(datetime.now()))
     db.session.add(feed)
     db.session.commit()

    return render_template('U_Settings.html',fname=current_user.fname,email=current_user.email, lname=current_user.lname)


@app.route('/UpdateUser', methods=['POST'])
@login_required
def UpdateUser():
    if request.method == 'POST':
        curr_user = User.query.get(current_user.id)
        curr_user.fname = request.form['fname']
        curr_user.lname = request.form['lname']
        curr_user.email = request.form['email']
        curr_user.phone = request.form['phone']
        db.session.commit()
    return redirect(url_for('U_Settings'))

@app.route('/UpdateMeasure', methods=['POST'])
@login_required
def UpdateMeasure():
    if request.method == 'POST':
        curr_user = User.query.get(current_user.id)
        curr_user.height = request.form['height']
        curr_user.weight = request.form['weight']
        curr_user.gender = request.form['gender']
        curr_user.age = request.form['age']
        curr_user.bodytype = request.form['bodytype']
        curr_user.diabetes_type = request.form['diabetes_type']
        db.session.commit()
    return redirect(url_for('U_Settings'))

@app.route('/UpdatePassword', methods=['POST'])
@login_required
def UpdatePassword():
    if request.method=='POST':
        usr=User.query.get(current_user.id)
        old_pass = request.form['old-pass']
        new_pass = request.form['new-pass']
        print(old_pass, new_pass)
        print(usr.password, generate_password_hash(new_pass, method='pbkdf2:sha256'))
        new_pass_hash = generate_password_hash(new_pass, method='pbkdf2:sha256')
        if check_password_hash(usr.password, old_pass):
            usr.password=generate_password_hash(new_pass, method='pbkdf2:sha256')
            db.session.commit()
            flash("Password Changed")
        else:
            flash("Old Password does not match")
    return redirect(url_for('U_Settings'))



@app.route('/User_database')
@login_required
def User_database():
    return render_template('Admin_User_Viewer.html', users=User.query.all())


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('User_database'))

@app.route('/Admin_Panel')
@login_required
def Admin_Panel():
    return render_template('Admin_Panel.html', menu=menu.query.all())



@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_menu_item(id):
    menu_item = menu.query.get_or_404(id)
    db.session.delete(menu_item)
    db.session.commit()

    return redirect(url_for('Admin_Panel'))


@app.route('/Feedback_Admin_Side')
@login_required
def Feedback_Admin_Side(): 
    feed_data = Feed.query.all()
    return render_template('Feedback_Admin_Side.html', feed=feed_data)



@app.route('/new2', methods=['GET', 'POST'])
@login_required
def new2():
    if request.method == 'POST':
        cal100_ = round((int(request.form['cal'])*100)/int(request.form['stdwt']),2)

        file1 = request.files['file1']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        length = len(path)
        print(path)
        path1 = path[13:]
        print(path1)
        file1.save(path)

        food = menu(item=request.form['item'], cal=request.form['cal'], stdwt=request.form['stdwt'],
                cal100=cal100_, meal=request.form['meal'], allergen1=request.form['allergen1'],
                    allergen2=request.form['allergen2'], glycemic_index=request.form['gi'],carbs=request.form['carbs'],
                    imgpath=str(path1),quantity=request.form['quantity'])

        db.session.add(food)
        db.session.commit()

        return redirect(url_for('Admin_Panel'))
    return render_template('new2.html')


@app.route('/new1', methods=['GET', 'POST'])
@login_required
def new1():
    if request.method == 'POST':
        if not request.form['fname'] or not request.form['lname']  or not request.form['email'] or not \
                request.form['phn'] or not request.form['dob'] or not request.form['pass'] or not request.form['pass1'] or not request.form['weight'] or not \
                request.form['height'] or not request.form['age'] or not request.form['gender'] or not request.form['bdy'] or not \
                request.form['act'] or not request.form['goal'] :
                
            flash('Please enter all the required* fields')
            return redirect(url_for('signup'))
        else:
            obj = MakeMeal(int(int(request.form['weight']) * 2.204), goal=request.form['goal'],
                           activity_level=request.form['act'], body_type=request.form['bdy'])
            cal_ = (obj.daily_min_calories() + obj.daily_max_calories()) / 2
            fat_ = (obj.daily_min_fat() + obj.daily_max_fat()) / 2
            protein_ = (obj.daily_min_protein() + obj.daily_max_protein()) / 2
            carbs_ = (obj.daily_min_carbs() + obj.daily_max_carbs()) / 2        
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            email = request.form.get('email')
            phone = request.form.get('phn')
            dob= request.form.get('dob')
            password = request.form.get('pass')
            weight = request.form.get('weight')
            height = request.form.get('height')
            age = request.form.get('age')
            gender = request.form.get('gender')
            bodytype = request.form.get('bdy')
            activity = request.form.get('act')
            goal = request.form.get('goal')
            diabetes_type = request.form.get('diabetes_type')
            gi_preference = request.form.get('gi_preference')
            allergy1=request.form.get('allergy1')
            allergy2=request.form.get('allergy2') 
        new_user1 = User(fname=fname, lname=lname, email=email, phone=phone,dob=dob,password=generate_password_hash(password, method='pbkdf2:sha256'),weight=weight,height=height,age=age,gender=gender,bodytype=bodytype,activity=activity,goal=goal,diabetes_type=diabetes_type,gi_preference=gi_preference,allergy1=allergy1,allergy2=allergy2,cal=cal_, fat=fat_, protein=protein_, carbs=carbs_)
        if new_user1:
                db.session.add(new_user1)
                db.session.commit()
                return redirect(url_for('User_database'))
    return render_template('new1.html')


@app.route('/edit_food/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_food(id):
    item = menu.query.get_or_404(id)

    if request.method == 'POST':
        item.item = request.form['item']
        item.cal = request.form['cal']
        item.stdwt = request.form['stdwt']
        item.cal100 = request.form['cal100']
        item.meal = request.form['meal']
        item.allergen1 = request.form['allergen1']
        item.allergen2 = request.form['allergen2']
        item.glycemic_index = request.form['glycemic_index']
        item.carbs = request.form['carbs']
        item.imgpath = request.form['img']
        
        db.session.commit()
        return redirect('/Admin_Panel')
        

    return render_template('edit_food.html', item=item)


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.fname = request.form['fname']
        user.lname = request.form['lname']
        user.age = request.form['age']
        user.email = request.form['email']
        user.phone = request.form['phn']
        user.dob = request.form['dob']
        user.password = request.form['pass']
        user.weight = request.form['weight']
        user.height = request.form['height']
        user.gender = request.form['gender']
        user.goal = request.form['goal']
        user.bodytype = request.form['bodytype']
        user.activity = request.form['act']
        user.diabetes_type = request.form['diabetes_type']
        user.gi_preference = request.form['gi_preference']
        user.allergy1 = request.form['allergy1']
        user.allergy2 = request.form['allergy2']
        user.cal = request.form['cal']
        user.fat = request.form['fat']
        user.protein = request.form['protein']
        user.carbs = request.form['carbs']
        
        
        db.session.commit()
        return redirect('/User_database')
        

    return render_template('edit_user.html', user=user)



@app.route('/live')
@login_required
def index():

    nutrition = None

    if food_label:
        nutrition = Nutrition.query.filter(
            Nutrition.food_name.ilike(f"%{food_label}%")
        ).first()


    return render_template(
        'index1.html',
        food_label=food_label,
        detected=detection_done,
        nutrition=nutrition
    )

@app.route('/video_feed')
@login_required
def video_feed():
    global camera

    # Restart camera if it was released
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        print("Camera restarted")

    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/reset')
@login_required
def reset():
    global food_label, captured_frame, detection_done
    food_label = ''
    captured_frame = None
    detection_done = False
    return redirect(url_for('index'))

@app.route('/detect_status')
@login_required
def detect_status():
    global detection_done, food_label

    nutrition = None
    diabetic_info = None

    if food_label:
        nutrition = Nutrition.query.filter(
            Nutrition.food_name.ilike(f"%{food_label}%")
        ).first()

        diabetic_info = get_diabetic_status(food_label, current_user)

    return {
        "detected": detection_done,
        "food": food_label,

        "nutrition": {
            "quantity": nutrition.quantity if nutrition else None,
            "glycemic_i": nutrition.glycemic_i if nutrition else None,
            "calories": nutrition.calories if nutrition else None,
            "protein": nutrition.protein if nutrition else None,
            "carbs": nutrition.carbs if nutrition else None,
            "fat": nutrition.fat if nutrition else None,
            "suggestion": nutrition.suggestion if nutrition else "No data available"
        } if nutrition else None,

        "diabetic": diabetic_info
    }



@app.route('/stop_camera', methods=['POST'])
@login_required
def stop_camera():
    global camera

    if camera.isOpened():
        camera.release()
        print("Camera released")

    return {"status": "stopped"}


@app.route('/confirm', methods=['POST'])
@login_required
def confirm():

    today = datetime.now().strftime('%Y-%m-%d')

    quota = daily2.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()

    if not quota:

        quota = daily2(
            user_id=current_user.id,
            date=today,
            usr_cal=0,

            br_item='',
            br_cal=0,

            el_item='',
            el_cal=0,

            lu_item='',
            lu_cal=0,

            sn_item='',
            sn_cal=0,

            di_item='',
            di_cal=0
        )

        db.session.add(quota)
        db.session.commit()

    total_cal = (
        (quota.br_cal or 0) +
        (quota.el_cal or 0) +
        (quota.lu_cal or 0) +
        (quota.sn_cal or 0) +
        (quota.di_cal or 0)
    )

    target = current_user.cal

    meal_type = request.form['type']
    cal = float(request.form['cal'])
    item = request.form['item']


    # =========================
    # DIABETIC CHECK
    # =========================

    selected_food = menu.query.filter_by(
        item=item
    ).first()

    if selected_food:

        gi = selected_food.glycemic_index or 50
        carbs = selected_food.carbs or 0

        gl = (gi * carbs) / 100

        if (
            current_user.diabetes_type != "none"
            and gl > 20
        ):

            flash(
                "Not suitable for diabetic patients"
            )

            return redirect(
                url_for('U_Diet_recommender')
            )

    # =========================
    # DAILY LIMIT
    # =========================

    new_total = total_cal + cal

    net_total = new_total - (
        quota.burned_cal or 0
    )

    percentage = (
        (net_total / target) * 100
        if target > 0 else 0
    )

    if percentage > 100:
        msg = "limit"

    elif percentage >= 80:
        msg = "warning"

    else:
        msg = "good"

    # =========================
    # ADD MEAL
    # =========================

    if meal_type == 'breakfast':

        quota.br_item = (
            quota.br_item + ", " + item
        ) if quota.br_item else item

        quota.br_cal = (
            quota.br_cal or 0
        ) + cal

    elif meal_type == 'elevenses':

        quota.el_item = (
            quota.el_item + ", " + item
        ) if quota.el_item else item

        quota.el_cal = (
            quota.el_cal or 0
        ) + cal

    elif meal_type == 'lunch':

        quota.lu_item = (
            quota.lu_item + ", " + item
        ) if quota.lu_item else item

        quota.lu_cal = (
            quota.lu_cal or 0
        ) + cal

    elif meal_type == 'snacks':

        quota.sn_item = (
            quota.sn_item + ", " + item
        ) if quota.sn_item else item

        quota.sn_cal = (
            quota.sn_cal or 0
        ) + cal

    elif meal_type == 'dinner':

        quota.di_item = (
            quota.di_item + ", " + item
        ) if quota.di_item else item

        quota.di_cal = (
            quota.di_cal or 0
        ) + cal

    # =========================
    # UPDATE USER TOTAL
    # =========================

    consumed = (
        (quota.br_cal or 0) +
        (quota.el_cal or 0) +
        (quota.lu_cal or 0) +
        (quota.sn_cal or 0) +
        (quota.di_cal or 0)
    )

    quota.usr_cal = (
        consumed - (
            quota.burned_cal or 0
        )
    )

    # =========================
    # SAVE LOG
    # =========================

    new_log = MealLog(
        user_id=current_user.id,
        food_name=item,
        calories=cal,
        meal_type=meal_type,
        time=datetime.now().strftime("%I:%M %p"),
        date=today
    )

    db.session.add(new_log)

    db.session.add(quota)

    db.session.commit()

    return redirect(
        url_for(
            'U_Home_page',
            msg=msg
        )
    )

@app.route('/signup', methods=['GET','POST'])
def signup():
    
    if request.method == 'POST':
        if not request.form['fname'] or not request.form['lname']  or not request.form['email'] or not \
                request.form['phn'] or not request.form['dob'] or not request.form['pass'] or not request.form['pass1'] or not request.form['weight'] or not \
                request.form['height'] or not request.form['age'] or not request.form['gender'] or not request.form['bdy'] or not \
                request.form['act'] or not request.form['goal'] :
                
            flash('Please enter all the required* fields')
            return redirect(url_for('signup'))
        
        else:
            
            obj = MakeMeal(int(int(request.form['weight']) * 2.204), goal=request.form['goal'],
                           activity_level=request.form['act'], body_type=request.form['bdy'])
            cal_ = (obj.daily_min_calories() + obj.daily_max_calories()) / 2
            fat_ = (obj.daily_min_fat() + obj.daily_max_fat()) / 2
            protein_ = (obj.daily_min_protein() + obj.daily_max_protein()) / 2
            carbs_ = (obj.daily_min_carbs() + obj.daily_max_carbs()) / 2        
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            email = request.form.get('email')
            phone = request.form.get('phn')
            dob= request.form.get('dob')
            password = request.form.get('pass')
            weight = request.form.get('weight')
            height = request.form.get('height')
            age = request.form.get('age')
            gender = request.form.get('gender')
            bodytype = request.form.get('bdy')
            activity = request.form.get('act')
            goal = request.form.get('goal')
            diabetes_type = request.form.get('diabetes_type')
            gi_preference = request.form.get('gi_preference')
            allergy1=request.form.get('allergy1')
            allergy2=request.form.get('allergy2') 

            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            Pattern = re.compile("(0|91)?[6-9][0-9]{9}")
            if not (re.fullmatch(regex, email)):
                flash("Enter a valid email")
                return redirect(url_for('signup'))   

            if not (Pattern.match(phone)):
                flash("Enter a valid phone no")
                return redirect(url_for('signup'))

        

            user = User.query.filter_by(email=email).first()  # if this returns a user, then the email already exists in database

            if user:  # if a user is found, we want to redirect back to signup page so user can try again
                flash('Email address already exists!')
                return redirect(url_for('signup'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
            new_user = User(fname=fname, lname=lname, email=email, phone=phone,dob=dob,password=generate_password_hash(password, method='pbkdf2:sha256'),weight=weight,height=height,age=age,gender=gender,bodytype=bodytype,activity=activity,goal=goal,diabetes_type=diabetes_type,gi_preference=gi_preference,allergy1=allergy1,allergy2=allergy2,cal=cal_, fat=fat_, protein=protein_, carbs=carbs_)
            if new_user:
                    db.session.add(new_user)
                    db.session.commit()
                    flash('New account created!')
                    return redirect(url_for('login'))

        
        
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET','POST'])
def login():

    global food_label, captured_frame, detection_done

    food_label = ''
    captured_frame = None
    detection_done = False

    log_obj = logsession.query.all()
    previous = log_obj[-1].log_date
    if request.method == 'POST':
        
        email = request.form.get('email')
        password = request.form.get('pass')

        user = User.query.filter_by(email=email).first()
    
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login')) # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user)
        ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S')
        ind_date = datetime.today().strftime('%d-%m-%Y')

        
        today = datetime.now().strftime('%Y-%m-%d')
        quota = daily2.query.filter_by(user_id=current_user.id).first()

        # if no record exists, create one
        if not quota:
            quota = daily2(
                user_id=current_user.id,
                date=today,
                br_item='', br_cal=0.0,
                lu_item='', lu_cal=0.0,
                di_item='', di_cal=0.0
            )
            db.session.add(quota)
            db.session.commit()

        log = logsession(log_date=ind_date, log_time=ind_time)
        db.session.add(log)
        db.session.commit()

        if current_user.utype == "user":
            return redirect(url_for('U_Home_page'))
        elif current_user.utype == "admin":
            return redirect(url_for('User_database'))

    return render_template('login.html')







@app.route('/logout')
@login_required
def logout():

    global food_label, captured_frame, detection_done, camera

    food_label = ''
    captured_frame = None
    detection_done = False
   
    logout_user()
    ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S')
    ind_date = datetime.today().strftime('%Y-%m-%d')
    log = logsession(log_date=ind_date, log_time=ind_time)  
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    app.run(host='0.0.0.0',debug=True,port=5200)
