from datetime import datetime, timedelta
from typing import List, Dict, Any

class ExecutionEngine:
    def __init__(self) -> None:
        pass

    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sorts tasks based on Phase 2 algorithm:
        1. Incomplete First
        2. Priority (High > Medium > Low)
        3. Duration (Short > Long)
        """
        priority_map: Dict[str, int] = {"High": 1, "Medium": 2, "Low": 3}
        
        def get_duration(t: Dict[str, Any]) -> int:
            """Helper to safely get duration (default to 60 if None/0)."""
            return t.get("duration") if t.get("duration") else 60

        return sorted(tasks, key=lambda x: (
            x.get("completed", False), # Incomplete (False) < Complete (True)
            priority_map.get(x.get("priority", "Low"), 3),
            get_duration(x)
        ))

    def calculate_capacity(self, tasks: List[Dict[str, Any]]) -> int:
        """
        Returns total minutes planned for incomplete tasks.
        """
        total_mins: int = 0
        for task in tasks:
            if not task.get("completed"):
                 total_mins += task.get("duration") if task.get("duration") else 0
        return total_mins
