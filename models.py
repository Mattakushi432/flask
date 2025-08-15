from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from werkzeug.security import generate_password_hash, check_password_hash
from sql_engine import Base, engine


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    password = Column(String(100))
    email = Column(String(100), unique=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.name!r}'




class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    owner = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))


class Transaction(Base):
    __tablename__ = 'paypal'

    transaction_id = Column(Integer, primary_key=True)
    description = Column(Text)
    category = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'))
    transaction_date = Column(String(50), nullable=False)
    transaction_type = Column(Integer, nullable=False)
    owner = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)

Base.metadata.create_all(engine)