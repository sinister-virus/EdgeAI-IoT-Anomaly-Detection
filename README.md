# 🛡️ A Unified Edge-AI Architecture for IoT Anomaly Detection

## 📌 Project Overview

This project presents a **Unified Edge-AI Architecture** designed for secure and autonomous smart home device management. It utilizes **Isolation Forest (Unsupervised ML)** to detect behavioral anomalies directly at the network gateway (Edge), ensuring **low-latency processing** and **privacy-centric security**.

> **🧾 Subject Code:**  CTMTAIDS SIII P1  
> **📘 Subject Name:** Major Project I  
> **🎓 Course:** M.Tech in Artificial Intelligence & Data Science *(Specialization in Cybersecurity)*  
> **🏛️ Institute:** National Forensic Sciences University (NFSU), Gandhinagar   
> **👨‍🏫 Supervisor:** Mr. Prakash Khasor *(Assistant Professor)*  

---

## 🚀 Key Features

- ⚡ **Edge-Centric Design:** Low-latency log processing at the network gateway to eliminate cloud bottlenecks.  
- 🔢 **Vectorized Feature Engineering:** High-performance calculation of Reconnect Delta Time (\(\Delta t\)) using Pandas.  
- 🧠 **Unsupervised Learning:** Uses Isolation Forest to establish behavioral baselines and detect zero-day threats.  
- 📊 **Real-Time SOC Dashboard:** Interactive Flask-based interface with dynamic traffic and risk visualization.  
- 🛡️ **Active Remediation:** Human-in-the-loop API mechanism for immediate device isolation and blocking.  

---

## 🛠️ Tools & Technologies

- **Python 3.11+**
- **Flask** (Lightweight Web Framework)
- **Scikit-learn** (Isolation Forest Model)
- **Pandas & NumPy** (Vectorized Data Processing)
- **SQLite** (Persistent Edge Storage)
- **Tailwind CSS & Chart.js** (Frontend Visualization)

---

## 📁 Repository Structure

| Path | Description |
|-----|------------|
| `src/main.py` | Flask Web Server for the SOC Dashboard |
| `src/monitor.py` | Real-time Edge Monitor & Log Simulator (forwarding to Wazuh) |
| `src/ai_model.py` | AI Inference Engine (Isolation Forest Logic) |
| `src/train_model.py` | Vectorized feature calculation & model training script |
| `src/data_handler.py` | SQLite Database CRUD operations |
| `src/notify.py` | Alerting system (Telegram/Console) |
| `src/templates/` | HTML templates for the Dashboard and Event logs |
| `data/` | Contains `logs.csv` (Raw logs) and `smart_home_soc.db` |
| `models/` | Stores serialized `anomaly_model.pkl` |
| `notebooks/` | Jupyter notebooks for exploratory data analysis (EDA) |
| `requirements.txt` | Project dependencies and libraries |

---

## 🏗️ System Architecture

The system follows a **modular architecture** where data collection, AI inference, and visualization operate independently to ensure **scalability** and **reliability** in an Edge environment.

---

## 📊 Innovation: Reconnect Delta Time (Δt)

The core innovation is the use of **vectorized operations** to calculate the temporal stability of device connections.

```python
# High-performance Vectorized Calculation
df_connect['reconnect_delta'] = (
    df_connect.groupby('MAC')['timestamp']
    .diff()
    .dt.total_seconds()
    .fillna(0)
)
```

The model identifies anomalies based on **unstable reconnection patterns**  
(e.g., **3–8 seconds** for attackers vs. **180+ seconds** for normal sensors).

---

# ⚙️ Installation & Usage

## 📥 Installation

### 1️⃣ Clone the Repository

```python
git clone https://github.com/sinister-virus/EdgeAI-IoT-Anomaly-Detection.git
cd EdgeAI-IoT-Anomaly-Detection
```

### 2️⃣ Create a Virtual Environment (Recommended)
```python
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```python
pip install -r requirements.txt
```

### ▶️ Usage
🔹 Train the Model
```python
python src/train_model.py
```

This script will:
1. Compute vectorized features from `data/logs.csv`
2. Train the Isolation Forest algorithm
3. Serialize and save the trained model to `models/anomaly_model.pkl`

🔹 Start the SOC Dashboard
```python
python src/main.py
```

Access the interactive dashboard at:
👉 http://127.0.0.1:5000

🔹 Run Edge Log Monitor
```python
python src/monitor.py
```
This simulates real-time IoT traffic, performs AI inference on incoming packets, and continuously updates the SOC dashboard.

---

## 🔔 Configure Telegram Alerts

The `notify.py` module sends alerts via Telegram. To keep your credentials secure, you should **never hardcode** your bot token or chat ID. Instead, use **environment variables** or a `.env` file.

### 1️⃣ Local Development

1. Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

2. Install `python-dotenv` to load `.env` variables:

```bash
pip install python-dotenv
```
The notify.py module will automatically load these values from the .env file.


### 2️⃣ CI/CD or GitHub Actions

1. Go to **Settings → Secrets and variables → Actions → New repository secret** in your GitHub repository.

2. Add these secrets:

| Name                | Value               |
|---------------------|---------------------|
| TELEGRAM_BOT_TOKEN  | your_bot_token_here |
| TELEGRAM_CHAT_ID    | your_chat_id_here   |

3. In your GitHub Actions workflow, the secrets will automatically be available as environment variables:

```yaml
env:
  TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
  TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

### 3️⃣ Safety

- If credentials are missing, `notify.py` logs a warning instead of failing.  
- No sensitive information is stored in the repository.  
- Always keep `.env` files in `.gitignore` to prevent accidental commits.


---

## 📜 License

This project is licensed under the **MIT License**.  
See the [`LICENSE`](LICENSE) file for details.

---

## 🙌 Acknowledgements

- **Mr. Prakash Khasor** for supervision and technical guidance.
- **School of Cyber Security & Digital Forensics**, NFSU Gandhinagar.
- **CoE-CS on 5G Use Case Lab** *(DoT, Govt. of India)* for hardware and infrastructure support.
