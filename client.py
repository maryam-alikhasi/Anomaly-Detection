import socket
import json
import pandas as pd
import joblib
import together
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import csv
import os
import random

HOST = 'localhost'
PORT = 9999

model = joblib.load("anomaly_model.joblib")

TOGETHER_API_KEY = "4ef3773beaa9827438534e25704e1153ae6b524d3eb059c9ea93dfeb9a37f977"
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"

client = together.Together(api_key=TOGETHER_API_KEY)

history = []

if not os.path.exists("anomalies.csv"):
    with open("anomalies.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["src_port", "dst_port", "packet_size",
                         "duration_ms", "protocol", "port_diff",
                         "bytes_per_ms", "label", "reason",
                         "confidence"])

def describe_anomaly(data, client):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that analyzes network traffic data and returns ONLY the type of anomaly and reason.\n"
                "Only return a plain response in the following format:\n"
                "Label: <type of anomaly>\nReason: <reason>"
            )
        },
        {
            "role": "user",
            "content": f"Analyze the following network data:\n{data}\n\n"
        }
    ]
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=False,
        temperature=0.3,
    )
    cleaned_response = re.sub(r"<think>.*?</think>", "", response.choices[0].message.content, flags=re.DOTALL).strip()
    return cleaned_response

def pre_process_data(data):
    df = pd.DataFrame([data])
    df = pd.get_dummies(df, columns=["protocol"], drop_first=True)
    if "protocol_UDP" not in df.columns:
        df["protocol_UDP"] = 0
    return df

def visualize_data(data_points):
    df = pd.DataFrame(data_points)
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(df.drop(columns=["label"]))
    df["PC1"] = reduced[:, 0]
    df["PC2"] = reduced[:, 1]

    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x="PC1", y="PC2", hue="label", palette={"normal": "green", "anomaly": "red"})
    plt.title("Network Traffic Visualization with PCA")
    plt.savefig("visualization.png")
    plt.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    buffer = ""
    print("Client connected to server.\n")

    data_buffer = []

    while True:
        chunk = s.recv(1024).decode()
        if not chunk:
            break
        buffer += chunk

        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            try:
                data = json.loads(line)
                print(f'Data Received:\n{data}\n')

                processed = pre_process_data(data)
                prediction = model.predict(processed)[0]

                score = model.decision_function(processed)[0]
                confidence = min(1.0, abs(score) / 0.5)

                if prediction == -1:
                    response = describe_anomaly(data, client)
                    print(f"\nAnomaly Detected! Confidence: {round(confidence, 2)}\n{response}\n")

                    match = re.search(r"Label:\s*(.*)\nReason:\s*(.*)", response)
                    if match:
                        label, reason = match.groups()
                    else:
                        label, reason = "Anomaly", "Unspecified"

                    with open("anomalies.csv", "a", newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            data["src_port"], data["dst_port"], data["packet_size"],
                            data["duration_ms"], data["protocol"], data["port_diff"],
                            data["bytes_per_ms"] , label, reason, confidence
                        ])

                    data_buffer.append({**processed.iloc[0].to_dict(), "label": "anomaly"})
                else:
                    data_buffer.append({**processed.iloc[0].to_dict(), "label": "normal"})

                if len(data_buffer) >= 20:
                    visualize_data(data_buffer)
                    data_buffer.clear()

            except json.JSONDecodeError:
                print("Error decoding JSON.")
