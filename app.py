# Import necessary libraries
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime, timedelta
from pytz import timezone

# Define timezone
zone = "Africa/Nairobi"

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///library.db")

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/signup")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Forget any user_id
        session.clear()

        state = int(request.form.get("state"))

       # Check whether user on Sign-up or Sign-in Form
       # State 0 = Sign-up; State 1 = Sign-in
        if state == 0:
            username = request.form.get("username")
            password = request.form.get("password")
            confirm_password = request.form.get("confirmation")
            status = request.form.get("status")

            # Check user input
            if not username:
                flash("Username Required")
                return render_template("signup.html")

            elif not password:
                flash("Password Required")
                return render_template("signup.html")

            elif not confirm_password:
                flash("Confirmation Password Required")
                return render_template("signup.html")

            elif password != confirm_password:
                flash("Password Mismatch")
                return render_template("signup.html")

            # Query database for username
            user = db.execute("SELECT * FROM users WHERE username = ?", username)

            if len(user) > 0:
                flash("Username in use")
                return render_template("signup.html")

            # Encrypt password
            hash = generate_password_hash(password)

            if status == 'admin':
                # Update admin database
                user = db.execute("INSERT INTO users (username, hash, student_id) VALUES (?, ?, ?)", username, hash, 'admin')

                # Remember which user has logged in
                session["user_id"] = user

                flash("Registration Successful")
                return render_template("index.html")

            else:
                # Update admin database
                student_id = request.form.get("student_id")

                # Validate input
                if not student_id:
                    flash("Student ID required")
                    return render_template("signup.html")

                # Check for student ID in students
                student = db.execute("SELECT * FROM students WHERE id LIKE ?", student_id)

                if len(student) == 0:
                    flash("Student ID Invalid")
                    return render_template("signup.html")

                user = db.execute("INSERT INTO users (username, hash, student_id) VALUES (?, ?, ?)", username, hash, student_id)

                # Remember which user has logged in
                session["user_id"] = user

                flash("Registration Successful")
                return render_template("index1.html")

        # State 0 = Sign-up; State 1 = Sign-in
        elif state == 1:
            username = request.form.get("username")
            password = request.form.get("password")

            # Check user input
            if not username:
                flash("Username Required: Redirecting to Signup")
                return render_template("signup.html")

            elif not password:
                flash("Password Required")
                return render_template("signup.html")

            user = db.execute("SELECT * FROM users WHERE username = ?", username)

            # Ensure username exists and password is correct
            if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
                flash("Incorrect Username or Password")
                return render_template("signup.html")

            # Remember which user has logged in
            session["user_id"] = user[0]["id"]

            # Redirect admin to admin page and student to student page
            if user[0]["student_id"] == "admin":
                flash("Welcome Admin")
                return redirect("/")

            else:
                flash(f"Welcome {user[0]['student_id']}")
                return redirect("/index1")

    # GET requests
    return render_template("signup.html")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # GET requests
    if request.method == "GET" and admin() == "admin":
        # Display current books issued to students
        books_request = db.execute("SELECT * FROM requests")
        books = db.execute("SELECT title, author, publisher FROM books WHERE id IN (SELECT book_id FROM requests)")

        # Add dates
        index = 0
        for book in books:
            book["student_id"] = books_request[index]["student_id"]
            book["issue_date"] = books_request[index]["issue_date"]
            book["due_date"] = books_request[index]["due_date"]
            index += 1

        return render_template("index.html", books=books)

    # POST requests
    elif request.method == "POST" and admin() == "admin":
        search = request.form.get("search")
        student_id = request.form.get("student_id")

        if search:
            # Display current books issued to specific student
            books_request = db.execute("SELECT * FROM requests WHERE student_id LIKE ?", search)

            # Flash message if no student found
            if len(books_request) == 0:
                flash(f"No Book Assigned to {search}")
                return render_template("index.html")

            books = db.execute("SELECT title, author, publisher FROM books WHERE id IN (SELECT book_id FROM requests)")

            # Add dates
            index = 0
            for book in books:
                book["student_id"] = books_request[index]["student_id"]
                book["issue_date"] = books_request[index]["issue_date"]
                book["due_date"] = books_request[index]["due_date"]
                index += 1

            return render_template("index.html", books=books)

        # Get student details
        elif student_id:
            student = db.execute("SELECT * FROM students WHERE id LIKE ?", student_id)
            return render_template("student.html", student=student)

        return redirect("/")

    # If stutent logs in
    else:
        return redirect("/index1")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to signin form
    return redirect("/signup")

