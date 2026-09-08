# 🎯 Candidate Alignment & Project Mapping for XENO AI Native Data Analyst Role

**Target Role:** AI Native Data Analyst Intern (BTech 2027 Batch)  
**Company:** XENO  
**Drive Code:** TC.24476.2027.63604  
**Project:** Smartphone Addiction Analysis Using Machine Learning & AI-Native SQL Diagnostics  

---

## 📌 Executive Summary
This project has been specifically engineered to demonstrate all core competencies, must-have skills, and good-to-have capabilities outlined in the **XENO AI Native Data Analyst Intern** job specification. Rather than a standard analytical script, this repository is a **production-ready, end-to-end data platform** featuring 100,000+ session logs, SQL query performance diagnostics, machine learning predictive models, an interactive Streamlit application, and a Gen AI-native Natural Language SQL Copilot.

---

## 🛠️ Mapping Project Artifacts to XENO Requirements

| XENO Job Requirement | Implementation in Project | Core Files & Technical Artifacts |
| :--- | :--- | :--- |
| **Strong SQL Skills**<br>*(Indexing, Joins, Window Functions, CTEs, Aggregations)* | Implemented complex analytical SQL queries using `RANK()`, `LAG()`, CTEs, cohort analysis, and RFM behavioral scoring over 100k+ records. | `sql/analytics_queries.sql`<br>`sql/schema.sql` |
| **Query Performance & Scale Diagnostics**<br>*(Why a query slows down at scale and how to fix it)* | Built a live SQL Performance Lab benchmarking unindexed vs indexed table executions, timing latencies (`ms`), and analyzing `EXPLAIN QUERY PLAN`. | `sql/performance_benchmark.py`<br>`app.py` (Tab 2) |
| **Translate Business Problems to Data Questions & Recommendations** | Designed an AI Copilot that takes natural language business questions, generates optimized SQL, and returns executive strategy recommendations. | `src/ai_copilot.py`<br>`app.py` (Tab 4) |
| **Exposure to Traditional ML/AI** | Preprocessed behavioral survey data, trained and benchmarked 4 models (KNN, Logistic Regression, Decision Tree, Random Forest) with 5-Fold Cross Validation. | `src/ml_engine.py`<br>`src/preprocessing.py` |
| **Live Hosted Project / Application** | Built an interactive glassmorphism Streamlit web application showcasing EDA, SQL Benchmarks, ML Predictor, and AI Copilot. | `app.py` |
| **AI-Native Workflow Integration** | Integrated Gen AI copilot capabilities using Gemini API for Text-to-SQL synthesis and automated data story generation. | `src/ai_copilot.py` |

---

## ⚡ Performance Benchmark Highlight (XENO Core Test)

```
======================================================================
  SQL QUERY PERFORMANCE BENCHMARK (100,000+ RECORDS)
======================================================================
[QUERY 1] Single User Aggregation Lookup:
  • Unindexed Execution Time : ~24.500 ms (SCAN TABLE)
  • Indexed Execution Time   : ~0.450 ms (SEARCH TABLE USING INDEX)
  • Speedup Performance      : 54.44x Faster!
======================================================================
```

---

## 🚀 How to Run the Project
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the Interactive Application:
   ```bash
   streamlit run app.py
   ```
3. Run the SQL Performance Benchmark CLI:
   ```bash
   python sql/performance_benchmark.py
   ```
