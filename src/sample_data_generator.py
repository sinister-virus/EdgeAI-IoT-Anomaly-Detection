"""
Sample Data Generator for IoT Security System
Generates synthetic network log data for testing
"""
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_handler import DataHandler


class DataGenerator:
    """Generates synthetic network log data"""
    
    DEVICES = ['camera_01', 'camera_02', 'thermostat_01', 'doorlock_01', 'light_01', 'sensor_01']
    PROTOCOLS = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS']
    COMMON_PORTS = [80, 443, 22, 21, 25, 53, 3306, 5432, 8080, 8443]
    
    def __init__(self):
        self.base_time = datetime.now().timestamp()
    
    def generate_normal_log(self, timestamp: float = None) -> Dict:
        """Generate a normal network log entry"""
        if timestamp is None:
            timestamp = self.base_time
        
        return {
            'timestamp': timestamp,
            'device_id': random.choice(self.DEVICES),
            'source_ip': f'192.168.1.{random.randint(10, 50)}',
            'destination_ip': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
            'port': random.choice(self.COMMON_PORTS),
            'protocol': random.choice(self.PROTOCOLS),
            'bytes_sent': random.randint(100, 5000),
            'bytes_received': random.randint(100, 5000)
        }
    
    def generate_anomalous_log(self, timestamp: float = None) -> Dict:
        """Generate an anomalous network log entry"""
        if timestamp is None:
            timestamp = self.base_time
        
        # Anomalies: unusual ports, high traffic, suspicious IPs
        anomaly_type = random.choice(['unusual_port', 'high_traffic', 'suspicious_ip', 'rapid_requests'])
        
        if anomaly_type == 'unusual_port':
            return {
                'timestamp': timestamp,
                'device_id': random.choice(self.DEVICES),
                'source_ip': f'192.168.1.{random.randint(10, 50)}',
                'destination_ip': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'port': random.randint(30000, 65535),  # Unusual high port
                'protocol': random.choice(self.PROTOCOLS),
                'bytes_sent': random.randint(100, 5000),
                'bytes_received': random.randint(100, 5000)
            }
        
        elif anomaly_type == 'high_traffic':
            return {
                'timestamp': timestamp,
                'device_id': random.choice(self.DEVICES),
                'source_ip': f'192.168.1.{random.randint(10, 50)}',
                'destination_ip': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'port': random.choice(self.COMMON_PORTS),
                'protocol': random.choice(self.PROTOCOLS),
                'bytes_sent': random.randint(50000, 100000),  # High traffic
                'bytes_received': random.randint(50000, 100000)
            }
        
        elif anomaly_type == 'suspicious_ip':
            return {
                'timestamp': timestamp,
                'device_id': random.choice(self.DEVICES),
                'source_ip': f'192.168.1.{random.randint(10, 50)}',
                'destination_ip': f'{random.choice([1, 2, 3, 10])}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',  # Suspicious external IP
                'port': random.choice(self.COMMON_PORTS),
                'protocol': random.choice(self.PROTOCOLS),
                'bytes_sent': random.randint(100, 5000),
                'bytes_received': random.randint(100, 5000)
            }
        
        else:  # rapid_requests
            return {
                'timestamp': timestamp,
                'device_id': random.choice(self.DEVICES),
                'source_ip': f'192.168.1.{random.randint(10, 50)}',
                'destination_ip': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'port': random.choice(self.COMMON_PORTS),
                'protocol': random.choice(self.PROTOCOLS),
                'bytes_sent': random.randint(50, 200),  # Small packets
                'bytes_received': random.randint(50, 200)
            }
    
    def generate_dataset(self, num_samples: int = 1000, anomaly_ratio: float = 0.1) -> List[Dict]:
        """
        Generate a dataset with normal and anomalous logs
        
        Args:
            num_samples: Total number of samples to generate
            anomaly_ratio: Ratio of anomalies in the dataset
            
        Returns:
            List of log dictionaries
        """
        num_anomalies = int(num_samples * anomaly_ratio)
        num_normal = num_samples - num_anomalies
        
        logs = []
        current_time = self.base_time
        
        # Generate normal logs
        for _ in range(num_normal):
            logs.append(self.generate_normal_log(current_time))
            current_time += random.uniform(0.1, 5.0)  # Random time delta
        
        # Generate anomalous logs
        for _ in range(num_anomalies):
            logs.append(self.generate_anomalous_log(current_time))
            current_time += random.uniform(0.1, 5.0)
        
        # Shuffle logs to mix normal and anomalous
        random.shuffle(logs)
        
        # Re-sort by timestamp to maintain temporal order
        logs.sort(key=lambda x: x['timestamp'])
        
        return logs


def populate_database(num_samples: int = 1000, anomaly_ratio: float = 0.1):
    """
    Populate the database with sample data
    
    Args:
        num_samples: Number of samples to generate
        anomaly_ratio: Ratio of anomalies
    """
    print(f"Generating {num_samples} network log samples...")
    
    generator = DataGenerator()
    logs = generator.generate_dataset(num_samples, anomaly_ratio)
    
    print(f"Inserting logs into database...")
    data_handler = DataHandler()
    count = data_handler.insert_logs_batch(logs)
    
    print(f"✓ Successfully inserted {count} logs into the database")
    print(f"  - Normal logs: ~{num_samples - int(num_samples * anomaly_ratio)}")
    print(f"  - Anomalous logs: ~{int(num_samples * anomaly_ratio)}")
    
    stats = data_handler.get_statistics()
    print(f"\nDatabase Statistics:")
    print(f"  - Total logs: {stats['total_logs']}")
    print(f"  - Total anomalies: {stats['total_anomalies']}")
    print(f"  - Recent logs (1h): {stats['recent_logs']}")


if __name__ == '__main__':
    populate_database(num_samples=2000, anomaly_ratio=0.1)
