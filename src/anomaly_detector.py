"""
Anomaly Detection Module for IoT Security System
Uses Isolation Forest for detecting anomalies in network traffic
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Tuple, List, Dict
import pickle
import os
import config


class AnomalyDetector:
    """Handles anomaly detection using Isolation Forest"""
    
    def __init__(
        self, 
        contamination: float = config.CONTAMINATION,
        n_estimators: int = config.N_ESTIMATORS,
        random_state: int = config.RANDOM_STATE
    ):
        """
        Initialize the anomaly detector
        
        Args:
            contamination: Expected proportion of outliers in the dataset
            n_estimators: Number of base estimators (trees) in the ensemble
            random_state: Random state for reproducibility
        """
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = None
        self.is_trained = False
        self._init_model()
    
    def _init_model(self):
        """Initialize the Isolation Forest model"""
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1,  # Use all available cores
            verbose=0
        )
    
    def train(self, X: np.ndarray) -> 'AnomalyDetector':
        """
        Train the Isolation Forest model
        
        Args:
            X: Feature matrix (n_samples, n_features)
            
        Returns:
            Self for method chaining
        """
        if X.shape[0] == 0:
            raise ValueError("Cannot train on empty dataset")
        
        # Fit the model
        self.model.fit(X)
        self.is_trained = True
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomalies
        
        Args:
            X: Feature matrix (n_samples, n_features)
            
        Returns:
            Array of predictions (1 for normal, -1 for anomaly)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        if X.shape[0] == 0:
            return np.array([])
        
        # Predict (-1 for anomalies, 1 for normal points)
        predictions = self.model.predict(X)
        
        return predictions
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """
        Compute anomaly scores for samples
        
        Args:
            X: Feature matrix (n_samples, n_features)
            
        Returns:
            Array of anomaly scores (lower scores indicate anomalies)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before scoring")
        
        if X.shape[0] == 0:
            return np.array([])
        
        # Score samples (negative scores indicate anomalies)
        scores = self.model.score_samples(X)
        
        return scores
    
    def detect_anomalies(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies and return predictions with scores
        
        Args:
            X: Feature matrix (n_samples, n_features)
            
        Returns:
            Tuple of (predictions, scores)
            predictions: 1 for normal, -1 for anomaly
            scores: Anomaly scores (lower = more anomalous)
        """
        predictions = self.predict(X)
        scores = self.score_samples(X)
        
        return predictions, scores
    
    def get_anomaly_indices(self, predictions: np.ndarray) -> np.ndarray:
        """
        Get indices of detected anomalies
        
        Args:
            predictions: Array of predictions (-1 for anomaly, 1 for normal)
            
        Returns:
            Array of indices where anomalies were detected
        """
        return np.where(predictions == -1)[0]
    
    def analyze_results(self, predictions: np.ndarray, scores: np.ndarray) -> Dict:
        """
        Analyze detection results
        
        Args:
            predictions: Array of predictions
            scores: Array of anomaly scores
            
        Returns:
            Dictionary containing analysis results
        """
        anomaly_indices = self.get_anomaly_indices(predictions)
        n_anomalies = len(anomaly_indices)
        n_total = len(predictions)
        
        return {
            'total_samples': n_total,
            'anomalies_detected': n_anomalies,
            'anomaly_rate': (n_anomalies / n_total * 100) if n_total > 0 else 0,
            'mean_score': float(np.mean(scores)) if len(scores) > 0 else 0,
            'min_score': float(np.min(scores)) if len(scores) > 0 else 0,
            'max_score': float(np.max(scores)) if len(scores) > 0 else 0,
            'anomaly_indices': anomaly_indices.tolist()
        }
    
    def save_model(self, filepath: str):
        """
        Save the trained model to disk
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'contamination': self.contamination,
            'n_estimators': self.n_estimators,
            'random_state': self.random_state,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str):
        """
        Load a trained model from disk
        
        Args:
            filepath: Path to the saved model
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.contamination = model_data['contamination']
        self.n_estimators = model_data['n_estimators']
        self.random_state = model_data['random_state']
        self.is_trained = model_data['is_trained']
    
    def get_model_info(self) -> Dict:
        """
        Get information about the model
        
        Returns:
            Dictionary containing model information
        """
        return {
            'algorithm': 'Isolation Forest',
            'contamination': self.contamination,
            'n_estimators': self.n_estimators,
            'random_state': self.random_state,
            'is_trained': self.is_trained,
            'n_features': self.model.n_features_in_ if self.is_trained else None
        }
