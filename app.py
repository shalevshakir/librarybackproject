from flask import Flask, jsonify, request
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
    type = db.Column(db.Integer, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)  # This column tracks if the book is deleted


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
    books = Book.query.filter_by(is_deleted=False).all()  # Only return books that aren't deleted
    result = [
        {"id": book.id, "name": book.name, "author": book.author, "year_published": book.year_published, "type": book.type}
        for book in books
    ]
    return jsonify(result)

# create book
@app.route('/books', methods=['POST'])
def add_book():
    try:
        data = request.get_json()

        name = data.get('name')
        author = data.get('author')
        year_published = data.get('year_published')
        book_type = data.get('type')

        # Validate input
        if not name or not author or not year_published or not book_type:
            return jsonify({"error": "Missing required fields: name, author, year_published, and type"}), 400

        # Create new book instance
        new_book = Book(name=name, author=author, year_published=year_published, type=book_type)

        # Add to the database
        db.session.add(new_book)
        db.session.commit()

        return jsonify({"message": "Book added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/books/search/<string:book_name>', methods=['GET'])
def find_book_by_name(book_name):
    try:
        # Search for books that aren't marked as deleted
        books = Book.query.filter(Book.name.ilike(f'%{book_name}%'), Book.is_deleted == False).all()

        if not books:
            return jsonify({"message": "No books found matching the name"}), 404

        result = [
            {
                "id": book.id,
                "name": book.name,
                "author": book.author,
                "year_published": book.year_published,
                "type": book.type
            }
            for book in books
        ]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/books/delete/<int:book_id>', methods=['PUT'])
def soft_delete_book(book_id):
    try:
        # Fetch the book by ID
        book = Book.query.get(book_id)
        
        if not book:
            return jsonify({"message": "Book not found"}), 404

        # Mark the book as deleted
        book.is_deleted = True
        db.session.commit()

        return jsonify({"message": "Book has been marked as deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# crud for customer


# get all customers.
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    result = [{"id": customer.id, "name": customer.name, "city": customer.city, "age": customer.age} for customer in customers]
    return jsonify(result), 200


# get single customer
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get(id)
    
    if customer is None:
        return jsonify({"error": "Customer not found"}), 404

    result = {"id": customer.id, "name": customer.name, "city": customer.city, "age": customer.age}
    return jsonify(result), 200

@app.route('/customers/search/<string:customer_name>', methods=['GET'])
def find_customer_by_name(customer_name):
    try:
        # Search for customers by name (case insensitive)
        customers = Customer.query.filter(Customer.name.ilike(f'%{customer_name}%')).all()

        if not customers:
            return jsonify({"message": "No customers found matching the name"}), 404

        # Prepare the result
        result = [
            {
                "id": customer.id,
                "name": customer.name,
                "city": customer.city,
                "age": customer.age
            }
            for customer in customers
        ]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# function that create a new customer
def add_new_customer(name, city, age):
    # Create a new customer instance
    new_customer = Customer(name=name, city=city, age=age)
    
    # Add the new customer to the session
    db.session.add(new_customer)
    
    # Commit the session to save the new customer to the database
    db.session.commit()
    
    print(f"Customer '{name}' added successfully!")

# route to add new customer.
@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.get_json()
    name = data.get('name')
    city = data.get('city')
    age = data.get('age')

    add_new_customer(name, city, age)
    
    return jsonify({"message": f"Customer {name} added successfully!"}), 201



# update by id 
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    try:
        customer = Customer.query.get(id)
        
        if customer is None:
            return jsonify({"error": "Customer not found"}), 404

        data = request.get_json()
        name = data.get('name')
        city = data.get('city')
        age = data.get('age')

        # Validate input
        if not name or not city or not age:
            return jsonify({"error": "Missing required fields: name, city, or age"}), 400

        if not isinstance(age, int) or age < 0:
            return jsonify({"error": "Invalid age value"}), 400

        # Update customer details
        customer.name = name
        customer.city = city
        customer.age = age

        db.session.commit()
        return jsonify({"message": f"Customer '{name}' updated successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# delete customer function 

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    try:
        customer = Customer.query.get(id)
        
        if customer is None:
            return jsonify({"error": "Customer not found"}), 404

        # Delete the customer
        db.session.delete(customer)
        db.session.commit()

        return jsonify({"message": f"Customer '{customer.name}' deleted successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


# loans crud

# create
@app.route('/loans', methods=['POST'])
def add_loan():
    try:
        data = request.get_json()
        cust_id = data.get('cust_id')
        book_id = data.get('book_id')
        loan_date_str = data.get('loan_date')

        # Validate input
        if not cust_id or not book_id or not loan_date_str:
            return jsonify({"error": "Missing required fields: cust_id, book_id, loan_date"}), 400

        # Convert loan_date string to datetime object
        loan_date = datetime.strptime(loan_date_str, '%Y-%m-%d')

        # Fetch the book to determine its type
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        # Calculate the return date based on book type
        if book.type == 1:
            return_date = loan_date + timedelta(days=10)
        elif book.type == 2:
            return_date = loan_date + timedelta(days=5)
        elif book.type == 3:
            return_date = loan_date + timedelta(days=2)
        else:
            return jsonify({"error": "Invalid book type"}), 400

        # Create a new loan entry
        new_loan = Loan(cust_id=cust_id, book_id=book_id, loan_date=loan_date, return_date=return_date)
        db.session.add(new_loan)
        db.session.commit()

        return jsonify({"message": "Loan created successfully!", "return_date": return_date.strftime('%Y-%m-%d')}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # read and get all loans

@app.route('/loans', methods=['GET'])
def get_loans():
    loans = Loan.query.all()
    result = [
        {
            "id": loan.id,
            "cust_id": loan.cust_id,
            "book_id": loan.book_id,
            "loan_date": loan.loan_date,
            "return_date": loan.return_date
        }
        for loan in loans
    ]
    return jsonify(result), 200

# get only one loan by id
@app.route('/loans/<int:id>', methods=['GET'])
def get_loan(id):
    loan = Loan.query.get(id)
    
    if loan is None:
        return jsonify({"error": "Loan not found"}), 404

    result = {
        "id": loan.id,
        "cust_id": loan.cust_id,
        "book_id": loan.book_id,
        "loan_date": loan.loan_date,
        "return_date": loan.return_date
    }
    return jsonify(result), 200



@app.route('/loans/late', methods=['GET'])
def get_late_loans():
    try:
        # Get today's date
        today = datetime.now()

        # Query loans where the return date has passed and they're not yet returned
        late_loans = Loan.query.filter(Loan.return_date < today).all()

        if not late_loans:
            return jsonify({"message": "No late loans found"}), 200

        # Prepare the result
        result = [
            {
                "id": loan.id,
                "cust_id": loan.cust_id,
                "book_id": loan.book_id,
                "loan_date": loan.loan_date.strftime('%Y-%m-%d'),
                "return_date": loan.return_date.strftime('%Y-%m-%d'),
                "days_late": (today - loan.return_date).days
            }
            for loan in late_loans
        ]

        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500





# Initialize database 
with app.app_context():
    db.create_all()
    add_default_data()
if __name__ == '__main__':
    app.run(debug=True)
