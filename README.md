# ETERNUM — Sacred Memorial Sanctuary Platform

> **A Dignified Choice for Every Family. Crafted with Sacred Reverence & Integrity.**  
> Developed using **Django 5.2 (Python)**, **SQLite**, and the **Stitch Modern Gothic Memorial UI Design System**.

---

## 1. Overview & Architecture

**Eternum** is an online platform designed to simplify and dignify the process of purchasing caskets and coffins for grieving families. It addresses the lack of transparency in traditional funeral homes by offering upfront pricing, direct mortuary delivery, FTC Funeral Rule compliance, and cryptographic certificates of authenticity.

- **Backend**: Python 3.10+ / Django 5.2
- **Database**: SQLite (`db.sqlite3`), implementing the relational schema specified in [Eternum_System_Design.md](file:///c:/Users/admin/Desktop/eternum2.0/Eternum_System_Design.md)
- **UI Design System**: Stitch Modern Gothic Memorial (`DESIGN.md`), featuring chiaroscuro lighting, burnished brass accents (`#c5a880`), deep obsidian surfaces (`#131314`), `EB Garamond` display typography, and `Hanken Grotesk` interface typography.

---

## 2. Quick Start: Running Locally

The project is currently running locally on port **8000**. To run or re-launch the server:

```bash
# 1. Apply database migrations
py -3.10 manage.py migrate

# 2. Seed database with initial catalog, admin, and demo customer (already seeded)
py -3.10 manage.py seed_eternum

# 3. Start the local server
py -3.10 manage.py runserver 127.0.0.1:8000
```

Open your browser at: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 3. Demo Credentials

Quick-fill demo buttons are integrated directly into the login modal for evaluator convenience:

| Role | Email | Password | Access / Features |
|---|---|---|---|
| **Administrator** | `admin@eternum.com` | `admin123` | [Director Admin Portal](http://127.0.0.1:8000/admin-portal/) & [Django Admin](http://127.0.0.1:8000/admin/) |
| **Family / Customer** | `eleanor@example.com` | `user123` | Pre-seeded order, invoices, address, and enquiry history |

---

## 4. System Features (SRS & System Design Mapping)

### 4.1 Product Catalog & Filter Pillars (SRS 3.2, 3.3)
- Categorized into:
  1. **Solid Hardwood Sanctuary** (Oak, Mahogany, Ash)
  2. **Protective Metal Architecture** (18-Gauge Steel, Copper, Bronze)
  3. **Natural Living Return** (Willow, Bamboo, Pine — Green Burial Council Certified)
  4. **Artisanal Cathedral Craft** (Gothic lancet arch relief carvings, walnut)
- Filter by:
  - **Category**: Hardwood, Metal, Eco, Artisanal
  - **Price Scale**: $1,000–$2,500, $2,501–$4,000, $4,001+
  - **Interior Bedding**: Pearl Crepe, Ivory Velvet, Organic Cotton
  - **Exterior Finish**: Satin Honey, Midnight Bronze, Natural, Beeswax, Walnut, Patina
  - **Logistics State**: Immediate Crypt Dispatch (<24h) vs. Artisan Handcraft
  - **Live Search**: By name, wood type, or metal gauge

### 4.2 Shopping Cart & Dignified Checkout (SRS 3.4, 3.5)
- Full item management (increment, decrement, remove, clear)
- Transparent cost breakdown ($0 hidden fees, complimentary white-glove direct delivery)
- Multi-step checkout:
  - Direct Mortuary Destination (Funeral home name, director contact, receiving address, ceremony date)
  - Federal Trade Commission (FTC) Funeral Rule direct delivery affirmation (16 CFR § 453)
  - Sandbox Payment Simulator (Card / Wire transfer) with instant test credentials
  - Instant formal invoice generation (`#INV-2026-XXXX`) and order tracking number (`#ETR-XXXX`)

### 4.3 Order Management & 4-Step Chain-of-Custody Tracking (SRS 3.7)
- Step 1: Order Placed & Mortuary Notified
- Step 2: Vault Prepared & Crypt Sealed
- Step 3: White-Glove Transit Dispatched
- Step 4: Mortuary Received & Signed
- Printable Formal Invoice with complete tax & provenance details

### 4.4 Urgent Assistance Desk & Bespoke Inscription (SRS 3.6)
- 24/7 Priority Emergency Desk for delivery within 24 hours
- Bespoke monogramming, scripture verses, and family crest carving requests
- Real-time enquiry tracking (`#ENQ-XXXX`) with status tracking (`Open`, `Responded`, `Closed`)

### 4.5 Authenticity Certificate Verification (System Design UC12)
- Public verification tool at `/certificate/verify/`
- Lookup by verification code (e.g. `ETR-AUTH-0824`, `ETR-AUTH-0912`, `ETR-AUTH-1102`)
- Displays ornate digital Certificate of Provenance with QR code, artisan issuing details, and material purity guarantee

### 4.6 Central Director Admin Portal (SRS 3.8)
- Real-time KPI metrics (Revenue, Orders, Open Enquiries, Vault Inventory)
- Order status workflow management (`placed` &rarr; `confirmed` &rarr; `dispatched` &rarr; `delivered`)
- Bereavement counselor enquiry response system
- Product inventory management and active toggle
- Direct integration with Django's administrative back-office at `/admin/`

---

## 5. Verification & Automated Tests

Run the full Django test suite:

```bash
py -3.10 manage.py test memorial
```
All 8 automated test suites validate home rendering, catalog filtering, cart workflows, checkout processing, enquiry handling, certificate verification, and admin permissions.
