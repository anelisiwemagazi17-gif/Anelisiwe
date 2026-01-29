"""
Dashboard Database Manager for SOR Automation System
Handles all dashboard-specific database operations
"""
from typing import Dict, List, Optional
import pymysql
from datetime import datetime, timedelta
from .config import config

class DashboardDB:
    """Manages dashboard database operations"""

    def __init__(self):
        self.config = {
            "host": config.DB_HOST,
            "user": config.DB_USER,
            "password": config.DB_PASSWORD,
            "database": config.DB_NAME,
            "port": config.DB_PORT,
            "cursorclass": pymysql.cursors.DictCursor
        }

    def get_connection(self):
        """Get database connection"""
        return pymysql.connect(**self.config)

    # ===== SOR Request Management =====

    def create_sor_request(self, learner_id: int, learner_name: str, learner_email: str, overall_score: float = None) -> Optional[int]:
        """Create a new SOR request"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                sql = """INSERT INTO sor_requests
                        (learner_id, learner_name, learner_email, status, overall_score)
                        VALUES (%s, %s, %s, 'pending', %s)"""
                cur.execute(sql, (learner_id, learner_name, learner_email, overall_score))
                conn.commit()
                return cur.lastrowid
        except Exception as e:
            print(f"❌ Error creating SOR request: {e}")
            return None
        finally:
            conn.close()

    def update_sor_request(self, sor_id: int, updates: Dict) -> bool:
        """Update SOR request with any fields"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
                sql = f"UPDATE sor_requests SET {set_clause} WHERE id = %s"
                values = list(updates.values()) + [sor_id]
                cur.execute(sql, values)
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Error updating SOR request: {e}")
            return False
        finally:
            conn.close()

    def get_sor_request(self, sor_id: int) -> Optional[Dict]:
        """Get single SOR request by ID"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM sor_requests WHERE id = %s", (sor_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"❌ Error fetching SOR request: {e}")
            return None
        finally:
            conn.close()

    def get_all_sor_requests(self, status: str = None, limit: int = 100) -> List[Dict]:
        """Get all SOR requests with optional status filter, sorted by last updated"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                if status:
                    sql = "SELECT * FROM sor_requests WHERE status = %s ORDER BY updated_at DESC, created_at DESC LIMIT %s"
                    cur.execute(sql, (status, limit))
                else:
                    sql = "SELECT * FROM sor_requests ORDER BY updated_at DESC, created_at DESC LIMIT %s"
                    cur.execute(sql, (limit,))
                return cur.fetchall()
        except Exception as e:
            print(f"❌ Error fetching SOR requests: {e}")
            return []
        finally:
            conn.close()

    def search_sor_requests(self, search_term: str) -> List[Dict]:
        """Search SOR requests by learner name or email"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                sql = """SELECT * FROM sor_requests
                        WHERE learner_name LIKE %s OR learner_email LIKE %s
                        ORDER BY created_at DESC LIMIT 100"""
                term = f"%{search_term}%"
                cur.execute(sql, (term, term))
                return cur.fetchall()
        except Exception as e:
            print(f"❌ Error searching SOR requests: {e}")
            return []
        finally:
            conn.close()

    # ===== Dashboard Statistics =====

    def get_dashboard_stats(self) -> Dict:
        """Get dashboard overview statistics"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                stats = {}

                # Total SORs
                cur.execute("SELECT COUNT(*) as total FROM sor_requests")
                stats['total'] = cur.fetchone()['total']

                # By status
                cur.execute("""SELECT status, COUNT(*) as count
                              FROM sor_requests
                              GROUP BY status""")
                status_counts = {row['status']: row['count'] for row in cur.fetchall()}

                stats['pending'] = status_counts.get('pending', 0)
                stats['signature_sent'] = status_counts.get('signature_sent', 0)
                # Combine pdf_generated and signed counts into the 'signed' card
                stats['signed'] = status_counts.get('pdf_generated', 0) + status_counts.get('signed', 0)
                stats['uploaded'] = status_counts.get('uploaded', 0)
                stats['failed'] = status_counts.get('failed', 0)

                # Overdue (signature sent > 7 days ago, not signed)
                cur.execute("""SELECT COUNT(*) as count FROM sor_requests
                              WHERE status = 'signature_sent'
                              AND signature_sent_at < DATE_SUB(NOW(), INTERVAL 7 DAY)""")
                stats['overdue'] = cur.fetchone()['count']

                # Recent activity (last 24 hours)
                cur.execute("""SELECT COUNT(*) as count FROM sor_requests
                              WHERE created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)""")
                stats['recent_24h'] = cur.fetchone()['count']

                return stats
        except Exception as e:
            print(f"❌ Error fetching dashboard stats: {e}")
            return {'total': 0, 'pending': 0, 'signed': 0, 'failed': 0, 'overdue': 0}
        finally:
            conn.close()

    # ===== Audit Logging =====

    def log_action(self, sor_id: int, action: str, details: str = None, status: str = 'success', user: str = 'system') -> bool:
        """Log an action to audit trail"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                sql = """INSERT INTO sor_audit_log
                        (sor_request_id, action, details, status, user)
                        VALUES (%s, %s, %s, %s, %s)"""
                cur.execute(sql, (sor_id, action, details, status, user))
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Error logging action: {e}")
            return False
        finally:
            conn.close()

    def get_audit_log(self, sor_id: int = None, limit: int = 100) -> List[Dict]:
        """Get audit log, optionally filtered by SOR request ID"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                if sor_id:
                    sql = """SELECT * FROM sor_audit_log
                            WHERE sor_request_id = %s
                            ORDER BY created_at DESC LIMIT %s"""
                    cur.execute(sql, (sor_id, limit))
                else:
                    sql = "SELECT * FROM sor_audit_log ORDER BY created_at DESC LIMIT %s"
                    cur.execute(sql, (limit,))
                return cur.fetchall()
        except Exception as e:
            print(f"❌ Error fetching audit log: {e}")
            return []
        finally:
            conn.close()

    # ===== Settings Management =====

    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT setting_value FROM sor_settings WHERE setting_key = %s", (key,))
                result = cur.fetchone()
                return result['setting_value'] if result else None
        except Exception as e:
            print(f"❌ Error fetching setting: {e}")
            return None
        finally:
            conn.close()

    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                sql = """INSERT INTO sor_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE setting_value = %s"""
                cur.execute(sql, (key, value, value))
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Error setting value: {e}")
            return False
        finally:
            conn.close()

# Create dashboard database instance
dashboard_db = DashboardDB()
