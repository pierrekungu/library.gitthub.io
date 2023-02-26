# LIBRARY MANAGEMENT SYSTEM
#### Video Demo:  <https://youtu.be/jQGzqNOPJuM>
#### Description:
The project is a library management system that manages most library functions. The system automates most processes, including student book requests, maintaining the book database, and student messages. Also, the management system allows for administrator and student privileges.
The sign-up form provides admin and student options, where the student ID is necessary for student registration. A student database confirms learners are registered at the university. The system allows for unique usernames; as such, the system automatically recognizes the admin and student during sign-in. A user session remembers the user login and ensures access until the user sign-outs.

# Sign-up
The library system provides both administrator and student privileges. During account creation, the system only allows for unique usernames. As such, it will automatically recognize an admin and a user. Moreover, for students, the system checks for the student ID to ensure all students are within the students' database.
Once the system checks for a unique username and student ID, a password hash generator encrypts the password and stores it in the users database.

# Sign-in
During sign-in, the system check for the username and the password. The user is allowed into the system when the username and password match. The users database provided a column to differentiate admins and students. A user session is started, and cookies are stored within the machine. Upon sign-out, cookies are cleared.
The system redirects students to their homepage when they try to access privileged administrator links.

# Administrator Functions
Homepage: The admin homepage lists all books issued and their due dates. The admin can access student details. A search bar allows searching specific students using their IDs.
Student requests: The admin views book return requests and student messages here. Ideally, a student issues a book return request, and the admin accepts the request when the book is physically presented at the library.
Inventory: It shows library book records and their current stock. The search bar allows finding books via the title.
Update books: This directory allows the admin to add a new book to the system. Moreover, the admin can update boom details such as title, author, publisher, and stock.

# Student Functions
Homepage. The system lists all books issued, issue dates, and return dates. The student can initiate a return request and be prompted to return the book to the library.
Book request. The student can request books; if available, the system automatically assigns the book. The system allows for ten books and only one specific book per student. On request, the books database automatically tracks all stock changes.
Return status. The system provides the student with the status of returned books. When the admin confirms the return request, the book disappears from this page and the book stock updates to reflect this process.
Messages: Allows the student to craft messages to the admin.

# Databases
The library management system uses a library database to keep track of everything in the system. Several databases include:
1. Users
2. Books
3. Students
4. Returns
5. Requests
6. Messages

## Users
This database stores the username, hash password, and student ID. For administrators, the table stores the word 'admin' in the student ID column. Users database stores all system user's credentials.
## Books
This database provides an inventory of all books within the library. Each book comes with a unique ID.
## Students
Here, all student details are stored. Important information such as student ID, names, and email is stored. Ideally, this database allows the system only to accept students within the institution.
## Returns
The database allows tracking of all student book return requests. When a student submits a return request, the database stores it, and only when the administrator confirms the request does the system delete it from this database.
## Requests
When a student requests a book, the database stores the student ID, book ID, issue date, and due date. The system provides two weeks before the book should be returned.
## Messages
All student messages are stored in this database. It stores the student ID with the message to identify each learner uniquely.

# Summary
This library management system streamlines the library process. The common function of the system includes managing the library database, providing data on the current stock, and instant book issue to students.

