import schedule
import time
import threading
from datetime import datetime
from .views import mark_absentees 

def start_scheduler():
    """Start background thread to mark absentees daily at 17:35."""
    def job():
        print(f"Triggering absentee auto-mark at {datetime.now()}")
        mark_absentees()

    schedule.every().day.at("17:35").do(job)

    def run_continuously():
        while True:
            schedule.run_pending()
            time.sleep(60)

    t = threading.Thread(target=run_continuously, daemon=True)
    t.start()
