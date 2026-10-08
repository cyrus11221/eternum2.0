# Software Requirements Specification (SRS) — ETERNUM

## 1. Introduction

Eternum is an online platform designed to simplify and dignify the process of purchasing caskets and coffins for grieving families. Traditionally, this process is handled through funeral homes with limited options, unclear pricing, and added stress during an already difficult time. Eternum addresses this gap by offering a transparent, accessible, and compassionate digital space where users can browse a variety of casket options — ranging from budget-friendly to premium and eco-friendly choices — view detailed product information, and place orders conveniently online.

### 1.1 Purpose

The purpose of this Software Requirement Specification document is to define the functional and non-functional requirements of the web application "Eternum". The application's goal is to give users an easy-to-use online platform for browsing, comparing, and purchasing caskets and coffins in a transparent and respectful manner.

### 1.2 Document Conventions

Not applicable.

### 1.3 Intended Audience and Reading Suggestions

- **Developers:** Should read the entire document, focusing especially on Section 3 (System Features) and Section 4 (External Interface Requirements) to understand functional and technical requirements.
- **Project Guide/Evaluator:** May focus on Section 1 (Introduction) and Section 2 (Overall Description) to assess the project's scope and feasibility.
- **Designers (UI/UX):** Should refer to Section 4 (External Interface Requirements) for interface and design-related requirements.
- **Testers:** Should focus on Section 3 (System Features) and Section 5 (Non-Functional Requirements) to design relevant test cases.
- **End Users (Customers/Funeral Homes):** May refer to Section 2 (Overall Description) to understand the product's purpose and usage.
- **Project Team Members:** Should read the complete document to maintain a shared understanding of the requirements throughout development.

### 1.4 Project Scope

Eternum is a web-based platform designed to enable users to browse, compare, and purchase caskets/coffins online in a transparent and respectful manner. The system provides a product catalog categorized into wooden, metal, eco-friendly/biodegradable, and premium/custom caskets, along with detailed product information such as material, dimensions, finish, and price. It includes a shopping cart and checkout module for placing orders, an enquiry/contact form for custom or urgent requirements, and supporting sections such as About Us, FAQs, and testimonials to build user trust during a sensitive purchase process. Admin functionality is included to manage product listings and orders.

The scope of this project is limited to the front-end and back-end development of the website and does not extend to actual logistics, delivery, or coordination with funeral homes, which is assumed to be handled outside the system. Payment gateway integration, if included, is limited to a demo/test environment. Overall, the system is developed for educational and demonstration purposes as part of a mini project, with potential to be scaled for real-world deployment in the future.

### 1.5 References

*(None listed.)*

---

## 2. Overall Description

Eternum is an online platform that offers consumers a transparent and respectful way to buy caskets and coffins. By providing a user-friendly interface, smooth product browsing, a dedicated enquiry system, and effective order management, the system seeks to bring ease, trust, and dignity into a traditionally difficult purchasing experience.

### 2.1 Product Perspective

Eternum is a new, independent, self-contained web-based system developed as part of a mini project. It is not a modification or extension of any existing product, but a standalone platform built to address the lack of transparency and convenience in the traditional casket-buying process. While similar to general e-commerce platforms in its basic structure (product catalog, cart, checkout), Eternum is tailored specifically to the sensitive and specialized nature of the funeral products industry, incorporating a calm, respectful user interface and a dedicated enquiry system for custom/urgent orders.

The system is designed as a client-server web application comprising a front-end (browsing, ordering, enquiries), a back-end (business logic, product data, order processing, admin operations), and a database (products, users, orders, enquiries). For the scope of this mini project, it functions as a self-contained unit without external system dependencies beyond standard web hosting and database services.

### 2.2 Product Functions

- User registration and secure login
- Product catalog categorized by type (wooden, metal, eco-friendly, premium/custom)
- Detailed product pages (material, dimensions, finish, price)
- Product search and filter (by category, price range)
- Shopping cart management
- Secure checkout process
- Enquiry and custom order form for urgent/special requirements
- Order confirmation, tracking, and order history
- Admin panel for managing products, orders, and enquiries
- About Us, FAQs, and Testimonials sections
- Contact Us section for general queries
- Responsive design across desktops, tablets, and mobile devices

### 2.3 User Classes and Characteristics

- **User:** Individuals visiting the website to browse, compare, and purchase caskets, either for immediate need or pre-planning. Users are expected to have basic computer literacy. They can register/log in to place orders, track order status, view order history, and submit enquiries for custom or urgent requirements. The system offers a simple, intuitive, and respectful interface requiring minimal technical effort.
- **Admin:** Responsible for managing backend operations, including adding/updating/removing product listings, managing and processing orders, responding to user enquiries, and maintaining website content (FAQ, testimonials). Requires higher technical proficiency and elevated access privileges.

### 2.4 Operating Environment

**Client Side**
- Operating System: Windows, Linux, macOS
- Web Browser: Chrome, Firefox, Microsoft Edge, Safari
- Internet connection required