@app.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    if request.method == "POST" and admin() == "admin":
        search = request.form.get("search")
        books  = db.execute("SELECT * FROM books WHERE title LIKE ?", f"%{search}%")
        return render_template("inventory.html", books=books)

    elif request.method == "GET" and admin() == "admin":
        books  = db.execute("SELECT * FROM books")
        return render_template("inventory.html", books=books)

    # Invalid student access
    else:
        flash("Invalid Acess")
        return render_template("index1.html")

@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    if request.method == "POST" and admin() == "admin":
        search = request.form.get("search")
        book_id = request.form.get("book_id")

        # Search book by title
        if search:
            books  = db.execute("SELECT * FROM books WHERE title LIKE ?", f"%{search}%")
            return render_template("update.html", books=books)

        # Get the book with the ID to edit details
        elif book_id:
            book  = db.execute("SELECT * FROM books WHERE id = ?", book_id)
            return render_template("edit.html", book=book)

        # Return inventory
        else:
            books  = db.execute("SELECT * FROM books")
            return render_template("update.html", books=books)

    # GET requests
    elif request.method == "GET" and admin() == "admin":
        books  = db.execute("SELECT * FROM books")
        return render_template("update.html", books=books)

    # Invalid student access
    else:
        flash("Invalid Acess")
        return render_template("index1.html")

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST" and admin() == "admin":
        book_id = request.form.get("book_id")
        title = request.form.get("title")
        author = request.form.get("author")
        publisher = request.form.get("publisher")
        stock = request.form.get("stock")

        # Update book details
        if title:
            db.execute("UPDATE books SET title=? WHERE id=?", title, book_id)

        if author:
             db.execute("UPDATE books SET author=? WHERE id=?", author, book_id)

        if publisher:
             db.execute("UPDATE books SET publisher=? WHERE id=?", publisher, book_id)

        if stock:
            if not stock.isdigit():
                flash("Invalid Stock Entry")
                books  = db.execute("SELECT * FROM books")
                return render_template("update.html", books=books)

            else:
                db.execute("UPDATE books SET stock=? WHERE id=?", stock, book_id)

        if title or author or publisher or stock:
            flash("Book Details Successfully Updated")

        else:
            flash("No Update Received")

        books  = db.execute("SELECT * FROM books")
        return render_template("update.html", books=books)

    # GET requests
    elif request.method == "GET" and admin() == "admin":
        books  = db.execute("SELECT * FROM books")
        return render_template("update.html", books=books)

    else:
        flash("Invalid Acess")
        return render_template("index1.html")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST" and admin() == "admin":
        title = request.form.get("title")
        author = request.form.get("author")
        publisher = request.form.get("publisher")
        stock = request.form.get("stock")

        # Check user input
        if not title:
            flash("Title Missing")
            db.execute("UPDATE books SET title=? WHERE id=?", title, book_id)

        elif not stock.isdigit():
            flash("Invalid Stock Entry")

        # Add book into database
        db.execute("INSERT INTO books (title, author, publisher, stock) VALUES (?, ?, ?, ?)", title, author, publisher, stock)

        flash("Book Added")
        return render_template("add.html")

    # GET requests
    elif request.method == "GET" and admin() == "admin":
        return render_template("add.html")

    else:
        flash("Invalid Acess")
        return render_template("index1.html")

