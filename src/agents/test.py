from data_officer_agent import DataOfficerAgent

# Initialize Data Officer
data_officer = DataOfficerAgent()

# -----------------------------
# Buggy Python file (syntax error)
# -----------------------------
buggy_code = """
def foo()
    print("Missing colon in function definition")
"""

data_officer.generate_test_file(
    path="sandbox/buggy_file.py",
    content=buggy_code
)

# -----------------------------
# Edge-case file (empty file)
# -----------------------------
data_officer.generate_test_file(
    path="sandbox/empty_file.py",
    content=""
)

# -----------------------------
# Trap scenario (infinite loop)
# -----------------------------
trap_code = """
while True:
    pass  # Infinite loop
"""

data_officer.generate_test_file(
    path="sandbox/infinite_loop.py",
    content=trap_code
)
