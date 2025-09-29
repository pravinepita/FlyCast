# ✈️ SkyFareCast – Flight Price Prediction System

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-orange?logo=streamlit)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-lightgrey)
![Airflow](https://img.shields.io/badge/Workflow-Airflow-blueviolet)
![Grafana](https://img.shields.io/badge/Monitoring-Grafana-red)
![License](https://img.shields.io/badge/License-MIT-green)

SkyFareCast is a **flight price prediction system** that predicts flight ticket prices, automates scheduled predictions, and provides a monitoring dashboard for model performance and data quality. It combines **user interactivity**, **API endpoints**, **scheduled jobs**, and **visual analytics** in one end-to-end solution.

> 🚀 Built with 💡 curiosity, ✈️ passion for travel, and 🧠 applied machine learning!  

---

## 🌟 Table of Contents

- [Project Highlights](#project-highlights)  
- [Demo Screenshots](#demo-screenshots)  
- [Tech Stack](#tech-stack)  
- [How It Works](#how-it-works)  
- [Project Structure](#project-structure)  
- [Getting Started](#getting-started)  
- [CSV Data](#csv-data)  
- [Conclusion](#conclusion)  

---

## 🌟 Project Highlights

- On-demand flight price predictions through **Streamlit UI**
- **FastAPI backend** to expose ML model and store results in PostgreSQL
- Scheduled predictions with **Airflow DAGs**
- Data validation & preprocessing with **Python**
- Monitoring dashboard using **Grafana**  
  - Pie chart for model performance (accuracy)  
  - Bar chart for high-alert inputs  
- End-to-end pipeline for **data ingestion, validation, prediction, and monitoring**

---
## 📸 Demo Screenshots

### Streamlit App
| Streamlit UI 1 | Streamlit UI 2 | Streamlit UI 3 |
|----------------|----------------|----------------|
| ![Streamlit 1](https://github.com/aswinroshanrajendran/SkyFareCast/blob/main/images/streamlit%20-1.png) | ![Streamlit 2](https://github.com/aswinroshanrajendran/SkyFareCast/blob/main/images/streamlit%20-%202.png) | ![Streamlit 3](https://github.com/aswinroshanrajendran/SkyFareCast/blob/main/images/streamlit%20-%203.png) |

### FastAPI Predictions
| FastAPI Prediction |
|------------------|
| ![FastAPI](https://github.com/aswinroshanrajendran/SkyFareCast/blob/main/images/Fast%20api%20-%201.png) |

### Airflow DAGs
| Data Ingestion DAG | Prediction DAG |
|------------------|----------------|
| ![Airflow Ingestion](https://github.com/aswinroshanrajendran/SkyFareCast/blob/main/images/Airflow%20-%201.png) | ![Airflow Prediction](https://github.com/aswinroshanrajendran/SkyFareCast/blob/main/images/Airflow%20-%202.png) |

### PostgreSQL Database (Predictions Storage)
| Database Screenshot 1 | Database Screenshot 2 |
|----------------------|----------------------|
| ![Postgres 1](https://github.com/aswinroshanrajendran/SkyFareCast/blob/main/images/pg%20-%201.png) | ![Postgres 2](https://github.com/aswinroshanrajendran/SkyFareCast/blob/main/images/pg%20-%202.png) |

### Grafana Dashboards
| Pie Chart | Bar Chart |
|-----------|-----------|
| ![Grafana Pie](https://github.com/aswinroshanrajendran/SkyFareCast/blob/main/images/grafana%20-%201.png) | ![Grafana Bar](https://github.com/aswinroshanrajendran/SkyFareCast/blob/main/images/grafana%20-%201.png) |

---

## 🛠 Tech Stack

- **Language**: Python 3.10+  
- **Libraries**: 
  - `pandas`, `numpy`, `requests`, `scikit-learn`, `SQLAlchemy`  
- **Web Framework**: Streamlit, FastAPI  
- **Workflow Orchestration**: Apache Airflow  
- **Monitoring & Visualization**: Grafana  
- **Database**: PostgreSQL  
- **IDE**: VS Code  
- **Version Control**: Git + GitHub  

---

## 🧠 How It Works

1. **User Interface (Streamlit)**  
   - Users provide flight details and get real-time predictions.  
   - Historical predictions are displayed with input features.  

2. **ML Model API (FastAPI)**  
   - Exposes `/predict` endpoint for model predictions.  
   - Saves results to the database with features and timestamp.  

3. **Database (PostgreSQL + SQLAlchemy)**  
   - Stores all prediction records.  
   - Enables historical analysis for monitoring model performance.  

4. **Scheduled Prediction Pipeline (Airflow)**  
   - Ingests new data and triggers predictions at defined intervals.  
   - Logs all scheduled runs for auditing and debugging.  

5. **Data Validation & Preprocessing**  
   - Ingested raw data is checked for missing or invalid values.  
   - Cleaned and transformed data is stored as “good data” for predictions.  

6. **Monitoring Dashboard (Grafana)**  
   - **Pie Chart**: Shows model accuracy (`Correct`, `Incorrect`, `Skipped`).  
   - **Bar Chart**: Highlights input features triggering high alerts.  
   - Enables visual tracking of model performance and data quality over time.  

---

## 📂 Project Structure
SkyFareCast/
│
├─ airflow/
│  ├─ dags/
│  │  ├─ ingestion_dag.py
│  │  └─ prediction_dag.py
│  └─ logs/
│
├─ predictions/
│  └─ prediction_results.csv
│
├─ stats/
│  └─ data_stats.csv
│
├─ src/
│  ├─ api/
│  │  └─ main.py           # FastAPI app
│  ├─ app/
│  │  └─ streamlit_app.py  # Streamlit UI
│  └─ utils/
│     └─ preprocessing.py
│
├─ requirements.txt
└─ README.md

---

## 🚀 Getting Started

### **1. Clone the repository**
```bash
git clone https://github.com/aswinroshanportfolio/SkyFareCast.git
cd SkyFareCast
```

### **2. Set up Python environment**
```bash
python -m venv venv
# Linux/Mac
source venv/bin/activate  
# Windows
venv\Scripts\activate     
pip install -r requirements.txt
```

### **3. Run FastAPI**
```bash
uvicorn src.api.main:app --reload

```

### **4. Run Streamlit**
```bash
streamlit run src.app.streamlit_app.py

```

### **5. Start Airflow**

```bash
airflow db init
airflow webserver --port 8080
airflow scheduler

```

### **6. Grafana**

Configure Infinity Data Source.

Import CSV files (prediction_results.csv, data_stats.csv).

Create Pie Chart and Bar Chart panels.

## **📊 CSV Data**

predictions/prediction_results.csv: Contains flight prediction results with features.

stats/data_stats.csv: Contains data quality metrics and high-alert counts.

## **🏁 Conclusion**

SkyFareCast demonstrates a complete end-to-end ML workflow including:

Prediction API

User-facing interface

Scheduled data processing

Monitoring and visualization

It’s an excellent example of production-ready ML pipelines integrating Python, Airflow, FastAPI, Streamlit, PostgreSQL, and Grafana.

## 🙋‍♂️ About Me

**Aswin Roshan Rajendran**  
🎓 Master's in Data Science & Analytics, **EPITA**, Paris  
📍 Paris, France  
📫 [aswinroshan17@gmail.com](mailto:aswinroshan17@gmail.com)

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---
