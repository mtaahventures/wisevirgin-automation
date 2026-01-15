"""
ENGINE 4.2: Schedule Optimizer
Determines optimal publish time for US audience (modular/reusable)
"""
from datetime import datetime, timedelta

class ScheduleOptimizer:
    def __init__(self):
        # Best times for Personal Finance audience (US EST)
        self.optimal_hours = [18, 19, 20]  # 6-8 PM EST
        self.optimal_days = [1, 2, 3, 4]  # Mon-Thu (weekdays)
    
    def get_optimal_publish_time(self):
        """Get next optimal publish time"""
        now = datetime.now()
        
        # If it's already past optimal time today, schedule for tomorrow
        if now.hour >= max(self.optimal_hours):
            target_date = now + timedelta(days=1)
        else:
            target_date = now
        
        # Set to 6 PM (18:00) as default optimal time
        publish_time = target_date.replace(hour=18, minute=0, second=0, microsecond=0)
        
        return publish_time

if __name__ == '__main__':
    optimizer = ScheduleOptimizer()
    time = optimizer.get_optimal_publish_time()
    print(f"Optimal publish time: {time}")
