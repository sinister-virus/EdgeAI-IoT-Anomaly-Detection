import sys
import os

# --- UNIVERSAL IMPORT FIX ---
# This block ensures the script runs correctly whether using "python -m src.main"
# OR pressing the PyCharm "Play" button.
current_dir = os.path.dirname(os.path.abspath(__file__))  # Path to src/
project_root = os.path.dirname(current_dir)  # Path to Major_Project_I/
if project_root not in sys.path:
    sys.path.insert(0,project_root)
# -----------------------------

from flask import Flask,render_template,jsonify,request
# Now these absolute imports work in both modes
from src import data_handler
from src import ai_model
from src.notify import send_alert
import pandas as pd

# Initialize the Flask app and ensure the AI model and DB are ready
app = Flask(__name__,static_folder='static',template_folder='templates')

# Initialize DB and Load Model on App Startup
data_handler.initialize_database()
ai_model.load_model()


# --- Routes for HTML Pages ---

@app.route("/")
def index():
    """Renders the main dashboard page."""
    df = data_handler.fetch_logs(limit=20)
    # Ensure device_name is used for the template display
    if not df.empty and 'device_name' in df.columns:
        df['device'] = df['device_name']
    logs_data = df.to_dict(orient="records")
    return render_template("index.html",logs=logs_data)


@app.route("/device_events")
def device_events():
    """Renders the detailed device event history page."""
    df = data_handler.fetch_logs(limit=100)
    events_data = df.to_dict(orient="records")
    for event in events_data:
        # Ensure 'risk_score' is float for the template logic
        if event.get('risk_score'):
            event['risk_score'] = float(event['risk_score'])
    return render_template("device_events.html",events=events_data)


# --- API ENDPOINTS for Dynamic Dashboard and Actions ---

@app.route("/api/latest_logs",methods=['GET'])
def get_latest_logs():
    """API endpoint to fetch latest log entries as JSON for real-time updates."""
    df = data_handler.fetch_logs(limit=50)
    if not df.empty:
        df['risk_score'] = df['risk_score'].astype(float)
        df['device'] = df['device_name']  # Add friendly name for dashboard
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/summary_stats",methods=['GET'])
def get_summary_stats():
    """API endpoint to fetch aggregated data for the top dashboard cards."""
    df = data_handler.fetch_logs(limit=500)

    if df.empty:
        return jsonify({
            "total_devices": 0,"total_anomalies": 0,"average_usage": "0 KB/s",
            "device_counts": {},"overall_risk_pct": 0.0
        })

    total_devices = df['device_mac'].nunique()
    total_anomalies = df[df['anomaly_flag'] == 'YES'].shape[0]
    avg_usage = round(df['usage'].mean(),2)
    overall_risk = round(df['risk_score'].mean() * 100,1)
    # Group devices by name for the doughnut chart
    device_counts = df.groupby('device_name').size().to_dict()

    return jsonify({
        "total_devices": total_devices,
        "total_anomalies": total_anomalies,
        "average_usage": f"{avg_usage} KB/s",
        "device_counts": device_counts,
        "overall_risk_pct": overall_risk
    })


@app.route("/api/take_action",methods=['POST'])
def take_action():
    """
    NEW API: Simulates taking a remediation action (Block, Isolate, etc.).
    Triggers a notification for the user.
    """
    data = request.get_json()
    action = data.get('action')
    device_mac = data.get('device_mac')
    device_name = data.get('device_name','Unknown Device')

    if not action or not device_mac:
        return jsonify({"status": "error","message": "Missing action or device MAC"}),400

    # --- Simulated Action Logic ---
    log_message = f"🛡️ ACTION TAKEN: {action} applied to {device_name} ({device_mac})."

    # Send confirmation alert to user's Telegram
    send_alert(log_message)

    return jsonify({"status": "success","message": f"{action} simulated successfully for {device_name}"})


if __name__ == "__main__":
    app.run(debug=True,port=5000)