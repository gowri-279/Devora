from fastapi import APIRouter

router = APIRouter(tags=["Missions"])


@router.get("/missions")
def get_missions():
    return {
        "missions": []
    }
    
@router.post("/complete-mission")
def complete_mission():
    return {
        "message": "Mission completed successfully!"
    }
    
@router.get("/learning-path")
def get_learning_path():
    return {
        "learning_path": []
    }
    
@router.post("/generate-learning-path")
def generate_learning_path():
    return {
        "message": "Learning path generation endpoint is working!"
    }