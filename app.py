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
    if request.method == 'POST':
        return 'POST'
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        return render_template('register.html')
    else:
        return 'Hello World!'

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
