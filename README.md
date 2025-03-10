# **CS 130 - BruinHub Project**

**Authors:** Nathan Zhang, Ingrid Lee, Paul Zhang, Justin Wang, Cyrus Asasi, George Zhou

## **App Overview**

BruinHub is a full-stack mobile application designed to provide UCLA students with **real-time facility occupancy, operating hours, and push notifications**. The project is structured into two repositories:

- **[`bruinhub-app`]** (Frontend - FE): Built with **React Native** and **Expo**.
- **[`bruinhub-backend`]** (Backend - BE): Powered by **Flask (Python)**.

---

## **Frontend (`bruinhub-app`)**

The frontend is a **mobile application** developed using **React Native** with **Expo**.

### **FE Directory Structure**

- **`app/`** - Houses all screen components (ex. `HomeScreen.tsx`, `NotificationScreen.tsx`).
- **`assets/`** - Contains fonts, images, and static resources used in the UI.
- **`components/`** - Reusable UI components (ex. `HomeCard.tsx`, `CapacityComponent.tsx`).
- **`constants/`** - Stores shared constants, such as colors and API URLs.
- **`__tests__/`** - Unit tests and integration tests implemented with **Jest** and **React Native Testing Library**.

### **💻 Running the Frontend**

```sh
# 1. Install dependencies
npm install

# 2. Start the Expo development server
npx expo start

```

## **Backend (`bruinhub-backend`)**

The backend is a **Flask-based service** that periodically scrapes UCLA facility data and provides REST APIs for the frontend.

### **BE Directory Structure**

- **`app.py`** - Main Flask application entry point with core configuration and health check endpoint.
- **`database/`** - Database interaction logic for different data domains:
  - Database connection management
  - Domain-specific database operations (gyms, dining, library)
- **`models/`** - SQLAlchemy data models defining database schema and object structures
- **`routes/`** - API endpoint definitions and request handlers
- **`scrapers/`** - Web scraping logic for different UCLA facility data sources
- **`tasks/`** - Background task definitions and scheduling:
  - Periodic data scraping jobs
  - Session management tasks
- **`config/`** - Configuration files and constants:
  - Database URLs
  - API endpoints
  - Facility IDs and static data
- **`services/`** - Business logic and utility services:
  - Notification handling
  - Data processing
- **`tests/`** - Unit tests and integration tests for backend functionality

### **💻 Running the Backend**

```sh
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the Flask server
python app.py

# 3. Start the scraping service
python scraper.py

# 4. Start the notifications service
python notifications_server.py
```

##TODO backend
