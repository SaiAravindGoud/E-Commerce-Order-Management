\# E-Commerce Order Management API



Backend REST API for an E-Commerce Order Management System built with FastAPI, SQLAlchemy, MySQL and Alembic.



\## Technology Stack



\- Python 3.9+

\- FastAPI

\- Pydantic

\- SQLAlchemy

\- MySQL

\- Alembic

\- JWT Authentication

\- Passlib / bcrypt

\- BackgroundTasks

\- SMTP / Gmail

\- Uvicorn



\## Features



\- Customer registration and login

\- JWT authentication

\- Customer and Admin roles

\- Category CRUD

\- Product CRUD

\- Product search, filtering, sorting and pagination

\- Shopping cart management

\- Address management

\- Order placement and cancellation

\- Order status management

\- GST calculation

\- Delivery charge calculation

\- Mock payments

\- Returns and refunds

\- Product reviews and ratings

\- Email notifications using BackgroundTasks and SMTP

\- Admin sales and order reports

\- Low-stock and top-product reports

\- Validation and error handling



\## Project Structure



```text

E-Commerce-Order-Management/

├── app/

│   ├── auth/

│   ├── models/

│   ├── routers/

│   ├── schemas/

│   ├── services/

│   ├── utils/

│   ├── database.py

│   └── main.py

├── alembic/

│   └── versions/

├── .env

├── .env.example

├── .gitignore

├── alembic.ini

├── README.md

└── requirements.txt

```



\## Environment Configuration



Create a `.env` file in the project root.



Example:



```text

DATABASE\_URL=mysql+pymysql://username:password@localhost/ecommerce\_db



JWT\_SECRET\_KEY=your-secret-key

JWT\_ALGORITHM=HS256

ACCESS\_TOKEN\_EXPIRE\_MINUTES=30



SMTP\_HOST=smtp.gmail.com

SMTP\_PORT=587

SMTP\_USERNAME=your-email@gmail.com

SMTP\_PASSWORD=your-gmail-app-password

SMTP\_FROM=your-email@gmail.com

```



Do not commit `.env` or real credentials to GitHub.



Use `.env.example` as the configuration template.



\## Database Setup



Create the MySQL database:



```sql

CREATE DATABASE ecommerce\_db;

```



Configure the connection in `.env`.



\## Installation



Create the virtual environment:



```powershell

python -m venv venv

```



Activate it:



```powershell

.\\venv\\Scripts\\Activate.ps1

```



If PowerShell blocks activation:



```powershell

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

```



Then activate:



```powershell

.\\venv\\Scripts\\Activate.ps1

```



Install dependencies:



```powershell

pip install -r requirements.txt

```



\## Database Migrations



Apply migrations:



```powershell

alembic upgrade head

```



Check the current migration:



```powershell

alembic current

```



View migration history:



```powershell

alembic history

```



The project uses Alembic migrations and does not use `Base.metadata.create\_all()`.



\## Run the Application



Start the server:



```powershell

python -m uvicorn app.main:app --reload

```



API:



```text

http://127.0.0.1:8000

```



Swagger documentation:



```text

http://127.0.0.1:8000/docs

```



\## Authentication



Register:



```text

POST /auth/register

```



Login:



```text

POST /auth/login

```



After login, use the JWT access token through Swagger's Authorize button.



\## Test Users



The local test database contains:



```text

Customer:

Username: customer1

Role: Customer



Admin:

Username: admin

Role: Admin

```



Passwords should remain private and must not be committed to GitHub.



\## Main API Modules



\### Authentication



\- Register

\- Login

\- Current user

\- JWT authentication

\- Role-based authorization



\### Categories



\- Create

\- List

\- Update

\- Delete



\### Products



\- Create

\- List

\- Search

\- Filter

\- Sort

\- Pagination

\- Update

\- Soft delete



\### Cart



\- View cart

\- Add item

\- Update quantity

\- Remove item

\- Clear cart



\### Addresses



\- Create address

\- List addresses

\- Update address

\- Delete address

\- Set default address



\### Orders



\- Create order

\- View own orders

\- View order details

\- Cancel order

\- Admin status updates



Order calculations:



\- GST: 18%

\- Delivery charge: ₹50 when subtotal is ₹500 or less

\- Free delivery when subtotal is above ₹500



\### Payments



Supported methods:



\- UPI

\- Card

\- Net Banking

\- COD



Payments use unique transaction IDs and mock payment processing.



\### Returns \& Refunds



\- Create return request

\- View returns

\- Admin approve

\- Admin reject

\- Refund processing

\- Stock restoration



Returns are allowed only for delivered orders within seven days.



\### Reviews



\- Create product review

\- View reviews

\- Update own review

\- Delete own review

\- Average rating

\- Review count



\### Email Notifications



Email notifications use FastAPI BackgroundTasks and SMTP.



Notifications include:



1\. Registration

2\. Order placed

3\. Payment success

4\. Order shipped

5\. Order delivered

6\. Order cancelled

7\. Return approved/refund processed

8\. Return rejected



SMTP credentials are stored only in `.env`.



\### Admin Reports



Admin-only endpoints:



```text

GET /reports/sales

GET /reports/orders-by-status

GET /reports/top-products

GET /reports/low-stock

```



\## Validation \& Error Handling



The API validates:



\- Required fields

\- Positive prices

\- Non-negative stock

\- Ten-digit phone numbers

\- Six-digit pincodes

\- Unique email addresses

\- Unique SKUs

\- Unique category names

\- Unique order numbers

\- Unique transaction IDs



Common HTTP responses:



\- 200 OK

\- 201 Created

\- 400 Bad Request

\- 401 Unauthorized

\- 403 Forbidden

\- 404 Not Found

\- 409 Conflict

\- 422 Unprocessable Entity



\## Assumptions



\- GST is 18%.

\- Delivery is ₹50 for subtotal ₹500 or less.

\- Delivery is free above ₹500.

\- Returns are allowed within seven days of delivery.

\- Approved returns restore stock.

\- Approved returns refund the order grand total.

\- Payments are simulated and do not connect to a real payment gateway.

\- Customers can access only their own carts, addresses, orders and returns.

\- Reports are restricted to Admin users.



\## Alembic Migrations



Current migration history:



```text

bb9e9bcf74ba - Create initial ecommerce tables

6b4893a3266e - Create order tables

```



Current database migration:



```text

6b4893a3266e (head)

```



\## Assignment Completion



The required assignment levels are completed:



\- Level 1 - Project Setup, Database \& Migrations

\- Level 2 - Authentication \& Authorization

\- Level 3 - Category \& Product Management

\- Level 4 - Search, Filtering, Sorting \& Pagination

\- Level 5 - Cart Management

\- Level 6 - Address Management

\- Level 7 - Order Management

\- Level 8 - Payment Management

\- Level 9 - Returns \& Refunds

\- Level 10 - Reviews

\- Level 11 - Email Notifications

\- Level 12 - Validation \& Error Handling

\- Level 13 - Admin Reports



\## Submission Checklist



\- `.env` excluded from Git

\- `.env.example` included

\- `.gitignore` included

\- `README.md` included

\- Alembic migrations included

\- Swagger screenshots

\- Email screenshots

\- GitHub repository

\- Setup and testing instructions



\## Project Status



The E-Commerce Order Management API is ready for final submission.

