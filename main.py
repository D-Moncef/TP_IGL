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

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    # Declaring the System state, the orchestrator and the different agents :
    state : SystemState
    auditor : AuditorAgent = AuditorAgent()
    fixer : FixerAgent = FixerAgent()
    tester : TesterAgent = TesterAgent()
    orchestrator : RefactoringOrchestrator = RefactoringOrchestrator(state,auditor,fixer,tester)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    log_experiment("System", "STARTUP", f"Target: {args.target_dir}", "INFO")

    if orchestrator.run() :
        print("✅ MISSION_COMPLETE")

if __name__ == "__main__":
    main()