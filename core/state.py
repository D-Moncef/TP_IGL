# core/state.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from typing import Union
import json

@dataclass
class AuditorError:
    stage: str        # at which stage the error occurred
    message: str                 # description of what went wrong
    file: Optional[str] = None   # file that caused the error, if any
    exception: Optional[str] = None   # exception string, if any

    def to_dict(self) -> Dict[str,Any]:
        return {
            "stage" : self.stage,
            "message" : self.message,
            "file" : self.file ,
            "exception" : self.exception ,
        }

@dataclass
class AuditorState:
    output: Optional[Dict[str, Any]] = None    # JSON output matching the schema defined in the prompt
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    has_run: bool = False                   # flag that auditor has run
    is_done: bool= False
    internal_errors: List[AuditorError] = field(default_factory=list)  # list of internal error that occurred in the auditor block

    def start_job(self):
        self.started_at = datetime.utcnow()
        self.has_run = True
        self.is_done = False

    def finish_job(self):
        self.finished_at = datetime.utcnow()
        self.is_done = True

    def get_started_at_str(self) -> Optional[str]:
        return self.started_at.isoformat() if self.started_at else None

    def get_finished_at_str(self) -> Optional[str]:
        return self.finished_at.isoformat() if self.finished_at else None

    def add_error(self, stage: str,message: str, file: Optional[str] = None, exception: Optional[Exception] = None):
        self.internal_errors.append(AuditorError(stage = stage, message = message, file = file, exception = str(exception) if exception else None))

    def to_dict(self) -> Dict[str,Any]:
        return {
            "output" : self.output ,
            "started_at" : self.get_started_at_str(),
            "finished_at": self.get_finished_at_str(),
            "has_run" : self.has_run,
            "is_done" : self.is_done,
            "internal_errors" : [error.to_dict() for error in self.internal_errors]
        }


@dataclass(frozen=True)
class FixerError:
    stage: str
    message: str
    file: Optional[str] = None
    exception: Optional[str] = None

    def to_dict(self) -> Dict[str,Any]:
        return {
            "stage" : self.stage,
            "message" : self.message,
            "file" : self.file,
            "exception" : self.exception,
        }

class FixerMode(str, Enum):
    REFACTOR = "REFACTOR"   # After Production of the refactoring plan by the auditor
    HEAL = "HEAL"           # After a failed iteration, we fix the code as instructed by the tester

@dataclass
class FixerState:
    mode: FixerMode                            # REFACTOR or HEAL
    output: Optional[Dict[str, Any]] = None    # JSON output from fixer
    run_num: int = 0                           # How many times the fixer has run
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    is_done : bool = False
    internal_errors: List[FixerError] = field(default_factory=list)

    def set_mode(self,mode : FixerMode):
        self.mode = mode

    def start_job(self):
        self.started_at = datetime.utcnow()
        self.finished_at = None
        self.run_num += 1
        self.is_done = False

    def finish_job(self):
        self.finished_at = datetime.utcnow()
        self.is_done = True

    def get_started_at_str(self) -> Optional[str]:
        return self.started_at.isoformat() if self.started_at else None

    def get_finished_at_str(self) -> Optional[str]:
        return self.finished_at.isoformat() if self.finished_at else None

    def add_error(self, stage: str, message: str, file: Optional[str] = None, exception: Optional[Exception] = None):
        self.internal_errors.append(FixerError(stage=stage, message=message, file=file, exception=str(exception) if exception else None))

    def to_dict(self) -> Dict[str,Any]:
        return {
            "mode" : self.mode.value,
            "output" : self.output,
            "run_num" : self.run_num,
            "started_at" : self.get_started_at_str(),
            "finished_at" : self.get_finished_at_str(),
            "is_done" : self.is_done,
            "internal_errors" : [error.to_dict() for error in self.internal_errors]
        }


@dataclass(frozen=True)
class TesterError:
    stage: str
    message: str
    file: Optional[str] = None
    exception: Optional[str] = None

    def to_dict(self) -> Dict[str,Any]:
        return {
            "stage" : self.stage,
            "message" : self.message,
            "file" : self.file,
            "exception" : self.exception,
        }

class TesterMode(str, Enum):
    GENERATE_TESTS = "GENERATE_TESTS"
    JUDGE_RESULTS = "TEST_AND_JUDGE_RESULTS"

