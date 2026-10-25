# ETERNUM — Memorial Commerce and Care Platform

Eternum is a Django web application for browsing, comparing, and ordering memorial caskets and burial products in a respectful and transparent way. The project was designed around the requirements documented in [Eternum_SRS.md](Eternum_SRS.md) and [Eternum_System_Design.md](Eternum_System_Design.md), and it combines a modern storefront, cart workflow, checkout flow, order tracking, public certificate lookup, and a director/admin dashboard.

Built with Python, Django 5.2, SQLite by default, and a custom modern-gothic storefront design inspired by the included Stitch UI assets.

## Project overview

This repository contains a complete Django app named `memorial` plus the project configuration in `eternum_project/`.

Key functionality currently in the codebase:

- Product catalog with category, search, and price filtering
- Product detail pages with material, finish, dimensions, provenance, and stock data
- Shopping cart for guest and authenticated users
- Checkout flow with shipping details and payment method selection
- Order creation, confirmation, and order history
- Urgent enquiry form for time-sensitive memorial needs
- Public certificate verification by provenance code
- Admin dashboard for operational oversight
- Responsive themed frontend in the `memorial/templates/` and `memorial/static/` folders

## Tech stack

- Python 3.10+
- Django 5.2
- SQLite (default config in `.env.example`)
- Django admin and custom application logic

## Repository structure

- `eternum_project/` — Django project settings and root URL configuration
- `memorial/` — app logic, models, views, forms, templates, static assets, tests, seed command
- `stitch_modern_gothic_ui_design/` — design references and presentation assets
- `Eternum_SRS.md` — software requirements specification
- `Eternum_System_Design.md` — system design and architecture notes
- `.env.example` — sample environment variables
- `manage.py` — Django project entry point

## Prerequisites

Before running the project, make sure you have:

- Python 3.10 or newer
- A virtual environment (recommended)
- No external database server required for the default SQLite setup

## Local setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install the project dependencies.

Install the project dependencies:

```bash
python -m pip install django python-dotenv Pillow
```

4. Copy the example environment file and update it for your local setup:

```bash
copy .env.example .env
```

Example values:

```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
SECRET_KEY=your-secret-key
DEBUG=True
```

If you later want to use another database backend, you can override the defaults with your own environment values.

5. Apply migrations:

```bash
python manage.py migrate
```

6. Seed demo content, users, categories, products, and certificate data:

```bash
python manage.py seed_eternum
```

7. Start the local development server:

```bash
python manage.py runserver 127.0.0.1:8000
```

Then open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/admin/
- http://127.0.0.1:8000/admin-portal/

## Demo accounts

The app includes a seeded admin user and buyer account for testing:

| Role | Email | Password |
|---|---|---|
| Administrator | `admin@eternum.com` | `admin123` |
| Buyer / Customer | `eleanor@example.com` | `user123` |

## Main user flows

### Customer flows

- Browse home page and catalog
- Filter by category, search term, price range, fabric, finish, or dispatch type
- View individual product details and provenance data
- Add products to cart
- Check out with shipping and payment details
- Review order confirmation and order history
- Submit urgent enquiry or custom memorial request
- Verify product authenticity through the certificate lookup page

### Admin flows

- Manage products and categories through Django admin or custom dashboard
- Add product images by uploading JPEG, PNG, or WEBP files (maximum 5 MB) or by providing an image URL
- Review incoming orders and order states
- Monitor enquiry history and responses
- Use the director dashboard for operational summaries and workflow management

## Tests

The project includes Django tests covering the main flows, including home page rendering, catalog filtering, cart operations, checkout, enquiry submission, certificate verification, and admin portal access.

Run the test suite with:

```bash
python manage.py test memorial
```

You can also run a Django configuration check:

```bash
python manage.py check
```

## Design and requirements documents

This project includes design and specification documentation that describes the business and UX goals:

- [Eternum_SRS.md](Eternum_SRS.md)
- [Eternum_System_Design.md](Eternum_System_Design.md)
- [stitch_modern_gothic_ui_design/DESIGN.md](stitch_modern_gothic_ui_design/DESIGN.md)

## Notes

- The project is designed as a respectful memorial commerce demo and is best suited for educational or demonstration use.
- Payment flows are implemented as a sandbox-style workflow rather than a production payment provider.
- The default configuration for this repository is SQLite for simple local development and easy setup.
- Uploaded product images are stored under `media/products/` and served by Django during development; production deployments should configure the web server or object storage to serve uploaded media.
- The project is intended to be a solid foundation for further extension, real-world compliance review, and production hardening.
