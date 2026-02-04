import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment
from src.orchestrator.orchestrator import RefactoringOrchestrator
from src.refactoring_agents.auditor_agent import AuditorAgent
from src.refactoring_agents.fixer_agent import FixerAgent
from src.refactoring_agents.tester_agent import TesterAgent
from core.state import SystemState
from src.llm.llm_service import LLMService
from src.data_management.data_officer import DataOfficer,TelemetryValidationError

load_dotenv()

def main():
    global state
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    # Declaring the System state, the orchestrator and the different agents :
    with open(".env", "r", encoding="utf-8") as f:
        content = f.read()

    key = content.split("=")[1]
    state : SystemState
    llm : LLMService = LLMService(key)
    auditor : AuditorAgent = AuditorAgent(llm)
    fixer : FixerAgent = FixerAgent(llm)
    tester : TesterAgent = TesterAgent(llm)
    orchestrator : RefactoringOrchestrator = RefactoringOrchestrator(state,auditor,fixer,tester)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    log_experiment("System", "STARTUP", f"Target: {args.target_dir}", "INFO")

    data_officer : DataOfficer = DataOfficer()
    try :
        if orchestrator.run() :
            data_officer.validate_logs()
            print("✅ MISSION_COMPLETE")
    except TelemetryValidationError as e:
        raise


if __name__ == "__main__":
    main()