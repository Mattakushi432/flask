from flask import Flask, request, render_template, session, redirect
from functools import wraps
import os
import dotenv
from sqlalchemy.exc import IntegrityError

from sql_engine import Session
from models import User, Category, Transaction

app = Flask(__name__)
dotenv.load_dotenv('.env')
app.secret_key = os.environ.get('secret_key')
if not app.secret_key:
    raise ValueError("Secret key is not set in the environment variables.")

db_session = Session()
if not db_session:
    raise ValueError("Database session could not be created. Check your database connection.")

INCOME = 1
SPEND = 2


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
        user = db_session.query(User).filter_by(email=email).first()
        if user and user.check_password(password):
            session['user'] = {'id': user.id, 'name': user.name, 'surname': user.surname, 'email': user.email}
            return redirect('/income')
        return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        try:
            new_user = User(
                name=request.form['name'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                email=request.form['email'],
                date_of_birth=request.form['date_of_birth'],
                country=request.form['country'],
            )
            new_user.set_password(request.form['password'])
            db_session.add(new_user)
            db_session.commit()
            return redirect('/login')
        except IntegrityError:
            db_session.rollback()
            return render_template('register.html', error='Email already exists')
    return render_template('register.html')


@app.route('/category', methods=['GET', 'POST'])
@login_required
def category_page():
    user_id = session['user']['id']
    if request.method == 'POST':
        category_name = request.form['name']
        if category_name:
            new_category = Category(name=category_name, owner=user_id)
            db_session.add(new_category)
            db_session.commit()
        return redirect('/income')
    user_categories = db_session.query(Category).filter_by(owner=user_id).all()
    return render_template('category_list.html', categories=user_categories)


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def get_category(category_id):
    category = db_session.query(Category).filter_by(id=category_id, owner=session['user']['id']).first()
    if not category:
        return redirect('/category')
    if request.method == 'POST':
        new_name = request.form['name']
        if new_name:
            category.name = new_name
            db_session.commit()
        return redirect('/category')
    return render_template('edit_category.html', category=category)


@app.route('/category/<int:category_id>/delete', methods=['GET'])
@login_required
def delete_category(category_id):
    category = db_session.query(Category).filter_by(id=category_id, owner=session['user']['id']).first()
    if category:
        db_session.delete(category)
        db_session.commit()
    return redirect('/category')


@app.route('/income', methods=['GET', 'POST'])
@login_required
def get_all_income():
    user_id = session['user']['id']
    if request.method == 'POST':
        transaction_data = Transaction(
            description=request.form['description'],
            amount=request.form['amount'],
            category=request.form['category'],
            transaction_date=request.form['transaction_date'],
            transaction_type=INCOME,
            owner=user_id
        )
        db_session.add(transaction_data)
        db_session.commit()
        return redirect('/income')
    income_data = db_session.query(Transaction).filter_by(owner=user_id, transaction_type=INCOME).all()
    category_data = db_session.query(Category).filter_by(owner=user_id).all()
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
        transaction_data = Transaction(
            description=request.form['description'],
            amount=request.form['amount'],
            category=request.form['category'],
            transaction_date=request.form['transaction_date'],
            transaction_type=SPEND,
            owner=user_id
        )
        db_session.add(transaction_data)
        db_session.commit()
        return redirect('/income')
    spend_data = db_session.query(Transaction).filter_by(owner=user_id, transaction_type=SPEND).all()
    category_data = db_session.query(Category).filter_by(owner=user_id).all()
    return render_template('income.html', paypal=spend_data, category=category_data)



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
