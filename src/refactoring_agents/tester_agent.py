# src/refactoring_agents/tester_agent.py
from json import JSONDecodeError
from src.utils.logger import log_experiment, ActionType
from src.llm.llm_service import LLMService
from src.tools.file_reader import read_dir, read_dir_separate
from src.tools.file_writer import write_file
from src.tools.extract_json import extract_json, sanitize_llm_json
from src.tools.test_sendbox import run_pytest
from src.state import SystemState
from src.utils.logger import ActionType
import json

class TesterAgent:
    def __init__(self, llm: LLMService):
        self.llm = llm
        self.name = "TESTER"

    def generate_tests(self, state : SystemState):
        file_path = None
        stage = None
        state.tester_state.start_job()
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
            # 2. LOAD TEST_GENERATOR PROMPT
            # --------------------------------------------------
            try:
                with open("src/prompts/TesterPrompt (Generate Tests).txt", "r", encoding="utf-8") as f:
                    prompt_template = f.read()
            except FileNotFoundError as e:
                stage = "LOADING_TEST_GENERATOR_PROMPT"
                raise RuntimeError("TesterPrompt(Generate Tests) file missing") from e

            # --------------------------------------------------
            # 3. BUILD PROMPT
            # --------------------------------------------------
            try:
                prompt = (
                        prompt_template
                        + "\n\nEach file content and relative path :\n"
                        + json.dumps(files, indent=2)
                )
            except (TypeError, ValueError) as e:
                stage = "BUILDING_PROMPT"
                raise RuntimeError("Failed to construct test generator prompt") from e

            # --------------------------------------------------
            # 4. CALL LLM
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
            # 5. PARSE LLM OUTPUT
            # --------------------------------------------------
            try:
                output = json.loads(output_str)
            except JSONDecodeError as e:
                stage = "PARSING_LLM_OUTPUT"
                raise RuntimeError("Test generator LLM output is not valid JSON") from e

            # --------------------------------------------------
            # 6. SAVE STATE
            # --------------------------------------------------
            state.tester_state.output = output

            # --------------------------------------------------
            # 7. WRITE TEST FILES
            # --------------------------------------------------
            try:
                for file in output["tests"]:
                        file_path = ("sandbox/"+file["file_path"])
                        write_file(file_path, file["content"], True)
            except PermissionError as e:
                stage = "WRITING_TEST_FILES"
                raise RuntimeError("No permission to write a test files") from e
            except Exception as e:
                stage = "WRITING_TEST_FILES"
                raise RuntimeError("Failed to write a test files") from e

            # --------------------------------------------------
            # 8. LOG SUCCESS
            # --------------------------------------------------
            log_experiment(
                agent_name=self.name,
                model_used="gemini-2.5-flash",
                action=ActionType.GENERATION,
                details={
                    "input_prompt": prompt,
                    "output_response": output_str
                },
                status="SUCCESS"
            )
        except RuntimeError as e:
            state.tester_state.add_error(
                stage=stage,
                message=str(e),
                exception=e
            )
            raise e
            #return False
        except Exception as e:
            state.tester_state.add_error(
                stage="TEST_GENERATION",
                message="Unexpected test generation failure",
                exception=e
            )
            raise e
            #return False

        state.tester_state.finish_job()
        return True

    def test_and_judge(self, state : SystemState):
        state.tester_state.start_job()
        file_path = None
        stage = None
        try:
            # --------------------------------------------------
            # 1. READ SOURCE FILES AND TEST FILES SEPARATELY
            # --------------------------------------------------
            try:
                files = read_dir_separate(state.target_dir)
            except FileNotFoundError as e:
                stage = "READING_SOURCE_AND_TEST_FILES"
                raise RuntimeError("Target directory not found") from e
            except PermissionError as e:
                stage = "READING_SOURCE_AND_TEST_FILES"
                raise RuntimeError("Permission denied while reading source files") from e

            # --------------------------------------------------
            # 2. EXECUTING PYTEST
            # --------------------------------------------------
            try:
                pytest_result = run_pytest(state.target_dir)
            except Exception as e:
                stage = "EXECUTING_PYTEST"
                raise RuntimeError("Failed to execute pytest")

            # --------------------------------------------------
            # 3. LOAD JUDGE PROMPT
            # --------------------------------------------------
            try:
                with open("src/prompts/TesterPrompt(Judge the results).txt", "r", encoding="utf-8") as f:
                    prompt_template = f.read()
            except FileNotFoundError as e:
                stage = "LOADING_JUDGE_PROMPT"
                raise RuntimeError("TesterPrompt(Judge the results) file missing") from e

            # --------------------------------------------------
            # 4. BUILD PROMPT
            # --------------------------------------------------
            try:
                prompt = (
                        prompt_template
                        + "\n\nRaw pytest execution output :\n"
                        + json.dumps(pytest_result, indent=2)
                        + "\n\n The full content of all test files with their relative paths :\n"
                        + json.dumps(files["test_files"], indent=2)
                        + "\n\nThe full content of all project source files with their relative paths :\n"
                        + json.dumps(files["source_files"], indent=2)
                )
            except (TypeError, ValueError) as e:
                stage = "BUILDING_PROMPT"
                raise RuntimeError("Failed to construct tester prompt") from e

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
                raise RuntimeError("Tester LLM output is not valid JSON") from e

            # --------------------------------------------------
            # 7. SAVE STATE
            # --------------------------------------------------
            state.tester_state.output = output

            # --------------------------------------------------
            # 8. LOG SUCCESS
            # --------------------------------------------------
            log_experiment(
                agent_name=self.name,
                model_used=self.llm.model,
                action=ActionType.DEBUG,
                details={
                    "input_prompt": prompt,
                    "output_response": output_str
                },
                status="SUCCESS"
            )

        # --------------------------------------------------
        # 8. ERROR HANDLING
        # --------------------------------------------------
        except RuntimeError as e:
            state.tester_state.add_error(
                stage=stage,
                message=str(e),
                file=file_path,
                exception=e
            )
            raise e
            #return 2
        except Exception as e:
            state.tester_state.add_error(
                stage="FIX",
                message="Unexpected judge failure",
                file=file_path,
                exception=e
            )
            raise e
            #return 2

        state.tester_state.finish_job()

        return pytest_result["passed"]