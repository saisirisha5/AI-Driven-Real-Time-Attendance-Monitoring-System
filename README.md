# ⚙️ AI-Driven Real-Time Attendance Monitoring System  

![Python](https://img.shields.io/badge/Python-3.10.0-blue?logo=python)
![Django](https://img.shields.io/badge/Framework-Django-green?logo=django)
![Firebase](https://img.shields.io/badge/Cloud-Firebase-orange?logo=firebase)
![IoT](https://img.shields.io/badge/IoT-ESP32--CAM-lightgrey)
![Status](https://img.shields.io/badge/Status-Research%20Prototype-yellow)

> **An intelligent, automated attendance solution integrating AI, IoT, and cloud technologies for real-time monitoring and accurate attendance tracking.**  

---

## 🎯 Objectives  

- Automate attendance using **AI-based facial recognition** integrated with **IoT (ESP32-CAM)**.  
- **Eliminate manual entry** and prevent **proxy or duplicate attendance**.  
- Enable **real-time attendance monitoring** through cloud-based synchronization.  
- Store attendance securely and efficiently using **Google Firebase**.  
- Provide a **user-friendly Django web interface** for administrators.  
---

## System Architecture  
![System Architecture](./Static/Architecture.jpeg)

---

## Tech Stack  

| Category | Tools / Frameworks |
|-----------|--------------------|
| **IoT Device** | ESP32-CAM + FTDI Programmer  |
| **AI / ML Library** | `face_recognition` (dlib CNN ResNet-Based) |
| **Backend Framework** | Django |
| **Database / Cloud** | Firebase Firestore |
| **Languages** | Python, HTML, CSS |
| **Architecture Pattern** | MVT (Model-View-Template) |

---

## Key Features  

- 🔹 **AI-Based Facial Recognition:** Automatically detects and identifies faces in real-time.  
- 🔹 **IoT Integration:** ESP32-CAM captures live feed for facial recognition.  
- 🔹 **Cloud Storage (Firebase):** Real-time data sync and scalability.  
- 🔹 **Optimized Recognition:** Caching and preprocessing for faster and more accurate results.  
- 🔹 **Event-Driven Activation:** Camera triggers only on motion or manual reset to prevent overheating.  
- 🔹 **Admin Dashboard:** Django web app for visualizing attendance records dynamically.  

---

## 🚀 Results & Impact  

- ⚡ **Recognition Speed:** 0.1 – 1 second per face  
- ✅ **Accuracy:** Consistent results under varying lighting conditions  
- 🖥️ **Real-Time Sync:** Dashboard updates instantly through Firebase  
- 🧱 **Maintainability:** Clean MVC structure and Django ORM for efficient data handling  

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