@app.route("/index1", methods=["GET", "POST"])
@login_required
def index1():
    if request.method == "POST":
        book_id = request.form.get("book_id")

        # Get the student id
        student_id = db.execute("SELECT student_id FROM users WHERE id = ?", session["user_id"])

        # Check status of book in return
        book = db.execute("SELECT * FROM returns WHERE book_id=? AND student_id=?", book_id, student_id[0]["student_id"])

        # If return request had been submitted
        if len(book) > 0:
            flash("Book Return Request Already Submitted")
            return redirect("/return1")

        # Store return request
        db.execute("INSERT INTO returns (student_id, book_id) VALUES (?, ?)", student_id[0]["student_id"], book_id)
        flash("Request Submitted: Return book to library")
        return redirect("/return1")

    student_id = db.execute("SELECT student_id FROM users WHERE id = ?", session["user_id"])
    books = db.execute("SELECT * FROM books WHERE id IN (SELECT book_id FROM requests WHERE student_id = ?)", student_id[0]['student_id'])
    dates = db.execute("SELECT * FROM requests WHERE student_id = ?", student_id[0]['student_id'])

    # Add issue dates to books
    index = 0
    for book in books:
        book['issue_date'] = dates[index]['issue_date']
        book['due_date'] = dates[index]['due_date']
        index += 1

    return render_template("index1.html", books=books)

@app.route("/return1", methods=["GET", "POST"])
@login_required
def return1():
    # Student initiates book return request
    # Get the student id
    student_id = db.execute("SELECT student_id FROM users WHERE id = ?", session["user_id"])
    books = db.execute("SELECT title, author, publisher FROM books WHERE id IN (SELECT book_id FROM returns WHERE student_id = ?)", student_id[0]["student_id"])
    return render_template("return1.html", books=books)

@app.route("/return2", methods=["GET", "POST"])
@login_required
def return2():
    # Admin confirms book return requests
    if request.method == "POST" and admin() == "admin":

        search = request.form.get("search")
        book_id = request.form.get("book_id")
        student_id = request.form.get("student_id")

        # Search specific student usind ID
        if search:
            books = db.execute("SELECT id, title, author, publisher FROM books WHERE id IN (SELECT book_id FROM returns WHERE student_id LIKE ?)", search)
        # Add student_id to books
            for book in books:
                book["student_id"] = search

            return render_template("return2.html", books=books)

        # Confirm book return
        elif book_id:
            db.execute("DELETE FROM returns WHERE student_id LIKE ? AND book_id = ?", student_id, book_id)
            flash("Book Return Success")

            # Update book stock
            books  = db.execute("SELECT * FROM books WHERE id = ?", book_id)

            # Update stocks
            stock = books[0]['stock']
            stock += 1
            db.execute("UPDATE books SET stock=? WHERE id=?", stock, book_id)

            # Delete from student register:
            db.execute("DELETE FROM requests WHERE student_id = ? AND book_id = ?", student_id, book_id)
            return redirect("/return2")

        return redirect("/return2")

    # Admin views all book return requests
    elif request.method == "GET" and admin() == "admin":
        students = db.execute("SELECT * FROM returns")
        books = db.execute("SELECT id, title, author, publisher FROM books WHERE id IN (SELECT book_id FROM returns)")

        # Add student_id to books
        index = 0
        for book in books:
            book["student_id"] = students[index]['student_id']
            index += 1

        return render_template("return2.html", books=books)

    else:
        flash("Invalid Access")
        return redirect("/index1")

@app.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
    if request.method == "POST":
        # Get student ID
        student_id = db.execute("SELECT student_id FROM users WHERE id = ?", session["user_id"])
        message = request.form.get("message")

        if not message:
            flash("Empty Message")
            return render_template("messages.html")

        # Get time and date of specific timezone
        now = datetime.now(timezone(zone))
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")

        # Store messages on database
        db.execute("INSERT INTO messages(student_id, message, date, time) VALUES (?, ?, ?, ?)", student_id[0]["student_id"], message, date, time)

        # Confirm message sent
        flash("Message Sent")
        return render_template("messages.html")

    elif request.method == "GET":
        return render_template("messages.html")