**Server Side**
- Web server capable of handling HTTP/HTTPS requests, running the chosen backend technology (e.g., Node.js, PHP)
- Database: MySQL, MongoDB, or Firebase
- Operating System: Platform-independent client; Windows/Linux server
- Network: Stable internet connection required for users and administrators

### 2.5 Design and Implementation Constraints

- Limited academic timeframe restricts the range of features that can be realistically implemented, requiring prioritization of core functionality
- Built using readily available, well-documented, academic-suitable technologies (HTML, CSS, JavaScript, chosen backend framework, and database)
- Developed individually by a single person, limiting overall scope, complexity, and extent of testing
- Only free or open-source tools, frameworks, and hosting services are used; no licensed/paid third-party services
- Payment functionality, if implemented, is restricted to a demo/sandbox environment rather than a live payment gateway
- Basic security practices (input validation, secure login) are included; advanced measures such as formal penetration testing are out of scope
- Design, language, and imagery must remain respectful, non-commercial in tone, and appropriate for a grieving audience
- Primarily designed for modern, updated browsers; full compatibility with legacy browsers is not guaranteed
- Built to handle a limited number of concurrent users and transactions, not optimized for large-scale deployment

### 2.6 User Documentation

- **User manual:** Explains how users can register, browse products, place orders, track order status, and submit enquiries.
- **FAQ section:** In-built and integrated within the website, addressing common queries related to ordering, delivery, and customization.
- **Admin guide:** Outlines how the administrator can manage product listings, process orders, respond to enquiries, and maintain content through the admin panel.
- **In-interface aids:** Tooltips and on-screen instructions (form hints, confirmation messages) guide users through key actions like checkout and enquiry submission.
- **Technical documentation:** This SRS document, along with UML diagrams, ER diagrams, and system architecture diagrams, for academic evaluation and future reference.

### 2.7 Assumptions

- Users have access to a stable internet connection
- The server remains operational and accessible
- The database functions without interruption
- Real-world delivery/logistics coordination is handled outside the system
- Users possess basic knowledge of web browsing and online shopping

---

## 3. System Features

| # | Feature | Description |
|---|---------|-------------|
| 3.1 | User Registration & Login | Allow users to create an account, log in securely, recover forgotten passwords, and manage their profiles. |
| 3.2 | Product Search and Filter | Allow users to search products by name and filter them based on category and price. |
| 3.3 | Product Catalog | Allow users to browse wooden, metal, eco-friendly, and premium/custom caskets organized into categories with detailed descriptions and images. |
| 3.4 | Shopping Cart | Users can add products to their shopping cart, update quantities, and remove items as required. |
| 3.5 | Checkout | Provide a secure checkout process with order confirmation, limited to demo/sandbox payment handling for this project scope. |
| 3.6 | Enquiry & Custom Order Form | Enable users with specific or urgent requirements to submit enquiries and communicate directly with the platform. |
| 3.7 | Order Management | Enable users to view order history and track order status. |
| 3.8 | Admin Management | Allow administrators to manage product listings, orders, and customer enquiries through a centralized admin panel. |
| 3.9 | Trust & Support Sections | About Us, FAQs, Testimonials, and Contact Us sections to build user trust and clarity during a sensitive purchase. |

---

## 4. External Interface Requirements

### 4.1 User Interface
The application provides a responsive and respectful, user-friendly interface accessible through web browsers on desktops, laptops, tablets, and smartphones.

### 4.2 Software Interface
The application is developed using a chosen backend framework (e.g., Node.js/PHP), a database (MySQL/MongoDB/Firebase), and HTML, CSS, and JavaScript for the frontend.

### 4.3 Hardware Interface
The system requires a client device such as a desktop, laptop, tablet, or smartphone with an internet connection. On the server side, it requires a computer capable of hosting the backend application and database.

### 4.4 Communication Interface
The system communicates over the HTTPS protocol to ensure secure data transmission. It uses the internet for user access and (demo) payment processing.

---

## 5. Other Non-Functional Requirements

### 5.1 Performance Requirements
The system should provide fast response times and ensure efficient processing of product and order data within the limited scale expected of an academic project.

### 5.2 Safety Requirements
The system should prevent loss of data through regular backups and maintain data integrity during transactions.

### 5.3 Security Requirements
The system should prevent unauthorized access, enable encrypted password storage, HTTPS communication, and basic protection against common web security threats.

### 5.4 Software Quality Attributes
The application should be user-friendly, reliable, maintainable, and respectful in tone, given its sensitive subject matter.

---

## 6. Other Requirements

- The system should be developed in such a way that future enhancements (e.g., real payment gateway integration, delivery/logistics APIs, funeral home management integration) can be supported
- Regular backups should be maintained for data safety
- The system should follow standard web development and basic security practices
- The application should allow easy maintenance and future scalability beyond its current academic scope

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| Admin | User who manages the application |
| Cart | Temporary storage for selected products |
| Checkout | Process of confirming and placing an order |
| Enquiry | A custom or urgent request submitted by a user outside the standard catalog/checkout flow |
| Customer/User | Registered user of the system |
| HTTPS | Secure communication protocol |
| Database | Stores application data |
