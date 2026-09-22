from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
)
from fastapi.responses import (
    FileResponse,
    RedirectResponse,
)


router = APIRouter(
    include_in_schema=False
)


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

FRONTEND_DIR = (
    REPO_ROOT
    / "frontend"
).resolve()


@router.get("/")
def root():

    return RedirectResponse(
        url="/ui/chat.html",
        status_code=302,
    )


@router.get("/ui")
def ui_root():

    return RedirectResponse(
        url="/ui/chat.html",
        status_code=302,
    )


@router.get(
    "/ui/{file_path:path}"
)
def ui_file(
    file_path: str,
):

    if not file_path:
        file_path = "chat.html"

    target = (
        FRONTEND_DIR
        / file_path
    ).resolve()

    # 防止目录穿越
    if (
        target != FRONTEND_DIR
        and FRONTEND_DIR
        not in target.parents
    ):
        raise HTTPException(
            status_code=404
        )

    if (
        not target.exists()
        or not target.is_file()
    ):
        raise HTTPException(
            status_code=404,
            detail="UI file not found.",
        )

    return FileResponse(
        target
    )
