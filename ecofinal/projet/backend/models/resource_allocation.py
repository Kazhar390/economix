from typing import List, Dict
import numpy as np

def resource_leveling(tasks: List[Dict], available_resources: int) -> Dict:
    """
    Basic resource leveling algorithm
    Each task should have:
    - id: Task identifier
    - duration: Duration in days
    - resources: Resources needed per day
    - predecessors: List of task ids that must be completed first
    """
    if not tasks:
        return {}
    
    # Initialize
    schedule = []
    current_time = 0
    resource_usage = []
    
    # Sort tasks based on dependencies (simple implementation)
    scheduled_ids = set()
    while len(scheduled_ids) < len(tasks):
        for task in tasks:
            if task['id'] in scheduled_ids:
                continue
                
            # Check if all predecessors are scheduled
            pred_met = all(pred in scheduled_ids for pred in task.get('predecessors', []))
            
            if pred_met:
                # Find earliest available time
                start_time = current_time
                end_time = start_time + task['duration']
                
                # Check resource constraints
                for t in range(start_time, end_time):
                    daily_usage = sum(
                        t >= task_start and t < task_start + task_duration
                        for (task_start, task_duration, task_resources) in resource_usage
                    )
                    
                    if daily_usage + task['resources'] > available_resources:
                        start_time += 1
                        end_time += 1
                        break
                
                schedule.append({
                    'id': task['id'],
                    'start': start_time,
                    'end': end_time,
                    'resources': task['resources']
                })
                
                resource_usage.append((start_time, task['duration'], task['resources']))
                scheduled_ids.add(task['id'])
                current_time = max(current_time, end_time)
    
    # Calculate metrics
    total_duration = max(task['end'] for task in schedule) if schedule else 0
    daily_load = np.zeros(total_duration)
    
    for task in schedule:
        daily_load[task['start']:task['end']] += task['resources']
    
    return {
        'schedule': schedule,
        'total_duration': total_duration,
        'resource_utilization': {
            'average': np.mean(daily_load),
            'max': np.max(daily_load),
            'min': np.min(daily_load),
            'underutilization': sum(daily_load < available_resources * 0.7) / len(daily_load)
        }
    }