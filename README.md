# 🚀 Task Management System
## 📄 Description
This is a **Task Management System (TMS)** designed to help individuals and teams manage their tasks efficiently. It provides a personalized, multi-tenant interface where users can view, create, update, and track their tasks, ensuring privacy and organization for each user.
The application is hosted locally at **`http://127.0.0.1:5000/`** during development and deployed server at **`https://task-management-app-i1v3.onrender.com/`**
---
## ✨ Features
* **User Authentication:** Secure user registration, login, and logout.
* **Personalized Dashboard:** A personalized welcome screen (e.g., "Welcome Back, Krishna Verma").
* **Task Management:** Core CRUD (Create, Read, Update, Delete) functionality for tasks.
* **User Profile:** Access to user profile settings.
* **Add Task** User can add the Task here 
* **Contact Me:** A dedicated contact mechanism.
---

## 📸 Screenshots

Here's a visual walkthrough of the main user features and application states:

### 1.Landing page of the Task Management APP.

![Landing page of the Task Management APP.](/assets/1.jpg)

### 2. Sign-In to Your Account
The form for existing users to sign in.

![Sign-in form with fields for email/username and password.](/assets/2.jpg)

### 3. Personalized Dashboard (Post-Login)
The main dashboard welcoming the user after a successful login.

![Personalized dashboard after successful login, showing "Welcome Back, Krishna Verma!".](/assets/3.jpg)

### 4. Add a New Task
The interface for users to create a new task with a due date.

![Modal window for adding a new task, including "What do you need to do?" and "Due Date" fields.](/assets/4.jpg)

### 5. Modify the Task here
The interface to to create and delete the task.

![Modal window to add a task view the task and delete the task.](/assets/5.jpg)

### 6. Your Profile
Displays the current user's profile information.

![User profile view showing username, full name, email, and profile picture.](/assets/6.jpg)

### 7. Update Your Profile
Allows users to modify their profile details, including changing their profile photo and account deletion.

![Profile update form, with options to change photo, username, full name, email, and delete account.](/assets/7.jpg)

### 8. Logged Out State
The view presented to the user immediately after logging out.

![Landing page indicating "You have been logged out.".](/assets/8.jpg)

### 9. Access Denied / Forced Login
Messages displayed when an unauthenticated user tries to access a protected page, redirecting them to login.

![Login screen with "Please log in to access this page." messages.](/assets/9.jpg)

### 10. Create Your Account
The registration form for new users to create an account.

![Registration form for creating a new account with fields for username, full name, email, and password.](/assets/10.jpg)

### 11. Contact Me
If the user have any query they can contact us via filling this form and reach us the link

![Cantact us if have any query](/assets/11.jpg)

---
## 🛠️ Tech Stack
* **Backend:** Python (**Flask**  given the `127.0.0.1:5000` default port).
* **Frontend:** HTML, CSS, JavaScript.
* **Database:** PostgreSQL
---
## 💻 Installation and Setup
### Prerequisites
* Python 3.x
* `pip` (Python package installer)
### Local Setup
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/krissshnaverrrma/Task-Management-APP.git]
    cd Multi-user-Task-Management-System
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate 
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Database and Configuration:**
    * Set up your database (if necessary) and apply migrations.
    * Create a `.env` file with your configuration, including a strong `SECRET_KEY`.
5.  **Run the application:**
    ```bash
    python app.py 
    # OR: flask run (if using Flask)
    ```
---
## 🌐 Usage
Access the running application in your browser at:
**`https://task-management-app-i1v3.onrender.com/`**
---
## 🙋 Contact
For questions or feedback, please reach out to:
* **Developer:** Krishna Verma
* **GitHub:** [https://github.com/krissshnaverrrma]
<<<<<<< Updated upstream
* **Email:** [krishna1290verma@gmail.com]
=======
* **Email:** [krishna1290verma@gmail.com]
>>>>>>> Stashed changes
