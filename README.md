# Levo Schema Management API

This project implements a simplified backend API for uploading, validating, versioning, and retrieving OpenAPI schemas (JSON/YAML).  
It mimics the SaaS platform used by the **Levo CLI**.

---

## Features

- Upload API schemas either JSON or YAML
- Validate JSON/YAML OpenAPI specs before saving
- Deduplicate schemas using SHA256 checksum
- Auto-versioning of schemas per application/service
- Retrieve:
  - Latest schema
  - Specific version
  - All versions for an application/service
- Store schema files on filesystem
- REST API built with **Django + DRF**

---

## 🛠 Tech Stack

- **Backend:** Django + Django REST Framework
- **Database:** SQLite (default, can be swapped)
- **Storage:** Django file storage (local FS)

---

## 📦 Installation

### 1. Clone Repo & Setup Environment
```bash
git clone https://github.com/sairamyadhav/levoSaas.git
cd levo-assessment

python -m venv venv
source venv/bin/activate  # (Linux/Mac)
venv\Scripts\activate     # (Windows)

pip install -r requirements.txt

cd levoSaas
python manage.py runserver
```

move to localhost:8000/swagger -> place where all the endpoints are visible and can be used from here.