# src/orchestrator/orchestrator.py
from src.state.state import (
    SystemState, SystemPhase, ConstructionPhase, RepairPhase,
    FixerMode, TesterMode, Agent
)
from src.refactoring_agents.auditor_agent import AuditorAgent
from src.refactoring_agents.fixer_agent import FixerAgent
from src.refactoring_agents.tester_agent import TesterAgent

class RefactoringOrchestrator:
    def __init__(self, state : SystemState, auditor : AuditorAgent, fixer : FixerAgent, tester : TesterAgent):
        self.state = state
        self.auditor = auditor
        self.fixer = fixer
        self.tester = tester

    def run(self):
        # --------------------------------------------------
        #  Construction
        # --------------------------------------------------
        self.state.change_phase(SystemPhase.CONSTRUCTION_PHASE, ConstructionPhase.AUDITING, Agent.AUDITOR)
        if not self.auditor.run(self.state) :
            return False

        self.state.change_phase(SystemPhase.CONSTRUCTION_PHASE, ConstructionPhase.INITIAL_REPAIR, Agent.FIXER)
        self.state.fixer_state.set_mode(FixerMode.REFACTOR)
        if not self.fixer.run(self.state) :
            return False

        self.state.change_phase(SystemPhase.CONSTRUCTION_PHASE, ConstructionPhase.TEST_GENERATION, Agent.TESTER)
        self.state.tester_state.set_mode(TesterMode.GENERATE_TESTS)
        if not self.tester.generate_tests(self.state) :
            return False

        self.state.change_phase(SystemPhase.CONSTRUCTION_PHASE, ConstructionPhase.BOOTSTRAP_DONE, Agent.TESTER)

        # --------------------------------------------------
        #  Repair Loop
        # --------------------------------------------------
        self.state.change_phase(SystemPhase.REPAIR_PHASE, RepairPhase.FIXING, Agent.FIXER)

        mission_successful = False

        while self.state.current_iteration < self.state.max_iterations and not self.state.is_stopped :

            self.state.fixer_state.set_mode(FixerMode.HEAL)
            if not self.fixer.run(self.state) :
                return False

            self.state.change_phase(SystemPhase.REPAIR_PHASE, RepairPhase.TESTING_AND_JUDGING, Agent.TESTER)
            mission_successful = self.tester.test_and_judge(self.state)

            if mission_successful == 2:
                self.state.terminate(with_error=True)
            elif mission_successful :
                self.state.terminate(with_error=False)
                return True

            self.state.next_iteration()
            if self.state.current_iteration == self.state.max_iterations :
                self.state.terminate()

        return False
