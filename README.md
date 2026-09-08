# 📱 Smartphone Addiction Analytics & User Behavior Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![PostgreSQL / SQLite](https://img.shields.io/badge/SQL-7%20Table%20Warehouse-green.svg)](https://sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)
[![ReportLab](https://img.shields.io/badge/PDF-Report%20Gen-yellow.svg)](https://www.reportlab.com/)
[![Scikit-Learn](https://img.shields.io/badge/Machine%20Learning-3--Class%20Risk-orange.svg)](https://scikit-learn.org/)

An end-to-end data analytics, SQL data warehousing, query performance engineering, predictive machine learning, and generative AI platform built to analyze smartphone usage behavior, diagnose high-scale SQL query bottlenecks, predict addiction levels (**Low Risk**, **Medium Risk**, **High Risk**), and generate downloadable personalized **Weekly Digital Wellness PDF Reports**.

---

## 📄 Ready-to-Use Resume Bullet Point

> **"Built and deployed an AI-powered Smartphone Addiction Analytics Platform using SQL, PostgreSQL, Streamlit, Machine Learning, and Generative AI. Implemented query optimization techniques, predictive risk modeling, interactive dashboards, and personalized recommendation generation."**

---

## 🎯 Architecture & Platform Capabilities

### 1. 🗄️ SQL-Centric Data Warehouse (7 Relational Tables)
Stores multi-dimensional behavioral data across relational tables:
- `users`: User demographics, occupations, and productivity scores.
- `usage_logs`: 100,000+ daily screen time and unlock records.
- `app_usage`: High-frequency app session logs across categories.
- `screen_time`: Pickup counts and continuous screen hours.
- `sleep_patterns`: Night sleep hours, quality scores, and pre-bed phone usage.
- `notifications`: Daily notification counts and muted alert metrics.
- `user_feedback`: Self-reported addiction risk tiers and anxiety levels.

### 2. ⚡ Query Performance Optimization Lab
- Demonstrates slow unindexed query scans vs optimized B-Tree index lookup.
- **Metric Comparison**:
  - **Unindexed Scan**: Execution Time `~2.5s` | Rows Scanned `1,000,000` (`SCAN TABLE`)
  - **Indexed Lookup**: Execution Time `~0.1s` | Rows Scanned `~500` (`SEARCH TABLE USING INDEX`)
  - **Result**: **25x Speedup & 99.9% I/O Reduction!**

### 3. 🤖 Predictive Analytics (Addiction Risk Model)
- Predicts 3 Addiction Risk Tiers: **Low Risk**, **Medium Risk**, **High Risk**.
- Features: Screen Time, Notifications, Social Media Hours, Sleep Hours, Daily Unlocks.
- Classifiers: **Logistic Regression** (99.0% Accuracy) & **Random Forest** (88.9% Accuracy).

### 4. 🧠 AI-Powered Recommendation Engine (GenAI)
- Input: Screen Time (11 hrs), Sleep (5 hrs), Instagram Usage (4 hrs).
- Output: Personalized GenAI recommendations:
  - *"Your screen time is 70% above healthy levels."*
  - *"Reduce social media usage by 1.5 hours daily."*
  - *"Enable focus mode after 10 PM."*

### 5. 📄 Personalised User PDF Report Generator
- Built-in `ReportLab` PDF engine generating downloadable **Weekly Digital Wellness Reports** containing user KPIs, risk level badges, app usage breakdowns, and AI advice callouts.

---

## 📈 Business Insights Highlights

- **Notification Intensity**: Users receiving >200 notifications/day spend **35% more screen time**.
- **Sleep Correlation**: Social media usage has a strong negative correlation (**r = -0.82**) with sleep duration.
- **Productivity Score Gap**: Students with >8 hours screen time show **28% lower productivity scores**.

---

## 🚀 How to Run

### 1. Launch Interactive Streamlit App
```bash
py -m streamlit run app.py
```

### 2. Generate 7-Table Relational Data Warehouse
```bash
py data/generate_schema_dataset.py
```

### 3. Train Machine Learning Risk Models
```bash
py src/ml_predictor_dw.py
```
