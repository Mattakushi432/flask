import cursor
from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)


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


@app.route('/user', methods=['GET', 'POST'])
def get_user():
    if request.method == 'POST':
        return 'POST'
    return 'Hello World!'


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        with sql_tracker('db_tracker') as cursor:
            result = cursor.execute(f"SELECT * FROM user WHERE email = '{email}' and password = '{password}'")
            data = result.fetchone()
        if data:
            return f"correct user pair"
        else:
            return f"wrong user pair"


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
                cursor.execute(f"INSERT INTO user (name, surname, password, email) VALUES ('{name}', '{surname}', '{password}', '{email}')")
                return f"Registration successful!"



@app.route('/category', methods=['GET', 'POST'])
def get_all_category():
    if request.method == 'POST':
        return 'POST'
    return 'Hello World!'


@app.route('/category/<int:category_id>', methods=['GET', 'PATCH', 'DELETE'])
def get_category(category_id):
    if request.method == 'GET':
        return f'Category: {category_id}'
    elif request.method == 'PATCH':
        return f'Update category: {category_id}'
    else:
        return f'Delete category: {category_id}'


@app.route('/income', methods=['GET', 'POST'])
def get_all_income():
    if request.method == 'POST':
        return 'POST'
    return 'Hello World!'


@app.route('/income/<int:income_id>', methods=['GET', 'PATCH', 'DELETE'])
def get_income(income_id):
    if request.method == 'GET':
        return f'Income: {income_id}'
    elif request.method == 'PATCH':
        return f'Update income: {income_id}'
    else:
        return f'Delete income: {income_id}'


@app.route('/spend', methods=['GET', 'POST'])
def get_all_spend():
    if request.method == 'POST':
        return 'POST'
    return 'Hello World!'


@app.route('/spend/<int:spend_id>', methods=['GET', 'PATCH', 'DELETE'])
def get_spend(spend_id):
    if request.method == 'GET':
        return f'Spend: {spend_id}'
    elif request.method == 'PATCH':
        return f'Update spend: {spend_id}'
    else:
        return f'Delete spend: {spend_id}'


if __name__ == '__main__':
    app.run()
