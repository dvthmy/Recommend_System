import subprocess
import os
import sys
from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict

router = APIRouter(prefix="/admin", tags=["Admin"])

def run_compute_features_script():
    """Run compute_features_improve.py script"""
    # Get the absolute path to the script
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    script_path = os.path.join(backend_dir, "scripts", "compute_features_improve.py")
    
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    # Change to scripts directory to ensure relative imports work
    scripts_dir = os.path.dirname(script_path)
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=scripts_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {result.stderr}")
    
    return result.stdout

@router.post("/compute-features", summary="Trigger compute_features_improve.py script")
async def trigger_compute_features(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """
    Trigger compute_features_improve.py script in background.
    
    This will:
    - Update TF-IDF vectors for recipes
    - Build user profile vectors (user_terms/user_weights)
    - Create SIMILAR_USER relationships
    - Create BELONGS_TO and POPULAR_IN relationships
    
    Note: Script runs in background and may take several minutes to complete.
    """
    try:
        background_tasks.add_task(run_compute_features_script)
        return {
            "message": "Script started in background",
            "status": "running",
            "note": "Check server logs for progress. Script may take several minutes to complete."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start script: {str(e)}")

@router.get("/compute-features/status", summary="Check if compute_features script is running")
async def get_compute_features_status() -> Dict[str, str]:
    """
    Check status of compute_features script.
    Note: This is a simple check. For production, consider using a job queue system.
    """
    return {
        "status": "unknown",
        "note": "For detailed status, check server logs or implement a job tracking system"
    }

