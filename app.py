from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta

app = Flask(__name__)

# Enable CORS
CORS(app)

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)  # 1, 2, or 3

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)

    customer = db.relationship('Customer', backref='loans')
    book = db.relationship('Book', backref='loans')

def add_default_data():
    # Check if tables are empty
    if not Book.query.first() and not Customer.query.first() and not Loan.query.first():
        # Adding default books
        book1 = Book(name="Book A", author="Author A", year_published=2001, type=1)
        book2 = Book(name="Book B", author="Author B", year_published=2005, type=2)
        book3 = Book(name="Book C", author="Author C", year_published=2010, type=3)

        # Adding default customers
        customer1 = Customer(name="Customer One", city="City A", age=30)
        customer2 = Customer(name="Customer Two", city="City B", age=25)

        # Adding default loans (assuming cust_id=1 is for customer1 and book_id=1 is for book1, etc.)
        loan1 = Loan(cust_id=1, book_id=1, loan_date=datetime.utcnow(), return_date=datetime.utcnow() + timedelta(days=7))
        loan2 = Loan(cust_id=2, book_id=2, loan_date=datetime.utcnow(), return_date=datetime.utcnow() + timedelta(days=5))

        # Adding all to the session
        db.session.add_all([book1, book2, book3, customer1, customer2, loan1, loan2])

        # Commit the session to save data in the database
        db.session.commit()
        print("Default data added successfully!")
    else:
        print("Tables are not empty. Default data will not be added.")


# API Routes
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Library API"})

@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    result = [{"id": book.id, "name": book.name, "author": book.author, "year_published": book.year_published, "type": book.type} for book in books]
    return jsonify(result)

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    result = [{"id": customer.id, "name": customer.name, "city": customer.city, "age": customer.age} for customer in customers]
    return jsonify(result)

@app.route('/loans', methods=['GET'])
def get_loans():
    loans = Loan.query.all()
    result = [{"id": loan.id, "cust_id": loan.cust_id, "book_id": loan.book_id, "loan_date": loan.loan_date, "return_date": loan.return_date} for loan in loans]
    return jsonify(result)

# Initialize database 
with app.app_context():
    db.create_all()
    add_default_data()
if __name__ == '__main__':
    app.run(debug=True)
