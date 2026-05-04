import subprocess
import os
import sys

def run_app():
    """
    Run both the FastAPI backend and Streamlit frontend in separate terminal windows.
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    print("Starting FastAPI backend in a new terminal window...")
    # Run the backend in a new CMD window
    subprocess.Popen(
        f'start cmd /k "{sys.executable}" main.py',
        cwd=backend_dir,
        shell=True
    )

    print("Starting Streamlit frontend in a new terminal window...")
    # Run the streamlit app in a new CMD window
    subprocess.Popen(
        f'start cmd /k "{sys.executable}" -m streamlit run app.py',
        cwd=frontend_dir,
        shell=True
    )

if __name__ == "__main__":
    run_app()
