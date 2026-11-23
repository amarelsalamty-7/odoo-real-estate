# Odoo Real Estate Management

An Odoo 17 application for managing a real-estate portfolio: properties, owners, buildings and the
sale workflow of each property — from first listing to closing — with a full audit trail.

> Built as a hands-on project to practise the Odoo framework end to end: ORM, views, security,
> wizards, cron jobs, QWeb reports, OWL components and HTTP controllers.

## Features

- **Property catalogue** – reference (auto-generated sequence `PRT00001`), price, bedrooms, facades,
  garage/garden details, tags, owner and a per-room area breakdown.
- **Status workflow** – `Draft → Pending → Sold → Closed`, driven by header buttons and tracked in the chatter.
- **Audit history** – every state change is stored in `property.history` (who, from, to, why).
- **Re-open wizard** – a closed property can only be re-opened through a wizard that requires a reason.
- **Late-property cron** – a daily job flags open properties whose expected selling date has passed
  (they are highlighted in red in the list view).
- **Sales integration** – link a sale order or a contact to a property.
- **PDF report** – printable property sheet (QWeb) with a custom font.
- **OWL client action** – a small reactive list view (create / delete / refresh) built with OWL.
- **REST endpoints** – create, list and read properties over HTTP with input validation.
- **Security** – *Property User* and *Property Manager* groups with separate access rights.
- **Automated tests** – workflow, history, constraints, cron and wizard.

## Tech stack

Python 3.10+ · Odoo 17 (Community) · PostgreSQL · XML views · QWeb · OWL (JavaScript)

## Installation

```bash
git clone https://github.com/amarelsalamty-7/odoo-real-estate.git)
# add the cloned folder to your Odoo addons path, then:
./odoo-bin -d mydb -i real_estate --addons-path=addons,/path/to/odoo-real-estate
```

Dependencies: `base`, `mail`, `sale`. Demo data (owners, tags, two properties) is loaded when the
database is created with demo data enabled.

## Running the tests

```bash
./odoo-bin -d test_db -i real_estate --test-enable --test-tags /real_estate \
    --stop-after-init --addons-path=addons,/path/to/odoo-real-estate
```

## REST API

The endpoints use the Odoo session (`auth="user"`), so authenticate first:

```bash
# 1) log in and keep the session cookie
curl -c cookies.txt -H "Content-Type: application/json" \
  -d '{"params": {"db": "mydb", "login": "admin", "password": "admin"}}' \
  http://localhost:8069/web/session/authenticate

# 2) create a property
curl -b cookies.txt -H "Content-Type: application/json" \
  -d '{"name": "Villa 7", "postcode": "35511", "bedrooms": 4, "expected_price": 2500000}' \
  http://localhost:8069/v1/property

# 3) list / read
curl -b cookies.txt http://localhost:8069/v1/property
curl -b cookies.txt http://localhost:8069/v1/property/1
```

| Method | Route                  | Description                         |
|--------|------------------------|-------------------------------------|
| POST   | `/v1/property`         | Create a property (whitelisted fields, returns `201`) |
| GET    | `/v1/property`         | List the first 100 properties       |
| GET    | `/v1/property/<id>`    | Read one property (`404` if missing)|

## Project structure

```
real_estate/
├── __manifest__.py
├── controllers/     # REST endpoints
├── data/            # sequence + cron
├── demo/            # demo records
├── models/          # property, owner, tag, building, history, sale/partner extensions
├── reports/         # QWeb PDF report
├── security/        # groups + access rights
├── static/          # OWL component, CSS, font
├── tests/           # automated tests
├── views/           # list / form / search views and menus
└── wizard/          # re-open (change state) wizard
```

## Roadmap

- Automatically mark a property as *Sold* when its sale order is confirmed
- Monetary fields with currency support
- Link properties to buildings
- Kanban and pivot views, dashboard
- Website listing page

## Credits

Report font: *Winky Rough* (Google Fonts, SIL Open Font License).

## Author

**Ammar Elsalamty**

## License

LGPL-3
