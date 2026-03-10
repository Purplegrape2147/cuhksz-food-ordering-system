# CUHK(SZ) Full-Stack Food Ordering System: Client-Server Architecture

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite3-orange.svg)]()
[![Status](https://img.shields.io/badge/Status-Completed-brightgreen.svg)]()

**Author:** Annabel Leonardi | Final-Year Fintech @ CUHK-Shenzhen  
**Contact:** https://www.linkedin.com/in/annabel-leonardi/	 | annabel.leonardi@gmail.com

---

## 📌 Executive Summary
This project is a robust, full-stack ordering platform designed to handle the logistics of a campus food delivery service. Moving beyond a simple script, it implements a decoupled **Client-Server architecture** using a RESTful API. The system manages complex relational data, secure user authentication, and multi-role access control (RBAC), providing a production-grade foundation for FinTech software solutions.

---

## 🚀 Technical Highlights

* **RESTful API Backend:** Developed a high-performance server using **Flask**, handling CRUD operations for stores, menus, and real-time order tracking.
* **Security & Authentication:** Integrated industry-standard **Bcrypt** password hashing and salting to ensure secure user authentication and data privacy.
* **Relational Database Design:** Architected a normalised **SQLite3** schema with 6+ interrelated tables, utilising complex SQL `JOIN` and `GROUP BY` operations for data aggregation.
* **Role-Based Access Control (RBAC):** Engineered separate interfaces for **Users** (ordering/tracking) and **Admins** (logistics/driver management/store editing).
* **Advanced CLI Rendering:** Solved localised UI challenges by implementing custom logic with `wcwidth` to handle **CJK character widths** and emojis in a terminal environment.

---

## 📂 Repository Structure



```text
cuhksz-food-ordering-system/
│
├── client/
│   ├── main.py              # Interactive CLI Frontend & API consumption
│   └── ui.py                # Terminal UI rendering & CJK width logic
│
├── server/
│   ├── app.py               # Flask REST API & Business logic
│   └── databases/
│       └── food_ordering.db # Relational SQLite database
│
├── docs/
│   ├── schema.png           # Database E-R Diagram
│   ├── schema_2.png         # Database E-R Diagram
│   └── Project_Report.pdf   # Full technical documentation
│
├── requirements.txt         # Project dependencies (Flask, Bcrypt, Requests)
└── README.md                # Project documentation
