from fastapi import APIRouter


router = APIRouter(tags=["Eval"])


@router.post("/eval/run")
def run_eval():
    return {
        "status": "stub",
        "message": (
            "Eval API skeleton is ready. "
            "Frozen Core Eval execution will be implemented in a later stage."
        ),
    }