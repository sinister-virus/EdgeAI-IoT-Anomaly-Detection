"""
Data Handler Module for IoT Security System
Manages SQLite database operations for network logs
"""
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import config


class DataHandler:
    """Handles all database operations for network logs"""
    
    def __init__(self, db_path: str = config.DB_PATH):
        """
        Initialize the data handler
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create network logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                device_id TEXT NOT NULL,
                source_ip TEXT NOT NULL,
                destination_ip TEXT NOT NULL,
                port INTEGER NOT NULL,
                protocol TEXT NOT NULL,
                bytes_sent INTEGER NOT NULL,
                bytes_received INTEGER NOT NULL,
                is_anomaly INTEGER DEFAULT 0,
                anomaly_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index on timestamp for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON network_logs(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_log(self, log_data: Dict) -> int:
        """
        Insert a single network log entry
        
        Args:
            log_data: Dictionary containing log information
            
        Returns:
            ID of the inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO network_logs 
            (timestamp, device_id, source_ip, destination_ip, port, protocol, 
             bytes_sent, bytes_received, is_anomaly, anomaly_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_data.get('timestamp', datetime.now().timestamp()),
            log_data.get('device_id', 'unknown'),
            log_data.get('source_ip', '0.0.0.0'),
            log_data.get('destination_ip', '0.0.0.0'),
            log_data.get('port', 0),
            log_data.get('protocol', 'TCP'),
            log_data.get('bytes_sent', 0),
            log_data.get('bytes_received', 0),
            log_data.get('is_anomaly', 0),
            log_data.get('anomaly_score', 0.0)
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def insert_logs_batch(self, logs: List[Dict]) -> int:
        """
        Insert multiple network log entries
        
        Args:
            logs: List of log dictionaries
            
        Returns:
            Number of records inserted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = [
            (
                log.get('timestamp', datetime.now().timestamp()),
                log.get('device_id', 'unknown'),
                log.get('source_ip', '0.0.0.0'),
                log.get('destination_ip', '0.0.0.0'),
                log.get('port', 0),
                log.get('protocol', 'TCP'),
                log.get('bytes_sent', 0),
                log.get('bytes_received', 0),
                log.get('is_anomaly', 0),
                log.get('anomaly_score', 0.0)
            )
            for log in logs
        ]
        
        cursor.executemany('''
            INSERT INTO network_logs 
            (timestamp, device_id, source_ip, destination_ip, port, protocol, 
             bytes_sent, bytes_received, is_anomaly, anomaly_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    def get_recent_logs(self, limit: int = 100) -> pd.DataFrame:
        """
        Get recent network logs
        
        Args:
            limit: Maximum number of logs to retrieve
            
        Returns:
            DataFrame containing log data
        """
        conn = sqlite3.connect(self.db_path)
        query = f'''
            SELECT * FROM network_logs 
            ORDER BY timestamp DESC 
            LIMIT {limit}
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_logs_by_timerange(self, start_time: float, end_time: float) -> pd.DataFrame:
        """
        Get logs within a specific time range
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            DataFrame containing log data
        """
        conn = sqlite3.connect(self.db_path)
        query = '''
            SELECT * FROM network_logs 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        '''
        df = pd.read_sql_query(query, conn, params=(start_time, end_time))
        conn.close()
        
        return df
    
    def get_anomalies(self, limit: int = 50) -> pd.DataFrame:
        """
        Get detected anomalies
        
        Args:
            limit: Maximum number of anomalies to retrieve
            
        Returns:
            DataFrame containing anomaly data
        """
        conn = sqlite3.connect(self.db_path)
        query = f'''
            SELECT * FROM network_logs 
            WHERE is_anomaly = 1
            ORDER BY timestamp DESC 
            LIMIT {limit}
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def update_anomaly_status(self, log_id: int, is_anomaly: bool, anomaly_score: float):
        """
        Update anomaly status for a log entry
        
        Args:
            log_id: ID of the log entry
            is_anomaly: Whether the log is an anomaly
            anomaly_score: Anomaly score from the model
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE network_logs 
            SET is_anomaly = ?, anomaly_score = ?
            WHERE id = ?
        ''', (1 if is_anomaly else 0, anomaly_score, log_id))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dictionary containing statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total logs
        cursor.execute('SELECT COUNT(*) FROM network_logs')
        total_logs = cursor.fetchone()[0]
        
        # Total anomalies
        cursor.execute('SELECT COUNT(*) FROM network_logs WHERE is_anomaly = 1')
        total_anomalies = cursor.fetchone()[0]
        
        # Recent logs count (last hour)
        one_hour_ago = datetime.now().timestamp() - 3600
        cursor.execute('SELECT COUNT(*) FROM network_logs WHERE timestamp > ?', (one_hour_ago,))
        recent_logs = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_logs': total_logs,
            'total_anomalies': total_anomalies,
            'recent_logs': recent_logs,
            'anomaly_rate': (total_anomalies / total_logs * 100) if total_logs > 0 else 0
        }