@app.route("/messagelist", methods=["GET", "POST"])
@login_required
def messagelist():
    # Check for administrator
    if admin() == "admin":
        student_id = request.form.get("search")

        if student_id:
            messages = db.execute("SELECT * FROM messages WHERE student_id LIKE ? ORDER BY id DESC", student_id)

            if len(messages) <= 0:
                flash(f"No messages for {student_id}")
                return redirect("/messagelist")

            # Display messages
            return render_template("messagelist1.html", messages=messages)

        else:
            messages = db.execute("SELECT * FROM messages ORDER BY id DESC")
            return render_template("messagelist1.html", messages=messages)



    # Get student ID
    student_id = db.execute("SELECT student_id FROM users WHERE id = ?", session["user_id"])

    messages = db.execute("SELECT * FROM messages WHERE student_id LIKE ? ORDER BY id DESC", student_id[0]["student_id"])

    # Display messages
    return render_template("messagelist.html", messages=messages)

@app.route("/request1", methods=["GET", "POST"])
@login_required
def request1():
    if request.method == "POST":
        search = request.form.get("search")
        book_id = request.form.get("book_id")

        # Search book by title
        if search:
            books  = db.execute("SELECT * FROM books WHERE title LIKE ?", f"%{search}%")
            return render_template("request1.html", books=books)

        # Get the book with the ID to edit details
        elif book_id:
            book  = db.execute("SELECT * FROM books WHERE id = ?", book_id)

            # Update stocks
            stock = book[0]['stock']
            stock -=1

            if stock < 0:
                flash("Book Unavailable")
                return render_template("request1.html", books=books)

            # Ensure one book per students
            current = db.execute("SELECT * FROM requests WHERE book_id = ?", book_id)

            if len(current) > 0:
                book[0]['issue_date'] = current[0]['issue_date']
                book[0]['due_date'] = current[0]['due_date']

                flash("You've Been Issued The Book")
                return render_template("index1.html", books=book)

            student_id = db.execute("SELECT student_id FROM users WHERE id = ?", session["user_id"])
            books = db.execute("SELECT * FROM books WHERE id IN (SELECT book_id FROM requests WHERE student_id = ?)", student_id[0]['student_id'])

            # Maximum books ten
            if len(books) > 9:
                flash("Only Ten Books Allowed Per Student")
                return render_template("index1.html", books=books)

            db.execute("UPDATE books SET stock=? WHERE id=?", stock, book_id)

            # Get time and date of specific timezone
            now = datetime.now(timezone(zone))
            date = now.strftime("%d/%m/%Y")

            # Books provided for two weeks
            due_date = now + timedelta(days=14)
            due_date = due_date.strftime("%d/%m/%Y")

            # Update student current books
            db.execute("INSERT INTO requests (student_id, book_id, issue_date, due_date) VALUES (?, ?, ?, ?)", student_id[0]['student_id'], book_id, date, due_date)

            books = db.execute("SELECT * FROM books WHERE id IN (SELECT book_id FROM requests WHERE student_id = ?)", student_id[0]['student_id'])
            dates = db.execute("SELECT * FROM requests WHERE student_id = ?", student_id[0]['student_id'])

            # Add issue dates to books
            index = 0
            for book in books:
                book['issue_date'] = dates[index]['issue_date']
                book['due_date'] = dates[index]['due_date']
                index += 1

            flash("Request Successful: Please Pick It Up")
            return render_template("index1.html", books=books)

        # Return inventory
        else:
            books  = db.execute("SELECT * FROM books")
            return render_template("request1.html", books=books)

    # GET Requests
    books  = db.execute("SELECT * FROM books")
    return render_template("request1.html", books=books)

def admin():
    #Check for ID
    user = db.execute("SELECT student_id FROM users WHERE id=?", session["user_id"])

    return user[0]["student_id"]