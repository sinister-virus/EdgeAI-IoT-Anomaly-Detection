"""
Main Application Entry Point for IoT Security System
Modular Python-based IoT security system with:
- Flask web server for SOC Dashboard
- Isolation Forest model for anomaly detection
- SQLite data handler
- Pandas-based vectorized feature engineering
"""
import sys
import argparse
from src.dashboard import run_dashboard
from src.data_handler import DataHandler
from src.anomaly_detector import AnomalyDetector
from src.feature_engineer import FeatureEngineer
from src.sample_data_generator import populate_database
import config


def setup_system():
    """Initialize the system components"""
    print("=" * 60)
    print("IoT Security System - Initialization")
    print("=" * 60)
    
    # Initialize data handler (creates database if not exists)
    print("\n1. Initializing database...")
    data_handler = DataHandler()
    print("   ✓ Database initialized")
    
    # Initialize feature engineer
    print("\n2. Initializing feature engineer...")
    feature_engineer = FeatureEngineer()
    print("   ✓ Feature engineer initialized")
    
    # Initialize anomaly detector
    print("\n3. Initializing anomaly detector...")
    anomaly_detector = AnomalyDetector()
    print(f"   ✓ Anomaly detector initialized")
    print(f"   - Algorithm: Isolation Forest")
    print(f"   - Contamination: {config.CONTAMINATION}")
    print(f"   - N Estimators: {config.N_ESTIMATORS}")
    
    print("\n✓ System initialization complete!")
    print("=" * 60)
    
    return data_handler, feature_engineer, anomaly_detector


def show_statistics(data_handler):
    """Display current system statistics"""
    stats = data_handler.get_statistics()
    
    print("\nCurrent System Statistics:")
    print("-" * 40)
    print(f"Total Logs:       {stats['total_logs']}")
    print(f"Total Anomalies:  {stats['total_anomalies']}")
    print(f"Recent Logs (1h): {stats['recent_logs']}")
    print(f"Anomaly Rate:     {stats['anomaly_rate']:.2f}%")
    print("-" * 40)


def train_model_cli(data_handler, feature_engineer, anomaly_detector, limit=10000):
    """Train the anomaly detection model via CLI"""
    print(f"\nTraining model with up to {limit} samples...")
    
    # Get training data
    df = data_handler.get_recent_logs(limit=limit)
    
    if df.empty:
        print("   ✗ No data available for training")
        return False
    
    print(f"   - Loaded {len(df)} samples")
    
    # Engineer features
    print("   - Engineering features...")
    features_df = feature_engineer.engineer_features(df)
    X = feature_engineer.get_feature_vector(features_df)
    
    if X.shape[0] < 10:
        print(f"   ✗ Insufficient data for training (got {X.shape[0]}, need at least 10)")
        return False
    
    print(f"   - Feature matrix shape: {X.shape}")
    
    # Train model
    print("   - Training Isolation Forest model...")
    anomaly_detector.train(X)
    
    print("   ✓ Model trained successfully!")
    print(f"   - Features used: {X.shape[1]}")
    
    return True


def analyze_data_cli(data_handler, feature_engineer, anomaly_detector, limit=1000):
    """Analyze data and detect anomalies via CLI"""
    print(f"\nAnalyzing {limit} recent logs...")
    
    # Get data
    df = data_handler.get_recent_logs(limit=limit)
    
    if df.empty:
        print("   ✗ No data available for analysis")
        return
    
    print(f"   - Loaded {len(df)} samples")
    
    # Engineer features
    print("   - Engineering features...")
    features_df = feature_engineer.engineer_features(df)
    X = feature_engineer.get_feature_vector(features_df)
    
    if not anomaly_detector.is_trained:
        print("   - Model not trained, training now...")
        if not train_model_cli(data_handler, feature_engineer, anomaly_detector):
            return
    
    # Detect anomalies
    print("   - Detecting anomalies...")
    predictions, scores = anomaly_detector.detect_anomalies(X)
    
    # Update database
    print("   - Updating database...")
    for idx, (pred, score) in enumerate(zip(predictions, scores)):
        log_id = features_df.iloc[idx]['id']
        is_anomaly = pred == -1
        data_handler.update_anomaly_status(log_id, is_anomaly, float(score))
    
    # Display results
    analysis = anomaly_detector.analyze_results(predictions, scores)
    
    print("\n   Analysis Results:")
    print("   " + "-" * 36)
    print(f"   Total Samples:      {analysis['total_samples']}")
    print(f"   Anomalies Detected: {analysis['anomalies_detected']}")
    print(f"   Anomaly Rate:       {analysis['anomaly_rate']:.2f}%")
    print(f"   Mean Score:         {analysis['mean_score']:.4f}")
    print("   " + "-" * 36)
    
    print("\n   ✓ Analysis complete!")


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='IoT Security System - Edge AI Anomaly Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Setup and show statistics
  python main.py --dashboard              # Run SOC dashboard
  python main.py --generate 2000          # Generate 2000 sample logs
  python main.py --train                  # Train the model
  python main.py --analyze                # Analyze recent data
  python main.py --generate 1000 --train --dashboard  # Full setup
        """
    )
    
    parser.add_argument('--dashboard', action='store_true',
                        help='Run the Flask SOC dashboard')
    parser.add_argument('--generate', type=int, metavar='N',
                        help='Generate N sample network logs')
    parser.add_argument('--train', action='store_true',
                        help='Train the anomaly detection model')
    parser.add_argument('--analyze', action='store_true',
                        help='Analyze recent data for anomalies')
    parser.add_argument('--port', type=int, default=config.FLASK_PORT,
                        help=f'Port for Flask dashboard (default: {config.FLASK_PORT})')
    parser.add_argument('--host', type=str, default=config.FLASK_HOST,
                        help=f'Host for Flask dashboard (default: {config.FLASK_HOST})')
    
    args = parser.parse_args()
    
    # Setup system
    data_handler, feature_engineer, anomaly_detector = setup_system()
    
    # Generate sample data if requested
    if args.generate:
        print(f"\nGenerating {args.generate} sample logs...")
        populate_database(num_samples=args.generate, anomaly_ratio=0.1)
    
    # Show statistics
    show_statistics(data_handler)
    
    # Train model if requested
    if args.train:
        train_model_cli(data_handler, feature_engineer, anomaly_detector)
    
    # Analyze data if requested
    if args.analyze:
        analyze_data_cli(data_handler, feature_engineer, anomaly_detector)
    
    # Run dashboard if requested
    if args.dashboard:
        print(f"\n{'=' * 60}")
        print("Starting SOC Dashboard...")
        print(f"Dashboard will be available at: http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop")
        print(f"{'=' * 60}\n")
        
        run_dashboard(host=args.host, port=args.port, debug=config.FLASK_DEBUG)
    elif not args.generate and not args.train and not args.analyze:
        # No action specified, show help
        print("\nNo action specified. Use --dashboard to run the web interface.")
        print("Run 'python main.py --help' for all options.")


if __name__ == '__main__':
    main()
