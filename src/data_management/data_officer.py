# src/data_management/data_officer.py
import os
import json
from datetime import datetime
from typing import Dict
from src.utils.logger import log_experiment, ActionType


class TelemetryValidationError(Exception):
    pass

class DataOfficer:

    def __init__(self, model_used: str = "gemini-2.5-flash"):
        self.log_file = "logs/experiment_data.json"
        self.model_used = model_used

    def _validate_entry(self, entry: Dict) -> None:

        required_fields = [
            "id",
            "timestamp",
            "agent",
            "model",
            "action",
            "details",
            "status",
        ]

        for field in required_fields:
            if field not in entry:
                raise TelemetryValidationError(
                    f"Missing required field: {field}"
                )

        try:
            datetime.fromisoformat(entry["timestamp"])
        except (ValueError, TypeError):
            raise TelemetryValidationError("Invalid timestamp format")

        # Details validation
        details = entry.get("details", {})
        for key in ("input_prompt", "output_response"):
            if key not in details:
                raise TelemetryValidationError(
                    f"Missing details field: {key}"
                )


    def validate_logs(self) -> None:

        if not os.path.exists(self.log_file):
            raise TelemetryValidationError(
                "Telemetry file logs/experiment_data.json is missing"
            )

        try:
            with open(self.log_file) as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise TelemetryValidationError(
                "Telemetry file contains invalid JSON"
            )

        if not isinstance(data, list):
            raise TelemetryValidationError(
                "Telemetry file must contain a list of entries"
            )

        for index, entry in enumerate(data):
            try:
                self._validate_entry(entry)
            except TelemetryValidationError as e:
                raise TelemetryValidationError(
                    f"Invalid entry at index {index}: {e}"
                )

    def force_log(
        self,
        agent_name: str,
        action_type: ActionType,
        details: Dict,
        status: str = "SUCCESS",
    ) -> None:

        details.setdefault("input_prompt", "N/A")
        details.setdefault("output_response", "N/A")

        log_experiment(
            agent_name=agent_name,
            model_used=self.model_used,
            action=action_type,
            details=details,
            status=status,
        )