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
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.commit()
        self.conn.close()


class DataBaseManager:
    def _execute(self, query, params=(), fetchone=False, fetchall=False):
        with sql_tracker('db_tracker') as cursor:
            cursor.execute(query, params)
            if fetchone:
                return cursor.fetchone()
            elif fetchall:
                return cursor.fetchall()

    def insert(self, table, data):
        keys = ', '.join(data.keys())
        values = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        try:
            self._execute(query, tuple(data.values()))
            return True
        except sqlite3.IntegrityError:
            return False

    def select(self, table, params=None, fetchone=False, fetchall=False):
        query = f"SELECT * FROM {table}"
        values = []
        if params:
            result_con = []
            for key, value in params.items():
                result_con.append(f"{key} = ?")
                values.append(value)
            query += f" WHERE {' AND '.join(result_con)}"
        return self._execute(query, values, fetchone=fetchone, fetchall=fetchall)

    def update(self, table, data, where_params):
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        where_clause = ' AND '.join([f"{key} = ?" for key in where_params.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + tuple(where_params.values())
        self._execute(query, params)

    def delete(self, table, where_params):
        where_clause = ' AND '.join([f"{key} = ?" for key in where_params.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        params = tuple(where_params.values())
        self._execute(query, params)


def login_required(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        else:
            return func(*args, **kwargs)

    return check_login


db = DataBaseManager()


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
        data = db.select('user', {'email': email, 'password': password}, fetchall=True)
        if data:
            session['user'] = dict(data[0])
            return redirect('/income')
        return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form['name']
        surname = request.form['surname']
        password = request.form['password']
        email = request.form['email']
        success = db.insert('user', {'name': name, 'surname': surname, 'password': password, 'email': email})
        if success:
            return redirect('/login')
        else:
            return render_template('register.html', error='Email already exists')


@app.route('/category', methods=['GET', 'POST'])
@login_required
def category_page():
    user_id = session['user']['id']
    if request.method == 'POST':
        category_name = request.form['name']
        if category_name:
            db.insert('category', {'name': category_name, 'owner': user_id})
        return redirect('/category')
    user_category = db.select('category', {'owner': user_id}, fetchall=True)
    return render_template('category_list.html', category=user_category)


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def get_category(category_id):
    user_id = session['user']['id']
    category = db.select('category', {'id': category_id, 'owner': user_id}, fetchone=True)
    if not category:
        return redirect('/category')
    if request.method == 'POST':
        new_name = request.form['name']
        if new_name:
            db.update('category', {'name': new_name}, {'id': category_id, 'owner': user_id})
        return redirect('/category')
    return render_template('edit_category.html', category=category)


@app.route('/category/<int:category_id>/delete', methods=['GET'])
@login_required
def delete_category(category_id):
    user_id = session['user']['id']
    db.delete('category', {'id': category_id, 'owner': user_id})
    return redirect('/category')


@app.route('/income', methods=['GET', 'POST'])
@login_required
def get_all_income():
    user_id = session['user']['id']
    if request.method == 'POST':
        transaction_data = {
            'description': request.form.get('description'),
            'amount': request.form.get('amount'),
            'category': request.form.get('category'),
            'transaction_date': request.form.get('transaction_date'),
            'transaction_type': INCOME,
            'owner': user_id
        }
        db.insert('paypal', transaction_data)
        return redirect('/income')

    income_data = db.select('paypal', {'owner': user_id, 'transaction_type': INCOME}, fetchall=True)
    category_data = db.select('category', {'owner': user_id}, fetchall=True)
    return render_template('income.html', paypal=income_data, category=category_data)


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
    user_id = session['user']['id']
    if request.method == 'POST':
        transaction_data = {
            'description': request.form['description'],
            'amount': request.form['amount'],
            'category': request.form['category'],
            'transaction_date': request.form['transaction_date'],
            'transaction_type': SPEND,
            'owner': user_id
        }
        db.insert('paypal', transaction_data)
        return redirect('/spend')
    spend_data = db.select('paypal', {'owner': user_id, 'transaction_type': SPEND}, fetchall=True)
    category_data = db.select('category', {'owner': user_id}, fetchall=True)
    return render_template('spend.html', paypal=spend_data, category=category_data)


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