@dataclass
class TesterState:
    mode: TesterMode                          # GENERATE_TESTS or JUDGE_RESULTS
    output: Optional[Dict[str, Any]] = None   # raw JSON output from Tester
    run_num: int = 0                           # How many times the fixer has run
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    is_done : bool = False
    internal_errors: List[TesterError] = field(default_factory=list)

    def set_mode(self,mode : TesterMode):
        self.mode = mode

    def start_job(self):
        self.started_at = datetime.utcnow()
        self.finished_at = None
        self.run_num += 1
        self.is_done = False

    def finish_job(self):
        self.finished_at = datetime.utcnow()
        self.is_done = True

    def get_started_at_str(self) -> Optional[str]:
        return self.started_at.isoformat() if self.started_at else None

    def get_finished_at_str(self) -> Optional[str]:
        return self.finished_at.isoformat() if self.finished_at else None

    def add_error(self, stage: str, message: str, file: Optional[str] = None, exception: Optional[Exception] = None):
        self.internal_errors.append(TesterError(stage=stage, message=message, file=file, exception=str(exception) if exception else None))

    def to_dict(self) -> Dict[str,Any]:
        return {
            "mode" : self.mode.value,
            "output" : self.output,
            "run_num" : self.run_num,
            "started_at" : self.get_started_at_str(),
            "finished_at" : self.get_finished_at_str(),
            "is_done" : self.is_done,
            "internal_errors" : [error.to_dict() for error in self.internal_errors]
        }


@dataclass(frozen=True)
class SystemError:
    stage: str
    message: str
    exception: Optional[str] = None

    def to_dict(self) -> Dict[str,Any]:
        return {
            "stage" : self.stage,
            "message" : self.message,
            "exception" : self.exception,
        }

class SystemPhase(str, Enum):
    INIT_PHASE = "INIT_PHASE"
    CONSTRUCTION_PHASE = "CONSTRUCTION_PHASE"
    REPAIR_PHASE = "REPAIR_PHASE"
    COMPLETED_PHASE = "COMPLETED_PHASE"
    FAILED_PHASE = "FAILED_PHASE"

class ConstructionPhase(str, Enum):
    AUDITING = "AUDITING"
    INITIAL_REPAIR = "INITIAL_REPAIR"
    TEST_GENERATION = "TEST_GENERATION"
    BOOTSTRAP_DONE = "BOOTSTRAP_DONE"

class RepairPhase(str, Enum):
    FIXING = "FIXING"
    TESTING_AND_JUDGING = "TESTING_AND_JUDGING"

class Agent(str, Enum):
    AUDITOR = "AUDITOR"
    FIXER = "FIXER"
    TESTER = "TESTER"

@dataclass
class SystemState:
    """Shared state between all agents and the orchestrator."""
    
    # Required from CLI
    target_dir: str
    
    # Execution tracking
    max_iterations: int = 10
    current_iteration: int = 0
    
    # Agent control
    system_phase: SystemPhase = SystemPhase.INIT_PHASE

    system_subphase: Optional[Union[ConstructionPhase, RepairPhase]] = None

    auditor_state: AuditorState = field(default_factory=AuditorState)
    fixer_state: FixerState = field(default_factory=lambda: FixerState(mode=FixerMode.REFACTOR))
    tester_state: TesterState = field(default_factory=lambda: TesterState(mode=TesterMode.GENERATE_TESTS))

    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

    system_errors: List[SystemError] = field(default_factory=list)

    # System flags
    is_stopped: bool = False
    last_agent: Agent = Agent.AUDITOR

    def get_started_at_str(self) -> Optional[str]:
        return self.started_at.isoformat() if self.started_at else None

    def get_finished_at_str(self) -> Optional[str]:
        return self.finished_at.isoformat() if self.finished_at else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_dir" : self.target_dir,
            "current_iteration" : self.current_iteration,
            "system_phase" : self.system_phase.value,
            "system_subphase": self.system_subphase.value if self.system_subphase else None,
            "auditor_state": self.auditor_state.to_dict(),
            "fixer_state": self.fixer_state.to_dict(),
            "tester_state": self.tester_state.to_dict(),
            "started_at": self.get_started_at_str(),
            "finished_at":self.get_finished_at_str(),
            "system_errors": [error.to_dict() for error in self.system_errors],
            "is_stopped": self.is_stopped,
            "last_agent": self.last_agent.value,
        }

    def change_phase(self, new_phase: SystemPhase, new_subphase : Optional[Union[ConstructionPhase, RepairPhase]], agent : Agent):
        self.system_phase = new_phase
        self.system_subphase = new_subphase
        self.last_agent = agent

    def next_iteration(self):
        self.current_iteration += 1

    def terminate(self, with_error : bool = False):
        if self.current_iteration >= self.max_iterations:
            self.system_phase = SystemPhase.FAILED_PHASE
        elif with_error :
            self.system_phase = SystemPhase.FAILED_PHASE
        else :
            self.system_phase = SystemPhase.COMPLETED_PHASE
        self.is_stopped = True
        self.finished_at = datetime.utcnow()

    def add_error(self, stage: str, message: str, exception: Optional[Exception] = None):
        self.system_errors.append(SystemError(stage=stage, message=message, exception=str(exception) if exception else None))