# src/refactoring_agents/auditor_agent.py
from json import JSONDecodeError
from src.utils.logger import log_experiment, ActionType
from src.llm.llm_service import LLMService
from src.tools.file_reader import read_dir, read_dir_separate
from src.tools.file_writer import write_file
from src.tools.extract_json import extract_json, sanitize_llm_json, strip_markdown_fences, is_subpath
from src.state.state import SystemState
from pathlib import Path
import json
import os

class FixerAgent:
    def __init__(self, llm: LLMService):
        self.llm = llm
        self.name = "FIXER"

    def run(self, state : SystemState):
        stage = None
        file_path = None
        state.fixer_state.start_job()
        try:
            file_path = None
            if state.fixer_state.mode.name == "REFACTOR":
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
                # 2. LOAD INITIAL_FIXER PROMPT
                # --------------------------------------------------
                try:
                    with open("src/prompts/FixerPrompt (Auditor -> Fixer).txt", "r", encoding="utf-8") as f:
                        prompt_template = f.read()
                except FileNotFoundError as e:
                    stage = "LOADING_INITIAL_FIXER_PROMPT"
                    raise RuntimeError("FixerPrompt(Auditor -> Fixer) file missing") from e

                # --------------------------------------------------
                # 3. BUILD PROMPT
                # --------------------------------------------------
                try:
                    prompt = (
                            prompt_template
                            + "\n\nRefactoring Plan :\n"
                            + json.dumps(state.auditor_state.output, indent=2)
                            + "\n\nEach file content and relative path :\n"
                            + json.dumps(files, indent=2)
                    )
                except (TypeError, ValueError) as e:
                    stage = "BUILDING_PROMPT"
                    raise RuntimeError("Failed to construct initial fixer prompt") from e
            else:
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
                # 2. LOAD FIXER PROMPT
                # --------------------------------------------------
                try:
                    with open("src/prompts/FixerPrompt(Tester -> Fixer).txt", "r", encoding="utf-8") as f:
                        prompt_template = f.read()
                except FileNotFoundError as e:
                    stage = "LOADING_FIXER_PROMPT"
                    raise RuntimeError("FixerPrompt(Tester -> Fixer) file missing") from e

                # --------------------------------------------------
                # 3. BUILD PROMPT
                # --------------------------------------------------
                try:

                    prompt = (
                            prompt_template
                            + "\n\nFixing instructions produced by tester :\n"
                            + json.dumps(state.tester_state.output, indent=2)
                            + "\n\nThe full content of all project source files with their paths :\n"
                            + json.dumps(files["source_files"], indent=2)
                            + "\n\n The full content of all test files with their paths :\n"
                            + json.dumps(files["test_files"], indent=2)
                    )
                except (TypeError, ValueError) as e:
                    stage = "BUILDING_PROMPT"
                    raise RuntimeError("Failed to construct fixer prompt") from e

            # --------------------------------------------------
            # 4. CALL LLM
            # --------------------------------------------------
            Error = True
            while(Error) :
                try:
                    output_str = self.llm.generate(prompt)
                    output_str = strip_markdown_fences(output_str)
                    output_str = extract_json(output_str)
                    output_str = sanitize_llm_json(output_str)
                    Error = False
                except TimeoutError as e:
                    stage = "CALLING_LLM"
                    #raise RuntimeError("LLM request timed out") from e
                except Exception as e:
                    stage = "CALLING_LLM"
                    #raise RuntimeError("LLM generation failed") from e

            # --------------------------------------------------
            # 5. PARSE LLM OUTPUT
            # --------------------------------------------------
            try:
                output = json.loads(output_str)
            except JSONDecodeError as e:
                stage = "PARSING_LLM_OUTPUT"
                raise RuntimeError("Fixer LLM output is not valid JSON") from e

            # --------------------------------------------------
            # 6. SAVE STATE
            # --------------------------------------------------
            state.fixer_state.output = output

            # --------------------------------------------------
            # 7. WRITE MODIFIED FILES
            # --------------------------------------------------
            try:
                target_root = Path(state.target_dir).resolve()

                if state.fixer_state.mode.name == "REFACTOR":
                    for file in output["files"]:

                        relative_path = Path(file["file_path"]).resolve()

                        relative_path = relative_path.resolve().relative_to(target_root)

                        safe_path = (target_root / relative_path).resolve()

                        # Prevent directory escape
                        if target_root not in safe_path.parents and safe_path != target_root:
                            raise RuntimeError("LLM attempted path escape")

                        write_file(
                            str(safe_path),
                            file["content"],
                            False,
                            str(target_root)
                        )
                else:
                    for file in output["files"]:

                        relative_path = Path(file["path"])

                        if is_subpath(target_root, relative_path.resolve()) :
                            relative_path = relative_path.resolve().relative_to(target_root)

                        safe_path = (target_root / relative_path).resolve()

                        if target_root not in safe_path.parents and safe_path != target_root:
                            raise RuntimeError("LLM attempted path escape")

                        if file.get("changed", False):
                            write_file(
                                str(safe_path),
                                file["content"],
                                False,
                                str(target_root)
                            )
            except PermissionError as e:
                stage = "WRITING_MODIFIED_FILES"
                raise RuntimeError("No permission to write a modified files") from e
            except Exception as e:
                stage = "WRITING_MODIFIED_FILES"
                raise RuntimeError("Failed to write a modified files") from e

            # --------------------------------------------------
            # 8. LOG SUCCESS
            # --------------------------------------------------
            log_experiment(
                agent_name=self.name,
                model_used=self.llm.model,
                action=ActionType.FIX,
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
            state.fixer_state.add_error(
                stage=stage,
                message=str(e),
                file = file_path,
                exception=e
            )
            raise e
            #return False
        except Exception as e:
            state.fixer_state.add_error(
                stage="FIX",
                message="Unexpected fix failure",
                file = file_path,
                exception=e
            )
            raise e
            #return False

        state.fixer_state.finish_job()
        return True