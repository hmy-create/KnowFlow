"""
S10 deployable entrypoint.

重要：
不修改冻结的 app.main 业务逻辑，
只在原 FastAPI app 上增加：

- Minimal UI
- Trace read API
- Badcase read API
"""

from app.main import app

from app.api.ops import (
    router as ops_router,
)
from app.api.ui import (
    router as ui_router,
)


app.include_router(
    ops_router
)

app.include_router(
    ui_router
)
