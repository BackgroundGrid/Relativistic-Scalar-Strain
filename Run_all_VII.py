import os
import sys
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def bootstrap_environment():
    """Ensures dependencies are available and sets the PYTHONPATH."""
    if ROOT_DIR not in sys.path:
        sys.path.insert(0, ROOT_DIR)
    os.environ["PYTHONPATH"] = ROOT_DIR

    req_file = os.path.join(ROOT_DIR, "requirements.txt")
    if os.path.exists(req_file):
        print("[1/3] Checking and installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])

def execute_section_scripts():
    """Runs equations_results_VII.py on root and all numerical section scripts in section_scripts_vol_02."""
    print("\n[2/3] Executing math engine & section scripts (generating plot/equation assets)...")
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT_DIR

    # 1. Run equations_results_VII.py located on root
    math_script = os.path.join(ROOT_DIR, "equations_results_VII.py")
    if os.path.exists(math_script):
        print(" -> Running equations_results_VII.py")
        subprocess.run([sys.executable, math_script], cwd=ROOT_DIR, env=env)
    else:
        print(f"Notice: {math_script} not found on root. Skipping.")

    # 2. Run all numerical section scripts in section_scripts_vol_02
    scripts_dir = os.path.join(ROOT_DIR, "section_scripts_vol_02")
    if not os.path.exists(scripts_dir):
        print(f"Directory missing: {scripts_dir}")
        return

    for script_name in sorted(os.listdir(scripts_dir)):
        if script_name.endswith(".py"):
            script_path = os.path.join(scripts_dir, script_name)
            print(f" -> Running {script_name}")
            subprocess.run([sys.executable, script_path], cwd=ROOT_DIR, env=env)

def execute_tests():
    """Runs automated physics tests in Test_files."""
    test_dir = os.path.join(ROOT_DIR, "Test_files")
    print("\n[3/3] Executing automated verification suite...")
    
    if not os.path.exists(test_dir):
        print(f"Notice: Test directory missing at {test_dir}. Skipping test phase.")
        return

    result = subprocess.run([sys.executable, "-m", "pytest", test_dir], cwd=ROOT_DIR)
    
    if result.returncode == 0:
        print("\n=========================================")
        print(" SUCCESS: All verification tests passed.")
        print("=========================================")
        sys.exit(0)
    else:
        print("\n=========================================")
        print(" FAILURE: One or more tests failed.")
        print("=========================================")
        sys.exit(1)

if __name__ == "__main__":
    print("=========================================")
    print(" Relativistic Scalar Strain - Volume II")
    print("=========================================")
    bootstrap_environment()
    execute_section_scripts()
    execute_tests()