from flask import Flask, request, render_template, session, redirect
from functools import wraps
import os
import dotenv
import sqlite3

app = Flask(__name__)
dotenv.load_dotenv('.env')
app.secret_key = os.environ.get('secret_key')
if not app.secret_key:
    raise ValueError("Secret key is not set in the environment variables.")

INCOME = 1
SPEND = 2


class sql_tracker:
    def __init__(self, db_tracker):
        self.db_tracker = db_tracker

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_tracker)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.commit()
        self.conn.close()


def login_required(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        else:
            return func(*args, **kwargs)

    return check_login


@app.route('/user', methods=['GET', 'POST'])
def get_user():
    if request.method == 'POST':
        return 'POST'
    return 'Hello World!'


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sql_tracker('db_tracker') as cursor:
            result = cursor.execute(f"SELECT * FROM user WHERE email = '{email}' and password = '{password}'")
            data = result.fetchone()
        if data:
            session['user'] = data[0]
            return redirect('/income')
        return render_template('login.html', error='Invalid email or password')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return 'You are logged out'


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form['name']
        surname = request.form['surname']
        password = request.form['password']
        email = request.form['email']
        with sql_tracker('db_tracker') as cursor:
            cursor.execute(f"SELECT * FROM user WHERE email = '{email}'")
            data = cursor.fetchone()
            if data:
                return f"User already exists"
            else:
                cursor.execute(
                    f"INSERT INTO user (name, surname, password, email) VALUES ('{name}', '{surname}', '{password}', '{email}')")
                return f"Registration successful!"


@app.route('/category', methods=['GET', 'POST'])
@login_required
def get_all_category():
    if request.method == 'POST':
        return 'POST'
    return 'Hello World!'


@app.route('/category/<int:category_id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def get_category(category_id):
    if request.method == 'GET':
        return f'Category: {category_id}'
    elif request.method == 'PATCH':
        return f'Update category: {category_id}'
    else:
        return f'Delete category: {category_id}'


@app.route('/income', methods=['GET', 'POST'])
@login_required
def get_all_income():
    if 'user' in session:
        if request.method == 'GET':
            with sql_tracker('db_tracker') as cursor:
                result = cursor.execute(
                    f"SELECT * FROM paypal WHERE owner = {session['user']} and transaction_type = {INCOME}")
                data = result.fetchall()
            return render_template('income.html', paypal=data)
        else:
            with sql_tracker('db_tracker') as cursor:
                description = request.form['description']
                category = request.form['category']
                transaction_date = request.form['transaction_date']
                owner = session['user']
                transaction_type = request.form['transaction_type']
                cursor.execute(
                    f"INSERT INTO paypal (description, category, transaction_date, transaction_type, owner) VALUES ('{description}', '{category}', '{transaction_date}', '{transaction_type}', '{owner}', '{INCOME}')")
            return redirect('/income')
    else:
        return redirect('/login')


@app.route('/income/<int:income_id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def get_income(income_id):
    if request.method == 'GET':
        return f'Income: {income_id}'
    elif request.method == 'PATCH':
        return f'Update income: {income_id}'
    else:
        return f'Delete income: {income_id}'


@app.route('/spend', methods=['GET', 'POST'])
@login_required
def get_all_spend():
    if 'user' in session:
        if request.method == 'GET':
            with sql_tracker('db_tracker') as cursor:
                result = cursor.execute(
                    f"SELECT * FROM paypal WHERE owner = {session['user']} and transaction_type = {SPEND}")
                data = result.fetchall()
            return render_template('spend.html', paypal=data)
        else:
            with sql_tracker('db_tracker') as cursor:
                description = request.form['description']
                category = request.form['category']
                transaction_date = request.form['transaction_date']
                owner = session['user']
                transaction_type = request.form['transaction_type']
                cursor.execute(
                    f"INSERT INTO paypal (description, category, transaction_date, transaction_type, owner) VALUES ('{description}', '{category}', '{transaction_date}', '{transaction_type}', '{owner}', '{SPEND}')")
            return redirect('/login')


@app.route('/spend/<int:spend_id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def get_spend(spend_id):
    if request.method == 'GET':
        return f'Spend: {spend_id}'
    elif request.method == 'PATCH':
        return f'Update spend: {spend_id}'
    else:
        return f'Delete spend: {spend_id}'


if __name__ == '__main__':
    app.run()
