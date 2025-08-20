from flask import Flask, request, render_template, session, redirect
from functools import wraps
import os
import dotenv
from sqlalchemy.exc import IntegrityError
from datetime import datetime

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


@app.route('/user', methods=['GET'])
@login_required
def get_user():
    user_id = session['user']['id']
    user = db_session.query(User).filter_by(id=user_id).first()
    if not user:
        return redirect('/login')

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date and end_date:
        try:
            date_from = datetime.strptime(start_date, '%Y-%m-%d').date()
            date_to = datetime.strptime(end_date, '%Y-%m-%d').date()
            transactions = db_session.query(Transaction).filter(
                Transaction.owner == user_id,
                Transaction.transaction_date.between(date_from, date_to)
            ).all()
        except ValueError:
            transactions = db_session.query(Transaction).filter_by(owner=user_id).all()
    else:
        transactions = db_session.query(Transaction).filter_by(owner=user_id).all()

    total_income = 0.0
    total_spend = 0.0
    for t in transactions:
        if t.transaction_type == INCOME:
            total_income += float(t.amount or 0)
        elif t.transaction_type == SPEND:
            total_spend += float(t.amount or 0)
    balance = total_income - total_spend

    user_categories = db_session.query(Category).filter_by(owner=user_id).all()
    cat_map = {c.id: c.name for c in user_categories}
    spend_totals = {}
    for t in transactions:
        if t.transaction_type == SPEND:
            name = cat_map.get(t.category, 'Uncategorized')
            spend_totals[name] = spend_totals.get(name, 0.0) + float(t.amount or 0)
    spend_by_category = sorted(spend_totals.items(), key=lambda kv: kv[0].lower())

    recent_transactions = sorted(transactions, key=lambda tr: (tr.transaction_date or ''), reverse=True)[:10]

    return render_template(
        'dashboard.html',
        user=user,
        transactions=transactions,
        total_income=total_income,
        total_spend=total_spend,
        balance=balance,
        spend_by_category=spend_by_category,
        recent_transactions=recent_transactions
    )


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db_session.query(User).filter_by(email=email).first()
        if user and user.check_password(password):
            session['user'] = {'id': user.id, 'name': user.name, 'first_name': user.first_name, 'email': user.email}
            return redirect('/user')
        return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        try:
            date_of_birth_str = request.form.get('date_of_birth')
            date_of_birth_obj = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            new_user = User(
                name=request.form.get('name'),
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                email=request.form.get('email'),
                date_of_birth=date_of_birth_obj,
                country=request.form.get('country'),
            )
            new_user.set_password(password)
            db_session.add(new_user)
            db_session.commit()
            return redirect('/login')
        except IntegrityError:
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
        return redirect('/category')
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
        try:
            description = request.form['description']
            amount = float(request.form['amount'])
            category_id = int(request.form['category_id'])
            transaction_date = request.form['transaction_date']
        except (KeyError, ValueError):
            income_data = db_session.query(Transaction).filter_by(owner=user_id, transaction_type=INCOME).all()
            category_data = db_session.query(Category).filter_by(owner=user_id).all()
            return render_template('income.html', paypal=income_data, category=category_data,
                                   error='Please provide valid input values.')

        transaction_data = Transaction(
            description=description,
            amount=amount,
            category=category_id,
            transaction_date=transaction_date,
            transaction_type=INCOME,
            owner=user_id
        )
        db_session.add(transaction_data)
        db_session.commit()
        return redirect('/user')
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


@app.route('/income/<int:income_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_income(income_id):
    user_id = session['user']['id']
    income = db_session.query(Transaction).filter_by(transaction_id=income_id, owner=user_id,
                                                     transaction_type=INCOME).first()
    if not income:
        return redirect('/income')
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        category_id = request.form.get('category_id')
        transaction_date = request.form.get('transaction_date')
        if description is not None:
            income.description = description
        if amount is not None:
            try:
                income.amount = float(amount)
            except ValueError:
                pass
        if category_id is not None:
            try:
                income.category = int(category_id)
            except ValueError:
                pass
        if transaction_date:
            income.transaction_date = transaction_date
        db_session.commit()
        return redirect('/income')
    category_data = db_session.query(Category).filter_by(owner=user_id).all()
    return render_template('edit_income.html', income=income, category=category_data)


@app.route('/income/<int:income_id>/delete', methods=['POST'])
@login_required
def delete_income(income_id):
    user_id = session['user']['id']
    income = db_session.query(Transaction).filter_by(transaction_id=income_id, owner=user_id,
                                                     transaction_type=INCOME).first()
    if income:
        db_session.delete(income)
        db_session.commit()
    return redirect('/income')


@app.route('/spend', methods=['GET', 'POST'])
@login_required
def get_all_spend():
    user_id = session['user']['id']
    if request.method == 'POST':
        try:
            description = request.form['description']
            amount = float(request.form['amount'])
            category_id = int(request.form['category_id'])
            transaction_date = request.form['transaction_date']
        except (KeyError, ValueError):
            spend_data = db_session.query(Transaction).filter_by(owner=user_id, transaction_type=SPEND).all()
            category_data = db_session.query(Category).filter_by(owner=user_id).all()
            return render_template('spend.html', paypal=spend_data, category=category_data,
                                   error='Please provide valid input values.')

        transaction_data = Transaction(
            description=description,
            amount=amount,
            category=category_id,
            transaction_date=transaction_date,
            transaction_type=SPEND,
            owner=user_id
        )
        db_session.add(transaction_data)
        db_session.commit()
        return redirect('/user')
    spend_data = db_session.query(Transaction).filter_by(owner=user_id, transaction_type=SPEND).all()
    category_data = db_session.query(Category).filter_by(owner=user_id).all()
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


@app.route('/spend/<int:spend_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_spend(spend_id):
    user_id = session['user']['id']
    spend = db_session.query(Transaction).filter_by(transaction_id=spend_id, owner=user_id,
                                                    transaction_type=SPEND).first()
    if not spend:
        return redirect('/spend')
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        category_id = request.form.get('category_id')
        transaction_date = request.form.get('transaction_date')
        if description is not None:
            spend.description = description
        if amount is not None:
            try:
                spend.amount = float(amount)
            except ValueError:
                pass
        if category_id is not None:
            try:
                spend.category = int(category_id)
            except ValueError:
                pass
        if transaction_date:
            spend.transaction_date = transaction_date
        db_session.commit()
        return redirect('/spend')
    category_data = db_session.query(Category).filter_by(owner=user_id).all()
    return render_template('edit_spend.html', spend=spend, category=category_data)


@app.route('/spend/<int:spend_id>/delete', methods=['POST'])
@login_required
def delete_spend(spend_id):
    user_id = session['user']['id']
    spend = db_session.query(Transaction).filter_by(transaction_id=spend_id, owner=user_id,
                                                    transaction_type=SPEND).first()
    if spend:
        db_session.delete(spend)
        db_session.commit()
    return redirect('/spend')


if __name__ == '__main__':
    app.run()
