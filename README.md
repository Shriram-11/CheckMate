# CheckMate

CheckMate is an Event Management System designed to streamline the process of organizing and managing events. This application provides functionalities for event registration, user management, and more.

## Features

- Event Registration
- User Authentication and Authorization
- Admin Interface for Managing Events
- Database Integration

## Project Structure

EventManagement/ │ ├── db.sqlite3
│ ├── entrysystem/
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── migrations/
│ │ └── init.py
│ ├── models.py
│ ├── serializers.py
│ ├── tests.py
│ ├── urls.py
│ └── views.py
│ ├── EventManagement/
│ ├── init.py
│ ├── asgi.py
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│ ├── manage.py
├── README.md
└── requirements.txt

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/Shriram-11/CheckMate.git
   cd CheckMate
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Apply migrations to set up the database:

   ```sh
   python manage.py migrate
   ```

5. Run the development server:
   ```sh
   python manage.py runserver
   ```

## Usage

- Access the application at `http://127.0.0.1:8000/`.
- Use the admin interface at `http://127.0.0.1:8000/admin/` to manage events and users.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
