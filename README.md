# Airport API

**Airport API** — is a RESTful API designed to manage data related to airports, flights, airplanes, and crew. It provides an easy way to interact with information about airports, schedule flights, register airplanes, and manage crew details.


## Опис проекту

**Airport API** provides an easy way to integrate flight information into your applications. Using the API, you can:
- Manage airports (add, update, view, and delete airport information).
- Schedule flights (create new flights, update their parameters, and view existing ones).
- Manage airplanes (add new airplanes, update maintenance records, and more).
- Monitor crew members (add crew members, their certifications, and schedule shifts).

## Technologies Used:

- **Django** — The web framework for rapid API development.
- **Django REST Framework** —  A powerful toolkit for building RESTful APIs.
- **PostgreSQL** — A relational database for storing flight, airplane, and crew information.
- **Docker** — Containerization for easy deployment and scalability.
- **JWT** — JSON Web Tokens for user authentication.

## Installation and Setup:

   ```bash
   git clone https://github.com/OLENA-KALITSINSKA/airport-api-service.git
   cd airport-api
   python -m venv venv
   venv\Scripts\activate (on Windows)
   
   source venv/bin/activate (on macOS)
   
   pip install -r requirements.txt
  
   python manage.py migrate
   python manage.py runserver
   ```
# API Documentation

This project provides an API to manage airlines, flights, airplanes, and other aviation-related data.

## Authentication

The API uses authentication to secure resources and provide access only to authorized users.

### Authentication Methods:

- **JWT (JSON Web Token)**: The API uses JWT for user authentication. Users must obtain a token upon login and include it in the `Authorization` header with each request.

#### 1. Get JWT Token:

- **POST /api/user/token/**: Obtain a token by providing login credentials.

## API Resources

### 1. **Airports**
   - **GET /api/airport/airports/**: Retrieve a list of all airports.
   - **POST /api/airport/airports/**:  Create a new airport (admin only).

### 2. **Ticket Classes**
   - **GET /api/airport/ticket_classes/**: Retrieve all ticket classes.
   - **POST /api/airport/ticket_classes/**: Add a new ticket class (admin only).

### 3. **Routes**
   - **GET /api/airport/routes/**: Retrieve all routes.
   - **POST /api/airport/routes/**: Create a new route (admin only).

### 4. **Airplane Types**
   - **GET /api/airport/airplane_types/**: Retrieve all airplane types.
   - **POST /api/airport/airplane_types/**: Add a new airplane type (admin only).
   - **GET /api/airport/airplane_types/{id}/**: Retrieve details of a specific airplane type.
   - **PUT /api/airport/airplane_types/{id}/**: Update airplane type details.
   - **DELETE /api/airport/airplane_types/{id}/**: Delete an airplane type.

### 5. **Airlines**
   - **GET /api/airport/airlines/**: Retrieve all airlines.
   - **POST /api/airport/airlines/**: Add a new airline (admin only).
   - **GET /api/airport/airlines/{id}/**: Retrieve details of a specific airline.
   - **PUT /api/airport/airlines/{id}/**: Update airline details.
   - **DELETE /api/airport/airlines/{id}/**: Delete an airline.
   - **POST /api/airport/airlines/{id}/upload-image/**: Upload an image for the airline (admin only).

### 6. **Airplanes**
   - **GET /api/airport/airplanes/**: Retrieve all airplanes with filtering by name or type.
   - **POST /api/airport/airplanes/**: Add a new airplane (admin only).
   - **GET /api/airport/airplanes/{id}/**: Retrieve details of a specific airplane.
   - **PUT /api/airport/airplanes/{id}/**: Update airplane details.
   - **DELETE /api/airport/airplanes/{id}/**: Delete an airplane.

### 7. **Crew**
   - **GET /api/airport/crews/**: Retrieve a list of all crew members.
   - **POST /api/airport/crews/**: Add a new crew member (admin only).

### 8. **Flights**
   - **GET /api/airport/flights/**: Retrieve all flights with filtering by departure date, airplane, or route.
   - **POST /api/airport/flights/**: Add a new flight (admin only).
   - **GET /api/airport/flights/{id}/**: Retrieve details of a specific flight.
   - **PUT /api/airport/flights/{id}/**: Update flight details.
   - **DELETE /api/airport/flights/{id}/**: Delete a flight.

### 9. **Orders**
   - **GET /api/airport/orders/**: Retrieve the list of a user's orders.
   - **POST /api/airport/orders/**: Create a new order for a user.
