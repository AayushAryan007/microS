# microS

## Overview

**microS** is a simple microservices-based demo project using Django and RabbitMQ to demonstrate event-driven communication between services.  
It consists of two main services:

- **Order Service**: Handles order creation and publishes order events.
- **Inventory Service**: Manages inventory, updates stock on order events, and publishes inventory updates.

Both services communicate asynchronously using RabbitMQ as the message broker.

---

## Tech Stack

- **Python 3.11+**
- **Django 5.x**
- **RabbitMQ** (via Docker)
- **pika** (Python RabbitMQ client)
- **SQLite** (default, can be swapped for any Django-supported DB)
- **Docker** (for RabbitMQ)
- **HTML/CSS/JS** (for templates)

---

## Features

- **Order Service**

  - Create orders via a web form.
  - Publishes `order.created` events to RabbitMQ.
  - Consumes inventory update events to keep a local copy of the inventory table in sync.
  - Displays the current inventory table below the order form.

- **Inventory Service**
  - CRUD operations for inventory items (products) via a web UI.
  - Consumes `order.created` events to update stock.
  - Publishes `inventory.updated` events (on add, update, delete, or stock change).
  - "Refresh Order Page" button to force-sync the inventory table in the order service.

## User Service

The **user_service** is responsible for managing user accounts and authentication within the microservices architecture. It provides endpoints for user registration, login, and profile management. The service uses Django and stores user data in a SQLite database. Authentication is handled using JWT tokens, ensuring secure access to protected resources across the system.

**Main features:**

- User registration and login
- JWT-based authentication
- User profile management
- Integration with other services for authorization

**Directory:** `user_service/`

**Key files:**

- `user_core/models.py`: User model definitions
- `user_core/views.py`: User-related views and endpoints
- `user_core/urls.py`: URL routing for user endpoints
- `user_core/templates/`: HTML templates for user pages

---

## Architecture

```
[Order Service] <---> [RabbitMQ] <---> [Inventory Service]
      ^                                         |
      |                                         v
      +----------<-- inventory.updated ---------+
```

- **Order Service** is both a producer (order events) and a consumer (inventory updates).
- **Inventory Service** is both a consumer (order events) and a producer (inventory updates).

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/AayushAryan007/microS.git
cd microS
```

### 2. Start RabbitMQ (via Docker)

```bash
docker run -d --name rabbitmq --restart unless-stopped -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

- Management UI: [http://localhost:15672](http://localhost:15672) (user: `guest`, pass: `guest`)

### 3. Set Up Python Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in both `order_service` and `inventory_service` directories with:

```
RABBITMQ_URL=amqp://guest:guest@127.0.0.1:5672/%2F
```

### 5. Apply Migrations

```bash
# Inventory Service
cd inventory_service
python manage.py makemigrations
python manage.py migrate

# Order Service
cd ../order_service
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the Services

**Inventory Service:**

```bash
cd inventory_service
python manage.py runserver 8000
python manage.py consume_orders
```

**Order Service:**

```bash
cd order_service
python manage.py runserver 8001
python manage.py consume_inventory
```

### 7. Using the App

- **Inventory UI:** [http://localhost:8000/](http://localhost:8000/)

  - Add, edit, delete products.
  - Use the "Copy" button to copy product UUIDs.
  - Use "Refresh Order Page" to force-sync inventory to the order service.

- **Order UI:** [http://localhost:8001/](http://localhost:8001/)
  - Create orders by entering a product UUID and quantity.
  - See the current inventory table below the order form (auto-updated via events).

---

## Notes

- **RabbitMQ** must be running for services to communicate.
- Both services must have the correct `RABBITMQ_URL` in their `.env`.
- The inventory table in the order service is kept in sync via RabbitMQ events.
- If you add, update, or delete inventory, the change is reflected in the order service's inventory table (either automatically or via "Refresh Order Page").

---

## License

MIT

---

## Author

[AayushAryan007](https://github.com/AayushAryan007)
