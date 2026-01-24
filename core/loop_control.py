# core/loop_control.py
from .state import SystemState
import logging

logger = logging.getLogger(__name__)

class RefactoringOrchestrator:
    """Controls the flow between agents."""
    
    def __init__(self, state: SystemState):
        self.state = state
    
    def run_cycle(self):
        """Execute one complete ANALYZE → FIX → VERIFY cycle."""
        
        # PHASE 1: ANALYSIS (Auditor)
        if not self.state.analysis_report:
            logger.info(f"[Iteration {self.state.current_iteration}] Phase 1: Analysis")
            # TODO: Call Auditor agent here
            self.state.last_agent = "auditor"
            
            # For now, simulate agent output
            self.state.analysis_report = {"issues": ["TODO: Implement auditor"]}
            self.state.refactoring_plan = "TODO: Implement auditor to generate plan"
        
        # PHASE 2: FIXING (Fixer)
        elif not self.state.test_results:
            logger.info(f"[Iteration {self.state.current_iteration}] Phase 2: Fixing")
            # TODO: Call Fixer agent here
            self.state.last_agent = "fixer"
            
            # For now, simulate
            self.state.test_results = {"status": "pending"}
        
        # PHASE 3: VERIFICATION (Judge)
        else:
            logger.info(f"[Iteration {self.state.current_iteration}] Phase 3: Verification")
            # TODO: Call Judge agent here
            self.state.last_agent = "judge"
            
            # Simulate test execution
            # In real system, this would come from pytest
            test_passed = False  # Change this when Judge is implemented
            
            if test_passed:
                self.state.success = True
                self.state.is_complete = True
                logger.info("✓ All tests passed!")
            else:
                # Tests failed, prepare for retry
                self.state.error_logs.append(f"Iteration {self.state.current_iteration}: Tests failed")
                self.state.test_results = None  # Reset for next cycle
                self.state.increment_iteration()
                
                if not self.state.should_continue():
                    self.state.is_complete = True
                    logger.error("✗ Max iterations reached without success")
    
    def run_full_loop(self):
        """Run the system until completion or max iterations."""
        logger.info(f"Starting Refactoring Swarm on: {self.state.target_dir}")
        
        while self.state.should_continue():
            self.run_cycle()
        
        # Final status
        if self.state.success:
            logger.info("🎉 MISSION SUCCESS: Code refactored and tests passing")
        else:
            logger.error(f"💥 MISSION FAILED: {len(self.state.error_logs)} errors")
        
        return self.state