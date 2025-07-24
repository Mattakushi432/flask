from flask import Flask, request, render_template
app = Flask(__name__)


@app.route('/user', methods=['GET', 'POST'])
def get_user():
    return 'Hello World!'

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    return render_template('register.html')

@app.route('/category', methods=['GET', 'POST'])
def get_all_category():
    return 'Hello World!'

@app.route('/category/category_id', methods=['GET', 'PATCH', 'DELETE'])
def get_category(category_id):
    if request.method == 'GET':
        return f'Hello World!, {category_id}'
    elif request.method == 'PATCH':
        return 'PATCH'
    else:
        return 'DELETE'

@app.route('/income', methods=['GET', 'POST'])
def get_all_income():
    return 'Hello World!'
@app.route('/income/income_id', methods=['GET', 'PATCH', 'DELETE'])
def get_income(category_id):
    return f'Hello World!, {category_id}'

@app.route('/spend', methods=['GET', 'POST'])
def get_all_spend():
    return 'Hello World!'

@app.route('/spend/spend_id', methods=['GET', 'PATCH', 'DELETE'])
def get_spend(category_id):
    return f'Hello World!, {category_id}'


if __name__ == '__main__':
    app.run()
