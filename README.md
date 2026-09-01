# 🛡️ Phishing Email Detector

An educational and defensive machine learning project that classifies email text into:

- **Phishing** – A potentially fraudulent or malicious email
- **Legitimate** – A normal email

The project uses classical machine learning techniques with **Scikit-learn**, including **TF-IDF** and three classification models: **Logistic Regression, Multinomial Naive Bayes, and Linear SVM**.

It also includes a **FastAPI backend** and a simple **HTML/CSS/JavaScript frontend** for interacting with the trained model.

> ⚠️ **Disclaimer:** This project is for educational purposes only. The model's accuracy is limited by the size and diversity of the training dataset. The `dataset.csv` file contains a limited number of synthetically generated examples. This project should not be used as a real-world email security solution or in production environments.

---

## 🎯 Project Objectives

- Detect potentially phishing emails using machine learning.
- Convert email text into numerical features using TF-IDF.
- Compare different machine learning classification models.
- Select the best-performing model based on F1-score.
- Build a REST API using FastAPI.
- Create a simple web interface for email classification.
- Demonstrate how machine learning can be applied to cybersecurity.

---

## 🧠 Machine Learning Approach

The project uses **TF-IDF (Term Frequency–Inverse Document Frequency)** to transform email text into numerical features.

Three machine learning models are trained and compared:

1. **Logistic Regression**
2. **Multinomial Naive Bayes**
3. **Linear SVM**

The best-performing model is automatically selected based on its **F1-score** and saved together with the trained vectorizer.

### Evaluation Metrics

The models are evaluated using:

- Accuracy
- Precision
- Recall
- F1-score

---

## 📁 Project Structure

```text
phishing-detector/
│
├── model/
│   ├── train_model.py
│   ├── dataset.csv
│   └── model.pkl
│
├── backend/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── README.md
