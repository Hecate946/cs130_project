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
- **`tests/`** - Unit tests and integration tests implemented with **Jest** and **React Native Testing Library**.

### **💻 Running the Frontend**

```sh
# 1. Install dependencies
npm install

# 2. Start the Expo development server
npx expo start

```

##TODO backend
