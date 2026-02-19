import argparse
import sys
import os
from dotenv import load_dotenv
from src.orchestrator.orchestrator import RefactoringOrchestrator
from src.refactoring_agents.auditor_agent import AuditorAgent
from src.refactoring_agents.fixer_agent import FixerAgent
from src.refactoring_agents.tester_agent import TesterAgent
from core.state import SystemState
from src.llm.llm_service import LLMService
from src.data_management.data_officer import DataOfficer,TelemetryValidationError
from src.utils.logger import log_experiment

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
    load_dotenv()
    key = os.getenv("MISTRAL_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY not found in .env")

    system_state : SystemState = SystemState(target_dir=args.target_dir)
    llm : LLMService = LLMService(key)
    auditor : AuditorAgent = AuditorAgent(llm)
    fixer : FixerAgent = FixerAgent(llm)
    tester : TesterAgent = TesterAgent(llm)
    orchestrator : RefactoringOrchestrator = RefactoringOrchestrator(system_state,auditor,fixer,tester)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    log_experiment("System","unknown", "STARTUP", f"Target: {args.target_dir}", "INFO")

    data_officer : DataOfficer = DataOfficer()
    try :
        if orchestrator.run() :
            data_officer.validate_logs()
            print("✅ MISSION_COMPLETE")
            print(system_state.system_errors)
    except TelemetryValidationError as e:
        raise


if __name__ == "__main__":
    main()