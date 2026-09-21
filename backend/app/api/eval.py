from fastapi import (
    APIRouter,
)

from app.schemas.eval import (
    EvalRunRequest,
    EvalRunResponse,
)
from app.services.eval_service import (
    run_eval,
)


router = APIRouter(
    tags=["Eval"]
)


@router.post(
    "/eval/run",
    response_model=(
        EvalRunResponse
    ),
)
def run_eval_endpoint(
    request: EvalRunRequest,
):

    result = run_eval(
        dataset_name=(
            request.dataset
        ),

        limit=request.limit,

        case_ids=(
            request.case_ids
            or None
        ),

        progress=True,
    )

    return EvalRunResponse(
        **result
    )