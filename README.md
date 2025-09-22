# Anomaly Detection

This project implements an **anomaly detection system** using **Isolation Forest** for classical machine learning and integrates **Large Language Models (LLMs)** to generate descriptive alerts for detected anomalies. It is designed to simulate real-time anomaly detection on streaming sensor data.

---

## 📌 Project Summary

- **Goal**: Detect anomalies in streaming sensor data and provide human-readable explanations using LLMs.  
- **Core Components**:
  - `train_model.ipynb`: Prepares synthetic data, trains an Isolation Forest model, and saves the trained model as anomaly_model.joblib.
  - `client.py`: Loads the trained model, detects anomalies in data from the server, and queries an LLM for labeling and explanation.
  - `server.py`: Continuously streams normal and anomalous data points (no modification required).  
- **ML Algorithm**: Isolation Forest (unsupervised anomaly detection).  
- **LLM Integration**: Uses Together AI API (DeepSeek LLaMA3 70B) to label and explain anomalies.

---

## 🧠 Workflow

1. **Data Preparation & Training**  
   - Generate synthetic sensor data.  
   - Preprocess features.  
   - Train an Isolation Forest model.  
   - Save the trained model.  

2. **Anomaly Detection**  
   - Load the model in `client.py`.  
   - Stream data from `server.py`.  
   - Predict anomalies in real time.  

3. **LLM-based Explanation**  
   - For detected anomalies, send a request to Together API.  
   - Receive a label and description of the anomaly.  
   - Display alerts in a human-readable format.

---

## 📊 Features

- Real-time anomaly detection  
- LLM-powered explanations for anomalies  
- Other extensions:
  - PCA-based visualization of normal vs anomalous points(visualization.png)
  - Logging anomalies to `anomalies.csv` 
  - Adding confidence scores  

---

## Tech Stack

- **Machine Learning**: scikit-learn (Isolation Forest)  
- **Visualization**: matplotlib / seaborn 
- **Language Model API**: Together AI – LLaMA3 70B  
- **Programming Language**: Python 

---
