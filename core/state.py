# core/state.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import os

@dataclass
class SystemState:
    """Shared state between all agents and the orchestrator."""
    
    # Required from CLI
    target_dir: str
    
    # Execution tracking
    current_iteration: int = 0
    max_iterations: int = 10
    
    # Agent outputs
    analysis_report: Optional[Dict] = None
    refactoring_plan: Optional[str] = None
    test_results: Optional[Dict] = None
    error_logs: List[str] = field(default_factory=list)
    
    # System flags
    is_complete: bool = False
    success: bool = False
    last_agent: str = ""  # "auditor", "fixer", "judge"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for logging."""
        return {
            "iteration": self.current_iteration,
            "target_dir": self.target_dir,
            "last_agent": self.last_agent,
            "is_complete": self.is_complete,
            "success": self.success,
            "has_analysis": self.analysis_report is not None,
            "has_plan": self.refactoring_plan is not None,
            "has_test_results": self.test_results is not None,
            "error_count": len(self.error_logs)
        }
    
    def increment_iteration(self):
        """Move to next iteration, check limits."""
        self.current_iteration += 1
        if self.current_iteration >= self.max_iterations:
            self.is_complete = True
            self.error_logs.append(f"Max iterations ({self.max_iterations}) reached")
    
    def should_continue(self) -> bool:
        """Determine if system should keep running."""
        if self.is_complete:
            return False
        if self.current_iteration >= self.max_iterations:
            return False
        return True