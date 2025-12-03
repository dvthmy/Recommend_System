import subprocess
import os
import sys
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from typing import Dict, Optional
from neo4j import GraphDatabase
from ..config import settings

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


def run_create_similar_user_script(user_id: str):
    """Run create_similar_user_for_new_user.py script for a specific user"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    script_path = os.path.join(backend_dir, "scripts", "create_similar_user_for_new_user.py")
    
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    scripts_dir = os.path.dirname(script_path)
    result = subprocess.run(
        [sys.executable, script_path, "--user-id", user_id],
        cwd=scripts_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {result.stderr}")
    
    return result.stdout


@router.post("/users/{user_id}/similar-users", summary="Create SIMILAR_USER for new user")
async def create_similar_user_for_user(
    user_id: str,
    background_tasks: BackgroundTasks,
    run_in_background: bool = Query(default=True, description="Run in background (recommended)")
) -> Dict[str, str]:
    """
    Create SIMILAR_USER relationships for a specific user (Cold Start Solution).
    
    **When to call:**
    - Right after user completes onboarding
    - When user updates their preferences
    
    **Method:** Content-Based Similarity
    - Favorite cuisines (Jaccard similarity) - 40%
    - Same demographic group (gender + age_group) - 30%
    - Cooking time similarity - 20%
    - Allergy overlap - 10%
    
    **Note:** This is a temporary solution for cold start. After user has 10+ interactions,
    the system will automatically upgrade to interaction-based SIMILAR_USER (more accurate).
    
    Args:
        user_id: User ID to create relationships for
        run_in_background: If True, run in background (default). If False, run synchronously.
    """
    try:
        if run_in_background:
            background_tasks.add_task(run_create_similar_user_script, user_id)
            return {
                "message": f"Creating SIMILAR_USER for {user_id} in background",
                "status": "queued",
                "user_id": user_id,
                "note": "Check server logs for progress. Typically completes in 1-2 seconds."
            }
        else:
            # Run synchronously
            output = run_create_similar_user_script(user_id)
            return {
                "message": f"Created SIMILAR_USER for {user_id}",
                "status": "completed",
                "user_id": user_id,
                "output": output
            }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/users/{user_id}/upgrade-similar-users", summary="Upgrade to interaction-based SIMILAR_USER")
async def upgrade_similar_user_from_interactions(
    user_id: str,
    background_tasks: BackgroundTasks,
    min_interactions: int = Query(default=10, description="Minimum interactions required"),
    run_in_background: bool = Query(default=True, description="Run in background")
) -> Dict[str, str]:
    """
    Upgrade SIMILAR_USER relationships from preference-based to interaction-based.
    
    **When to call:**
    - After user has 10+ interactions (likes, ratings, views)
    - Automatically called by system when threshold is reached
    
    **Method:** Collaborative Filtering (Cosine Similarity on user vectors)
    - More accurate than preference-based
    - Uses actual user behavior
    
    Args:
        user_id: User ID to upgrade
        min_interactions: Minimum interactions required (default: 10)
        run_in_background: If True, run in background (default)
    """
    
    def run_upgrade():
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        script_path = os.path.join(backend_dir, "scripts", "create_similar_user_for_new_user.py")
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        scripts_dir = os.path.dirname(script_path)
        result = subprocess.run(
            [sys.executable, script_path, 
             "--user-id", user_id,
             "--update-from-interactions",
             "--min-interactions", str(min_interactions)],
            cwd=scripts_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Script failed: {result.stderr}")
        
        return result.stdout
    
    try:
        if run_in_background:
            background_tasks.add_task(run_upgrade)
            return {
                "message": f"Upgrading SIMILAR_USER for {user_id} in background",
                "status": "queued",
                "user_id": user_id,
                "note": "Upgrading from preference-based to interaction-based similarity"
            }
        else:
            output = run_upgrade()
            return {
                "message": f"Upgraded SIMILAR_USER for {user_id}",
                "status": "completed",
                "user_id": user_id,
                "output": output
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/belongs-to", summary="Create BELONGS_TO relationship for user")
async def create_belongs_to_for_user(
    user_id: str,
    background_tasks: BackgroundTasks,
    run_in_background: bool = Query(default=False, description="Run in background")
) -> Dict[str, str]:
    """
    Create BELONGS_TO relationship for a user to their demographic Group.
    
    **When to call:**
    - Right after user completes onboarding
    - When user updates their profile (gender or age_group)
    
    **What it does:**
    - Creates/finds Group node based on user's gender + age_group
    - Creates BELONGS_TO relationship: User → Group
    - Used for demographic-based recommendations
    
    **Note:** This is very fast (< 100ms), so running synchronously is recommended.
    
    Args:
        user_id: User ID to create relationship for
        run_in_background: If True, run in background. Default False (synchronous).
    """
    
    def run_belongs_to():
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        script_path = os.path.join(backend_dir, "scripts", "create_similar_user_for_new_user.py")
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        scripts_dir = os.path.dirname(script_path)
        result = subprocess.run(
            [sys.executable, script_path, 
             "--user-id", user_id,
             "--belongs-to-only"],
            cwd=scripts_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Script failed: {result.stderr}")
        
        return result.stdout
    
    try:
        if run_in_background:
            background_tasks.add_task(run_belongs_to)
            return {
                "message": f"Creating BELONGS_TO for {user_id} in background",
                "status": "queued",
                "user_id": user_id
            }
        else:
            # Run synchronously (recommended - it's very fast)
            output = run_belongs_to()
            return {
                "message": f"Created BELONGS_TO for {user_id}",
                "status": "completed",
                "user_id": user_id,
                "output": output
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/cuisine-preferences-updated", summary="Re-create SIMILAR_USER after cuisine preferences change")
async def handle_cuisine_preferences_update(
    user_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Re-create SIMILAR_USER relationships after user updates cuisine preferences.
    
    **When to call:**
    - After user updates cuisine preferences in profile edit
    - After PUT /users/{user_id}/cuisine-preferences
    
    **What it does:**
    - Deletes old preference-based SIMILAR_USER relationships
    - Creates new ones based on updated cuisines
    
    **Note:** If user already has interaction-based SIMILAR_USER (10+ interactions),
    this will NOT downgrade them. Only updates preference-based users.
    
    Args:
        user_id: User ID who updated cuisine preferences
    """
    
    def run_update():
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        script_path = os.path.join(backend_dir, "scripts", "create_similar_user_for_new_user.py")
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        scripts_dir = os.path.dirname(script_path)
        
        # Re-create SIMILAR_USER (skip BELONGS_TO as it's not affected by cuisines)
        result = subprocess.run(
            [sys.executable, script_path, "--user-id", user_id, "--skip-belongs-to"],
            cwd=scripts_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Script failed: {result.stderr}")
        
        return result.stdout
    
    try:
        background_tasks.add_task(run_update)
        return {
            "message": f"Re-creating SIMILAR_USER for {user_id} based on new cuisine preferences",
            "status": "queued",
            "user_id": user_id,
            "note": "This will update preference-based SIMILAR_USER only. Runs in background."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/onboarding-complete", summary="Complete all post-onboarding tasks")
async def complete_onboarding_tasks(
    user_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Complete all post-onboarding tasks for a new user.
    
    **When to call:**
    - Right after user completes onboarding form
    
    **What it does:**
    1. Creates BELONGS_TO relationship (User → Group)
    2. Creates SIMILAR_USER relationships (preference-based cold start)
    
    **Note:** All tasks run in background. Typically completes in 1-2 seconds.
    
    Args:
        user_id: User ID who just completed onboarding
    """
    
    def run_all_tasks():
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        script_path = os.path.join(backend_dir, "scripts", "create_similar_user_for_new_user.py")
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        scripts_dir = os.path.dirname(script_path)
        
        # Run with both BELONGS_TO and SIMILAR_USER
        result = subprocess.run(
            [sys.executable, script_path, "--user-id", user_id],
            cwd=scripts_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Script failed: {result.stderr}")
        
        return result.stdout
    
    try:
        background_tasks.add_task(run_all_tasks)
        return {
            "message": f"Post-onboarding tasks queued for {user_id}",
            "status": "queued",
            "user_id": user_id,
            "tasks": [
                "Create BELONGS_TO (User → Group)",
                "Create SIMILAR_USER (preference-based)"
            ],
            "note": "Tasks will complete in 1-2 seconds. Check server logs for progress."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

