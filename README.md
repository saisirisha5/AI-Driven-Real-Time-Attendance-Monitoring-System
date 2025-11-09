# ⚙️ AI-Driven Real-Time Attendance Monitoring System  

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Django](https://img.shields.io/badge/Framework-Django-green?logo=django)
![Firebase](https://img.shields.io/badge/Cloud-Firebase-orange?logo=firebase)
![IoT](https://img.shields.io/badge/IoT-ESP32--CAM-lightgrey)
![License](https://img.shields.io/badge/License-Proprietary-red)
![Status](https://img.shields.io/badge/Status-Research%20Prototype-yellow)

> **An intelligent, automated attendance solution integrating AI, IoT, and cloud technologies for real-time monitoring and accurate attendance tracking.**  

---

## Abstract  

Manual attendance systems are often error-prone, time-consuming, and prone to proxy entries.  
This project presents an **AI-driven attendance monitoring system** that automates attendance using **facial recognition** and **IoT-based live image capture**.  

An **ESP32-CAM** captures live facial images which are processed using a **Python-based face recognition engine**.  
Attendance data is stored securely on **Google Firebase**, and a **Django-powered web interface** displays the results in real-time for organizational administrators.  

Optimizations like **face encoding caching**, **event-driven camera activation**, and **image normalization** improved performance and recognition speed (≈0.1–1s per face).  

---

## System Architecture  
![System Architecture](.Static/Architecture.jpeg)

---

## Tech Stack  

| Category | Tools / Frameworks |
|-----------|--------------------|
| **IoT Device** | ESP32-CAM |
| **AI / ML Library** | `face_recognition` (Python) |
| **Backend Framework** | Django |
| **Database / Cloud** | Firebase Firestore |
| **Languages** | Python, HTML, CSS |
| **Architecture Pattern** | MVC (Model-View-Controller) |

---

## Key Features  

- 🔹 **AI-Based Facial Recognition:** Automatically detects and identifies faces in real-time.  
- 🔹 **IoT Integration:** ESP32-CAM captures live feed for facial recognition.  
- 🔹 **Cloud Storage (Firebase):** Real-time data sync and scalability.  
- 🔹 **Optimized Recognition:** Caching and preprocessing for faster and more accurate results.  
- 🔹 **Event-Driven Activation:** Camera triggers only on motion or manual reset to prevent overheating.  
- 🔹 **Admin Dashboard:** Django web app for visualizing attendance records dynamically.  

---

##  Challenges & Solutions  

### Hardware Challenges  

- **WiFi Instability (Serial Data Loss):**  
  Resolved by periodic ESP32 resets to reinitialize and re-establish clean connections.  

- **Overheating Issue:**  
  Implemented trigger-based activation to prevent continuous camera operation.  

### Software Challenges  

- **Lighting Variations:**  
  Solved with image preprocessing (brightness/contrast normalization).  

- **Recomputation Overhead:**  
  Cached face encodings to minimize redundant processing and speed up recognition.  

---

## 🚀 Results & Impact  

- ⚡ **Recognition Speed:** 0.1 – 1 second per face  
- ✅ **Accuracy:** Consistent results under varying lighting conditions  
- 🖥️ **Real-Time Sync:** Dashboard updates instantly through Firebase  
- 🧱 **Maintainability:** Clean MVC structure and Django ORM for efficient data handling  

---

## Future Enhancements  

- 🧍‍♂️ **Gait-Based Validation:** Additional behavior-based layer for higher accuracy.  
- 🎨 **Enhanced UI/UX:** Interactive and analytics-driven dashboard.  
- ⚙️ **Offline Mode:** Cache-based local attendance storage for poor network environments.  


---

## 🧰 Tools Used  

- Visual Studio Code  
- Arduino IDE  
- Python 3.10.0
- Firebase Console  
- Django Framework  

---

## ⚠️ Usage Restrictions  

This repository is **not open-source**.  
It is intended **for demonstration and educational reference only**.  

- ❌ Do **not fork** or **clone** this repository.  
- ❌ Do **not copy**, **reuse**, or **redistribute** any part of the source code.  

📬 For permissions or collaboration queries:  
📧 [prabhalasaisirisha25@gmail.com](mailto:prabhalasaisirisha25@gmail.com)  

📄 Refer to [LICENSE.txt](./LICENSE.txt) for complete terms.  

---

⭐ **Developed by [Sai Sirisha Devi Prabhala](mailto:prabhalasaisirisha25@gmail.com)**  
> _Making attendance systems smarter, faster, and fully automated with AI + IoT + Cloud._
