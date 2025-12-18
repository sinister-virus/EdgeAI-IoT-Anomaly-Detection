"""
Flask Dashboard for IoT Security System SOC (Security Operations Center)
Provides web interface for monitoring and analysis
"""
from flask import Flask, render_template, jsonify, request
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_handler import DataHandler
from src.anomaly_detector import AnomalyDetector
from src.feature_engineer import FeatureEngineer
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iot-security-system-secret-key'

# Initialize components
data_handler = DataHandler()
anomaly_detector = AnomalyDetector()
feature_engineer = FeatureEngineer()


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/statistics')
def get_statistics():
    """Get system statistics"""
    try:
        stats = data_handler.get_statistics()
        model_info = anomaly_detector.get_model_info()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'model_info': model_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recent-logs')
def get_recent_logs():
    """Get recent network logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        df = data_handler.get_recent_logs(limit=limit)
        
        # Convert to JSON-friendly format
        logs = df.to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'logs': logs,
            'count': len(logs)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/anomalies')
def get_anomalies():
    """Get detected anomalies"""
    try:
        limit = request.args.get('limit', 50, type=int)
        df = data_handler.get_anomalies(limit=limit)
        
        # Convert to JSON-friendly format
        anomalies = df.to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'anomalies': anomalies,
            'count': len(anomalies)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_logs():
    """Analyze logs and detect anomalies"""
    try:
        # Get recent logs
        limit = request.json.get('limit', 1000) if request.json else 1000
        df = data_handler.get_recent_logs(limit=limit)
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No logs available for analysis'
            }), 400
        
        # Engineer features
        features_df = feature_engineer.engineer_features(df)
        X = feature_engineer.get_feature_vector(features_df)
        
        if X.shape[0] == 0:
            return jsonify({
                'success': False,
                'error': 'Failed to extract features'
            }), 400
        
        # Train or retrain model if not trained
        if not anomaly_detector.is_trained:
            anomaly_detector.train(X)
        
        # Detect anomalies
        predictions, scores = anomaly_detector.detect_anomalies(X)
        
        # Update database with results
        for idx, (pred, score) in enumerate(zip(predictions, scores)):
            log_id = features_df.iloc[idx]['id']
            is_anomaly = pred == -1
            data_handler.update_anomaly_status(log_id, is_anomaly, float(score))
        
        # Get analysis results
        analysis = anomaly_detector.analyze_results(predictions, scores)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/train-model', methods=['POST'])
def train_model():
    """Train the anomaly detection model"""
    try:
        # Get training data
        limit = request.json.get('limit', 10000) if request.json else 10000
        df = data_handler.get_recent_logs(limit=limit)
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No data available for training'
            }), 400
        
        # Engineer features
        features_df = feature_engineer.engineer_features(df)
        X = feature_engineer.get_feature_vector(features_df)
        
        if X.shape[0] < 10:
            return jsonify({
                'success': False,
                'error': 'Insufficient data for training (minimum 10 samples required)'
            }), 400
        
        # Train model
        anomaly_detector.train(X)
        
        model_info = anomaly_detector.get_model_info()
        
        return jsonify({
            'success': True,
            'message': 'Model trained successfully',
            'model_info': model_info,
            'training_samples': X.shape[0]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'IoT Security System SOC Dashboard'
    })


def run_dashboard(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG):
    """
    Run the Flask dashboard
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard()
