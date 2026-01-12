# src/agents/data_officer_agent.py

import os 
import json 
from datetime import datetime
from src.utils.logger import log_experiment , ActionType

class DataOfficerAgent:
    
    def __init__(self, agent_name="DataOfficerAgent" , model_used="gemini-2.5-flash"):
        self.agent_name = agent_name
        self.model_used = model_used
        self.log_file = "logs/experiment_data.json"

    def _validate_entry(self , entry : dict) -> bool:
        required_fields = ["id", "timestamp", "agent", "model", "action", "details", "status"]
        for field in required_fields:
            if field not in entry:
                return False
        # Validate timestamp format (ISO 8601)
        try:
            datetime.fromisoformat(entry["timestamp"])
        except (ValueError, TypeError):
            return False
        details_required = ["input_prompt", "output_response"]
        for key in details_required:
            if key not in entry.get("details",{}):
                return False 
        return True 
    
    def validate_logs(self) -> bool:
        if not os.path.exists(self.log_file):
            print(f"{self.log_file} missing")
            return False
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print("Invalid JSON format in log file")
            return False
        all_valid = True 
        for i , entry in enumerate(data):
            if not self._validate_entry(entry):
                print(f"Invalid entry at index {i}")
                all_valid = False

        if all_valid:
            print("All entries are valid")
            return True 
        else:
            print("Some entries are invalid")
            return False

    def force_log(self , action_type: ActionType , details : dict , status="SUCCESS"):
        if "input_prompt" not in details:
            details["input_prompt"] = "N/A"
        if "output_response" not in details:
            details["output_response"] = "N/A"
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_used,
            action=action_type,
            details=details,
            status=status
        )

    def generate_test_file(self, path="sandbox/test_edge_case.py", content=""):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        print(f"Test file created: {path}")    
        