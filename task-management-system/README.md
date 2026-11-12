# 📋 TaskFlow — Full-Stack Django Task Management System

A complete, production-ready, beginner-friendly **Task Management System** built with **Python 3**, **Django 6**, **SQLite**, and **Bootstrap 5.3**. TaskFlow features secure user authentication, strict data isolation, interactive Chart.js analytics, dynamic search & filtering, pagination, responsive navigation, and comprehensive automated test coverage.

---

## 🌟 Key Features

### 🔐 1. Authentication & Security
- **Registration & Login**: Secure user registration with email uniqueness checks and password confirmation.
- **Strict User Isolation**: Users can only see, create, update, or delete their own tasks. Direct URL access to another user's task returns a `404 Not Found`.
- **Protected Views**: All task views are protected with `@login_required` decorators, redirecting unauthenticated users to `/login/`.
- **Profile Management**: Profile page to update user personal details (first name, last name, email) and monitor productivity metrics.

### 📊 2. Interactive Analytics Dashboard
- **6 Key Metrics**: Real-time summary cards for:
  - Total Tasks
  - Pending Tasks
  - In Progress Tasks
  - Completed Tasks
  - Overdue Tasks (automatically computed based on current date)
  - Completion Rate (%) with visual progress bar
- **Interactive Visualizations (Chart.js)**:
  - **Status Distribution**: Doughnut chart showing task statuses.
  - **Priority Breakdown**: Bar chart breaking down High, Medium, and Low priorities.
- **Recent Activity Table**: Quick preview of recently created tasks.
- **Upcoming Deadlines Widget**: Countdown pill highlighting tasks due today, tomorrow, or in upcoming days.

### 📝 3. Task Management (CRUD)
- **Create Task**: Set title, description, priority (Low, Medium, High), status (Pending, In Progress, Completed), start date, and due date.
- **Form Validation**: Clean validation preventing start date from being set after due date.
- **View Task Detail**: Dedicated task detail view with full description, metadata badges, countdown pills, and action controls.
- **Edit Task**: Update any field with pre-filled inputs.
- **Delete Task**: Interactive Bootstrap modal confirmation preventing accidental deletions.
- **Quick Status Toggle**: One-click status cycling (Pending → Completed / In Progress) directly from the list view or details page.

### 🔍 4. Search, Filter & Sort
- **Text Search**: Real-time case-insensitive keyword search matching task title or description.
- **Status Filter**: Filter by Pending, In Progress, or Completed.
- **Priority Filter**: Filter by High, Medium, or Low.
- **Overdue Quick Filter**: One-click toggle switch to isolate overdue tasks.
- **Multi-criteria Sorting**: Sort by Newest First, Oldest First, Due Date (Earliest / Latest), or Priority.
- **Pagination**: Clean, responsive pagination displaying 8 tasks per page with preserved query parameters across pages.

### 🛠️ 5. Django Admin Integration
- Pre-configured `TaskAdmin` with searchable titles, usernames, emails, status/priority filters, date hierarchy by due date, and custom overdue boolean indicators.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Python 3.13 + Django 6.1 |
| **Database** | SQLite (Default relational database) |
| **Frontend UI** | HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons |
| **Data Visualization** | Chart.js 4.4 |
| **JavaScript** | Vanilla JavaScript (Sidebar toggle, alert auto-dismiss) |
| **Architecture** | Django MTV (Model - Template - View) |

---

## 📁 Project Structure

```
task-management-system/
│
├── manage.py                   # Django CLI management script
├── requirements.txt            # Python dependencies
├── db.sqlite3                  # Pre-seeded SQLite database
├── README.md                   # Complete documentation
│
├── task_manager/               # Project configuration package
│   ├── __init__.py
│   ├── settings.py             # Settings (installed apps, templates, static)
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI configuration
│   └── asgi.py                 # ASGI configuration
│
├── tasks/                      # Core application
│   ├── __init__.py
│   ├── admin.py                # Django admin configuration
│   ├── forms.py                # TaskForm, UserRegisterForm, UserUpdateForm
│   ├── models.py               # Task model with overdue logic
│   ├── tests.py                # 11 automated unit & integration tests
│   ├── urls.py                 # App URL patterns
│   ├── views.py                # Dashboard, CRUD, and auth views
│   │
│   ├── migrations/             # Database schema migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   │
│   └── management/commands/    # Custom management commands
│       ├── __init__.py
│       └── seed_data.py        # Demo data generator
│
├── templates/                  # Django HTML templates
│   ├── base.html               # Base layout with sidebar, navbar, footer
│   │
│   ├── registration/           # Authentication templates
│   │   ├── login.html          # Clean sign-in screen
│   │   └── register.html       # User registration screen
│   │
│   └── tasks/                  # Task view templates
│       ├── dashboard.html      # Metrics, Chart.js charts & deadlines
│       ├── task_list.html      # Search, filters, table & delete modal
│       ├── task_form.html      # Add & Edit task form with date pickers
│       ├── task_detail.html    # Detailed task view with metadata
│       ├── task_confirm_delete.html # Direct deletion fallback
│       └── profile.html        # User profile & productivity stats
│
└── static/                     # Static assets
    ├── css/
    │   └── style.css           # Custom styling, transitions & sidebar
    └── js/
        └── script.js           # Vanilla JS helpers
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
Ensure **Python 3.10+** and `pip` are installed on your machine.

### 2. Navigate to the Project Directory
```bash
cd C:\Users\vince\.gemini\antigravity\scratch\task-management-system
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. (Optional) Populate Sample Demo Data
A custom management command is included that sets up sample users and realistic tasks across all priorities, statuses, and overdue states:
```bash
python manage.py seed_data
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Open your browser and navigate to: **`http://127.0.0.1:8000/`**

---

## 🔑 Pre-Configured Demo Accounts

| Role | Username | Password | Email | Purpose |
|---|---|---|---|---|
| **Superuser / Admin** | `admin` | `admin123` | `admin@taskflow.dev` | Full admin console & sample tasks |
| **Regular User** | `alex` | `alex123` | `alex@taskflow.dev` | Demonstrates user isolation |

*(You can also register your own brand-new user at `/register/`)*

---

## 🧪 Automated Testing

A comprehensive test suite of **11 tests** validates user authentication, CRUD operations, user isolation, search/filtering, and model validations:

```bash
python manage.py test tasks
```

### Test Coverage Highlights:
- `test_user_registration`: Ensures account creation and password hashing.
- `test_user_login_and_logout`: Tests session establishment and redirection for unauthenticated requests.
- `test_invalid_registration`: Validates mismatched password handling.
- `test_invalid_task_dates`: Confirms validation error when `start_date > due_date`.
- `test_create_task`: Verifies task ownership assignment.
- `test_update_task`: Verifies fields persistence.
- `test_delete_task`: Verifies cascade and deletion.
- `test_user_isolation`: Proves User A receives `404` when trying to view, edit, or delete User B's task.
- `test_search_and_filter`: Tests keyword search and status/priority/overdue filters.
- `test_task_toggle_status`: Tests quick status toggle action.
- `test_overdue_property`: Tests overdue date evaluation.

---

## 🔮 Future Enhancements
- Email reminders for tasks approaching their due date.
- File and attachment uploads for tasks.
- Task tags/labels and categories.
- Export task records to CSV or PDF reports.
- Team workspace sharing and task assignment.
