# EdgeAI-IoT-Anomaly-Detection

A modular Edge-AI architecture for real-time IoT anomaly detection in smart homes. Uses Isolation Forest and vectorized feature engineering (Delta T) for low-latency threat monitoring at the network gateway.

## 🎯 Features

- **Modular Python Architecture**: Clean separation of concerns with dedicated modules
- **Flask Web Server**: SOC (Security Operations Center) Dashboard for real-time monitoring
- **Isolation Forest ML Model**: Unsupervised anomaly detection for network traffic
- **SQLite Database**: Efficient data storage and retrieval for network logs
- **Pandas Vectorized Feature Engineering**: High-performance timestamp-based feature extraction
- **Real-time Analysis**: Detect anomalies in network traffic patterns

## 🏗️ Architecture

```
EdgeAI-IoT-Anomaly-Detection/
├── main.py                          # Application entry point
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
└── src/
    ├── data_handler.py             # SQLite database operations
    ├── anomaly_detector.py         # Isolation Forest model
    ├── feature_engineer.py         # Pandas-based feature engineering
    ├── dashboard.py                # Flask web server
    ├── sample_data_generator.py    # Sample data generation
    └── templates/
        └── dashboard.html          # SOC Dashboard UI
```

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/sinister-virus/EdgeAI-IoT-Anomaly-Detection.git
cd EdgeAI-IoT-Anomaly-Detection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### Option 1: Full Demo (Recommended)
Run the complete setup with sample data and dashboard:
```bash
python main.py --generate 2000 --train --dashboard
```

This will:
1. Initialize the system
2. Generate 2000 sample network logs (10% anomalous)
3. Train the Isolation Forest model
4. Launch the SOC Dashboard at http://localhost:5000

### Option 2: Step-by-Step

1. **Initialize and generate sample data**:
```bash
python main.py --generate 2000
```

2. **Train the anomaly detection model**:
```bash
python main.py --train
```

3. **Analyze recent data**:
```bash
python main.py --analyze
```

4. **Launch the SOC Dashboard**:
```bash
python main.py --dashboard
```

## 🖥️ SOC Dashboard

The web-based dashboard provides:

- **Real-time Statistics**: Total logs, anomalies detected, anomaly rate, recent activity
- **Network Log Viewer**: View recent network traffic logs
- **Anomaly Detection**: Analyze data and detect anomalies with one click
- **Model Training**: Train or retrain the ML model
- **Auto-refresh**: Updates every 30 seconds

Access the dashboard at: `http://localhost:5000`

### Dashboard Features:

- 🔄 **Refresh Logs**: Reload the latest network logs
- 🔍 **Analyze Data**: Detect anomalies in recent traffic
- 🧠 **Train Model**: Train the Isolation Forest model on existing data

## 🔧 Components

### 1. Data Handler (`src/data_handler.py`)
- SQLite database management
- CRUD operations for network logs
- Efficient querying with timestamp indexing
- Batch insert operations for performance

### 2. Feature Engineer (`src/feature_engineer.py`)
- **Vectorized timestamp features** using Pandas:
  - Delta T (time between events)
  - Rolling time statistics
  - Time-based aggregations
- **Traffic features**:
  - Bytes sent/received
  - Traffic ratios and z-scores
- **Device-based features**:
  - Event counts per device
  - Unique destinations and ports

### 3. Anomaly Detector (`src/anomaly_detector.py`)
- Isolation Forest implementation
- Unsupervised anomaly detection
- Configurable contamination rate
- Model persistence (save/load)
- Anomaly scoring and analysis

### 4. Flask Dashboard (`src/dashboard.py`)
- RESTful API endpoints
- Real-time statistics
- Interactive web interface
- JSON responses for easy integration

## 📊 API Endpoints

- `GET /` - Dashboard home page
- `GET /api/statistics` - Get system statistics
- `GET /api/recent-logs?limit=N` - Get N recent logs
- `GET /api/anomalies?limit=N` - Get N recent anomalies
- `POST /api/analyze` - Analyze data and detect anomalies
- `POST /api/train-model` - Train the ML model
- `GET /api/health` - Health check

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Database Configuration
DB_PATH = 'iot_security.db'

# Flask Configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000

# Anomaly Detection Configuration
CONTAMINATION = 0.1      # Expected proportion of outliers (10%)
N_ESTIMATORS = 100       # Number of trees in Isolation Forest
TIME_WINDOW_SECONDS = 60 # Time window for feature aggregation
```

## 🧪 Sample Data Generator

Generate synthetic network logs for testing:

```bash
# Generate 2000 logs with 10% anomalies
python src/sample_data_generator.py
```

The generator creates:
- Normal traffic patterns (common ports, regular bytes)
- Anomalous patterns:
  - Unusual high ports
  - High traffic volumes
  - Suspicious IP addresses
  - Rapid request patterns

## 📈 Feature Engineering Details

The system uses **Pandas vectorized operations** for efficient feature engineering:

### Timestamp-based Features (Delta T):
- Time difference between consecutive events
- Per-device time deltas
- Per-source IP time deltas
- Rolling mean and std of time deltas

### Traffic Features:
- Total bytes (sent + received)
- Bytes ratio
- Rolling traffic statistics
- Z-scores for anomaly detection

### Temporal Features:
- Hour of day
- Day of week
- Events per time window

## 🔒 Security Considerations

This system is designed for:
- **Network edge deployment** (IoT gateway)
- **Real-time anomaly detection**
- **Low-latency processing**
- **Privacy-preserving** (local processing)

## 🛠️ Command-Line Options

```bash
usage: main.py [-h] [--dashboard] [--generate N] [--train] [--analyze] 
               [--port PORT] [--host HOST]

Options:
  --dashboard       Run the Flask SOC dashboard
  --generate N      Generate N sample network logs
  --train          Train the anomaly detection model
  --analyze        Analyze recent data for anomalies
  --port PORT      Port for Flask dashboard (default: 5000)
  --host HOST      Host for Flask dashboard (default: 0.0.0.0)
```

## 📝 Example Workflow

```bash
# 1. Generate sample data
python main.py --generate 5000

# 2. Train the model
python main.py --train

# 3. Analyze data
python main.py --analyze

# 4. Launch dashboard for monitoring
python main.py --dashboard
```

## 🔬 Technical Details

- **Machine Learning**: Isolation Forest (scikit-learn)
- **Data Processing**: Pandas with vectorized operations
- **Database**: SQLite with indexed queries
- **Web Framework**: Flask
- **Frontend**: Vanilla JavaScript with responsive CSS

## 📄 License

See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or issues, please open an issue on GitHub.
