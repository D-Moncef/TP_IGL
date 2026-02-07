# src/refactoring_agents/fixer_agent.py
from json import JSONDecodeError
from src.utils.logger import log_experiment, ActionType
from src.llm.llm_service import LLMService
from src.tools.file_reader import read_dir
from src.tools.pylint_inal import analyse_file
from src.tools.extract_json import extract_json, sanitize_llm_json
from core.state import SystemState
import json

class AuditorAgent:
    def __init__(self, llm : LLMService):
        self.llm = llm
        self.name = "AUDITOR"

    def run(self, state : SystemState):
        stage = None
        state.auditor_state.start_job()

        try:
        # --------------------------------------------------
        # 1. READ SOURCE FILES
        # --------------------------------------------------
            try:
                files = read_dir(state.target_dir)
            except FileNotFoundError as e:
                stage = "READING_SOURCE_FILES"
                raise RuntimeError("Target directory not found") from e
            except PermissionError as e:
                stage = "READING_SOURCE_FILES"
                raise RuntimeError("Permission denied while reading source files") from e

        # --------------------------------------------------
        # 2. RUN PYLINT ANALYSIS
        # --------------------------------------------------
            pylint_reports = {}
            try:
                for path in files:
                    pylint_reports[path] = analyse_file(path)
            except Exception as e:
                stage = "RUNNING_PYLINT_ANALYSIS"
                raise RuntimeError("Pylint analysis failed") from e

        # --------------------------------------------------
        # 3. LOAD AUDITOR PROMPT
        # --------------------------------------------------
            try:
                with open("src/prompts/AuditorPrompt.txt", "r", encoding="utf-8") as f:
                    prompt_template = f.read()
            except FileNotFoundError as e:
                stage = "LOADING_AUDITOR_PROMPT"
                raise RuntimeError("Auditor prompt file missing") from e

        # --------------------------------------------------
        # 4. BUILD PROMPT
        # --------------------------------------------------
            try:
                files_info = []
                for path in files:
                    report = pylint_reports.get(path, {})
                    files_info.append({
                        "path": path,
                        "pylint_score": report.get("score"),
                        "pylint_report": report.get("details"),
                        "file_content": files[path]
                    })

                prompt = (
                        prompt_template
                        + "\n\nFiles report:\n"
                        + json.dumps(files_info, indent=2)
                )
            except (TypeError, ValueError) as e:
                stage = "BUILDING_PROMPT"
                raise RuntimeError("Failed to construct auditor prompt") from e

        # --------------------------------------------------
        # 5. CALL LLM
        # --------------------------------------------------
            try:
                output_str = self.llm.generate(prompt)
                output_str = extract_json(output_str)
                output_str = sanitize_llm_json(output_str)
            except TimeoutError as e:
                stage = "CALLING_LLM"
                raise RuntimeError("LLM request timed out") from e
            except Exception as e:
                stage = "CALLING_LLM"
                raise RuntimeError("LLM generation failed") from e

        # --------------------------------------------------
        # 6. PARSE LLM OUTPUT
        # --------------------------------------------------
            try:
                output = json.loads(output_str)
            except JSONDecodeError as e:
                stage = "PARSING_LLM_OUTPUT"
                raise RuntimeError("Auditor LLM output is not valid JSON") from e

        # --------------------------------------------------
        # 7. SAVE STATE
        # --------------------------------------------------
            state.auditor_state.output = output

        # --------------------------------------------------
        # 8. LOG SUCCESS
        # --------------------------------------------------
            log_experiment(
                agent_name=self.name,
                model_used="gemini-2.5-flash",
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": prompt,
                    "output_response": output_str
                },
                status="SUCCESS"
            )

        # --------------------------------------------------
        # 9. ERROR HANDLING
        # --------------------------------------------------
        except RuntimeError as e:
            state.auditor_state.add_error(
                stage=stage,
                message=str(e),
                exception=e
            )
            raise e
            #return False
        except Exception as e:
            state.auditor_state.add_error(
                stage="AUDIT",
                message="Unexpected auditor failure",
                exception=e
            )
            raise e
            #return False

        state.auditor_state.finish_job()
        return True