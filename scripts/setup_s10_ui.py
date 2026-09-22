from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FILES = {}


FILES[
    "backend/app/api/ops.py"
] = r'''import json
from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)
from fastapi.encoders import (
    jsonable_encoder,
)

from app.db.connection import (
    get_connection,
)


router = APIRouter(
    prefix="/ops",
    tags=["Ops"],
)


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

BADCASE_PATH = (
    REPO_ROOT
    / "eval"
    / "badcase_runtime.jsonl"
)


@router.get("/traces")
def list_traces(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    """
    S10 Trace 页面使用。

    只读取已经持久化的 Trace，
    不修改任何 S3-S9 业务逻辑。
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT to_jsonb(t)
                FROM traces AS t
                ORDER BY ctid DESC
                LIMIT %s
                """,
                (limit,),
            )

            rows = cur.fetchall()

    items = [
        jsonable_encoder(
            row[0]
        )
        for row in rows
    ]

    return {
        "count": len(items),
        "items": items,
    }


@router.get(
    "/traces/{trace_id}"
)
def get_trace(
    trace_id: str,
):
    """
    按 trace_id 完整还原一次请求。
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT to_jsonb(t)
                FROM traces AS t
                WHERE trace_id = %s
                LIMIT 1
                """,
                (trace_id,),
            )

            row = cur.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Trace not found.",
        )

    return jsonable_encoder(
        row[0]
    )


@router.get("/badcases")
def list_badcases(
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
):
    """
    S10 Badcase 页面。

    当前直接复用 S9 runtime badcase pool。
    """

    if not BADCASE_PATH.exists():

        return {
            "count": 0,
            "items": [],
        }

    lines = (
        BADCASE_PATH
        .read_text(
            encoding="utf-8"
        )
        .splitlines()
    )

    items = []

    for line in reversed(lines):

        if not line.strip():
            continue

        try:

            items.append(
                json.loads(line)
            )

        except json.JSONDecodeError:

            items.append(
                {
                    "raw": line,
                    "parse_error": True,
                }
            )

        if len(items) >= limit:
            break

    return {
        "count": len(items),
        "items": items,
    }
'''


FILES[
    "backend/app/api/ui.py"
] = r'''from pathlib import Path

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
'''


FILES[
    "backend/app/s10_app.py"
] = r'''"""
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
'''


FILES[
    "frontend/styles.css"
] = r'''* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family:
        Inter,
        "Microsoft YaHei",
        Arial,
        sans-serif;
    background: #f6f7fb;
    color: #172033;
}

header {
    height: 64px;
    background: #ffffff;
    border-bottom: 1px solid #e5e8ef;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
}

.brand {
    font-size: 20px;
    font-weight: 700;
}

.brand span {
    color: #667085;
    font-size: 12px;
    margin-left: 8px;
    font-weight: 500;
}

nav a {
    text-decoration: none;
    color: #667085;
    margin-left: 22px;
    font-size: 14px;
}

nav a.active {
    color: #111827;
    font-weight: 700;
}

main {
    max-width: 1180px;
    margin: 32px auto;
    padding: 0 22px;
}

h1 {
    font-size: 26px;
    margin-bottom: 6px;
}

.subtitle {
    color: #667085;
    margin-bottom: 24px;
}

.card {
    background: #fff;
    border: 1px solid #e5e8ef;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 18px;
}

.grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
}

label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 6px;
}

input,
select,
textarea {
    width: 100%;
    border: 1px solid #d5dae4;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 14px;
    background: #fff;
}

textarea {
    min-height: 110px;
    resize: vertical;
}

button {
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    background: #111827;
    color: #fff;
    cursor: pointer;
    font-weight: 600;
}

button:disabled {
    opacity: .55;
    cursor: wait;
}

.row {
    display: flex;
    gap: 10px;
    align-items: center;
}

.badge {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 999px;
    background: #eef2ff;
    margin-right: 7px;
    font-size: 12px;
    font-weight: 600;
}

pre {
    white-space: pre-wrap;
    word-break: break-word;
    background: #101828;
    color: #e6edf3;
    padding: 16px;
    border-radius: 9px;
    max-height: 580px;
    overflow: auto;
    font-size: 12px;
}

.item {
    padding: 12px 0;
    border-bottom: 1px solid #edf0f5;
}

.item:last-child {
    border-bottom: 0;
}

.muted {
    color: #667085;
    font-size: 13px;
}

.error {
    color: #b42318;
}

.success {
    color: #067647;
}

.metric {
    font-size: 28px;
    font-weight: 700;
}
'''


FILES[
    "frontend/common.js"
] = r'''async function getJSON(url) {
    const response = await fetch(url);

    if (!response.ok) {
        const text = await response.text();
        throw new Error(
            `${response.status} ${text}`
        );
    }

    return await response.json();
}


async function postJSON(
    url,
    payload
) {
    const response = await fetch(
        url,
        {
            method: "POST",
            headers: {
                "Content-Type":
                    "application/json"
            },
            body:
                JSON.stringify(payload)
        }
    );

    if (!response.ok) {
        const text = await response.text();
        throw new Error(
            `${response.status} ${text}`
        );
    }

    return await response.json();
}


function pretty(data) {
    return JSON.stringify(
        data,
        null,
        2
    );
}


function setLoading(
    button,
    loading
) {
    button.disabled = loading;

    button.dataset.oldText =
        button.dataset.oldText
        || button.innerText;

    button.innerText =
        loading
        ? "处理中..."
        : button.dataset.oldText;
}
'''


HEADER = r'''<header>
    <div class="brand">
        KnowFlow
        <span>Enterprise Knowledge Agent</span>
    </div>

    <nav>
        <a href="/ui/chat.html">Chat</a>
        <a href="/ui/trace.html">Trace</a>
        <a href="/ui/eval.html">Eval</a>
        <a href="/ui/badcase.html">Badcase</a>
    </nav>
</header>
'''


FILES[
    "frontend/chat.html"
] = f'''<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>KnowFlow · Chat</title>
    <link rel="stylesheet"
          href="/ui/styles.css">
</head>
<body>

{HEADER}

<main>

    <h1>智能问答</h1>

    <div class="subtitle">
        严格依据企业知识证据、
        权限和版本规则进行判断。
    </div>

    <div class="card">

        <div class="grid">

            <div>
                <label>身份预设</label>
                <select id="preset">
                    <option value="hr">
                        HR 普通员工
                    </option>
                    <option value="finance">
                        Finance 普通员工
                    </option>
                    <option value="product">
                        Product 普通员工
                    </option>
                    <option value="service">
                        Service 普通员工
                    </option>
                    <option value="finance_manager">
                        Finance Manager
                    </option>
                    <option value="admin">
                        Admin
                    </option>
                </select>
            </div>

            <div>
                <label>User ID</label>
                <input id="userId"
                       value="UI001">
            </div>

            <div>
                <label>Department</label>
                <input id="department"
                       value="hr">
            </div>

            <div>
                <label>Role</label>
                <input id="role"
                       value="employee">
            </div>

        </div>

        <br>

        <label>Authorized KB IDs</label>
        <input id="kbIds"
               value="KB_HR_PUBLIC">

        <br><br>

        <label>问题</label>

        <textarea id="query"
        >试用期多久？</textarea>

        <br>

        <button id="sendBtn">
            发送问题
        </button>

    </div>

    <div class="card">

        <div id="summary">
            尚未发起请求。
        </div>

        <pre id="result">{{}}</pre>

    </div>

</main>

<script src="/ui/common.js"></script>

<script>

const PRESETS = {{
    hr: {{
        department: "hr",
        role: "employee",
        kb: ["KB_HR_PUBLIC"]
    }},
    finance: {{
        department: "finance",
        role: "employee",
        kb: ["KB_FINANCE_PUBLIC"]
    }},
    product: {{
        department: "product",
        role: "employee",
        kb: ["KB_PRODUCT_PUBLIC"]
    }},
    service: {{
        department: "service",
        role: "employee",
        kb: ["KB_SERVICE_PUBLIC"]
    }},
    finance_manager: {{
        department: "finance",
        role: "finance_manager",
        kb: [
            "KB_FINANCE_PUBLIC",
            "KB_FINANCE_PRIVATE"
        ]
    }},
    admin: {{
        department: "admin",
        role: "admin",
        kb: [
            "KB_FINANCE_PUBLIC",
            "KB_HR_PUBLIC",
            "KB_PRODUCT_PUBLIC",
            "KB_SERVICE_PUBLIC",
            "KB_FINANCE_PRIVATE"
        ]
    }}
}};


document
.getElementById("preset")
.addEventListener(
    "change",
    (event) => {{

        const p =
            PRESETS[event.target.value];

        document.getElementById(
            "department"
        ).value = p.department;

        document.getElementById(
            "role"
        ).value = p.role;

        document.getElementById(
            "kbIds"
        ).value = p.kb.join(",");
    }}
);


document
.getElementById("sendBtn")
.addEventListener(
    "click",
    async () => {{

        const button =
            document.getElementById(
                "sendBtn"
            );

        const summary =
            document.getElementById(
                "summary"
            );

        const result =
            document.getElementById(
                "result"
            );

        setLoading(
            button,
            true
        );

        try {{

            const kbIds =
                document
                .getElementById("kbIds")
                .value
                .split(",")
                .map(v => v.trim())
                .filter(Boolean);

            const payload = {{
                query:
                    document
                    .getElementById("query")
                    .value,

                user: {{
                    user_id:
                        document
                        .getElementById(
                            "userId"
                        ).value,

                    department:
                        document
                        .getElementById(
                            "department"
                        ).value,

                    role:
                        document
                        .getElementById(
                            "role"
                        ).value,

                    authorized_kb_ids:
                        kbIds
                }}
            }};

            const data =
                await postJSON(
                    "/chat",
                    payload
                );

            summary.innerHTML =
                `<span class="badge">
                    ${{data.domain}}
                 </span>
                 <span class="badge">
                    ${{data.decision}}
                 </span>
                 <span class="badge">
                    trace=${{
                        data.trace_id || "-"
                    }}
                 </span>
                 <br><br>
                 <b>Reason:</b>
                 ${{
                    data.reason || "-"
                 }}
                 ${{
                    data.clarifying_question
                    ? `<br><br><b>Clarify:</b>
                       ${{data.clarifying_question}}`
                    : ""
                 }}`;

            result.innerText =
                pretty(data);

        }}
        catch (error) {{

            summary.innerHTML =
                `<span class="error">
                    ${{error}}
                 </span>`;

        }}
        finally {{

            setLoading(
                button,
                false
            );

        }}

    }}
);

</script>

</body>
</html>
'''


FILES[
    "frontend/trace.html"
] = f'''<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>KnowFlow · Trace</title>
    <link rel="stylesheet"
          href="/ui/styles.css">
</head>
<body>

{HEADER}

<main>

    <h1>Trace</h1>

    <div class="subtitle">
        按 trace_id 完整还原
        Router / Filter / Retrieval /
        Judge / Citation 结果。
    </div>

    <div class="card">

        <div class="row">

            <input id="traceId"
                   placeholder="TR-...">

            <button id="loadBtn">
                查询 Trace
            </button>

            <button id="recentBtn">
                最近 20 条
            </button>

        </div>

    </div>

    <div class="card">
        <pre id="result">{{}}</pre>
    </div>

</main>

<script src="/ui/common.js"></script>

<script>

const output =
    document.getElementById(
        "result"
    );


document
.getElementById("loadBtn")
.addEventListener(
    "click",
    async () => {{

        try {{

            const id =
                document
                .getElementById(
                    "traceId"
                ).value.trim();

            const data =
                await getJSON(
                    `/ops/traces/${{
                        encodeURIComponent(id)
                    }}`
                );

            output.innerText =
                pretty(data);

        }}
        catch (error) {{

            output.innerText =
                String(error);

        }}

    }}
);


document
.getElementById("recentBtn")
.addEventListener(
    "click",
    async () => {{

        try {{

            const data =
                await getJSON(
                    "/ops/traces?limit=20"
                );

            output.innerText =
                pretty(data);

        }}
        catch (error) {{

            output.innerText =
                String(error);

        }}

    }}
);

</script>

</body>
</html>
'''


FILES[
    "frontend/eval.html"
] = f'''<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>KnowFlow · Eval</title>
    <link rel="stylesheet"
          href="/ui/styles.css">
</head>
<body>

{HEADER}

<main>

    <h1>Eval</h1>

    <div class="subtitle">
        运行冻结 Core61 或 Gold100 回归。
    </div>

    <div class="card">

        <div class="grid">

            <div>
                <label>Dataset</label>
                <select id="dataset">
                    <option value="core_61">
                        Core61
                    </option>
                    <option value="gold_v1">
                        Gold100
                    </option>
                </select>
            </div>

            <div>
                <label>Limit（可空）</label>
                <input id="limit"
                       type="number"
                       min="1">
            </div>

        </div>

        <br>

        <label>
            Case IDs（逗号分隔，可空）
        </label>

        <input id="caseIds"
               placeholder="F001,H302,V101">

        <br><br>

        <button id="runBtn">
            运行 Eval
        </button>

    </div>

    <div class="card">

        <div id="summary">
            尚未运行。
        </div>

        <pre id="result">{{}}</pre>

    </div>

</main>

<script src="/ui/common.js"></script>

<script>

document
.getElementById("runBtn")
.addEventListener(
    "click",
    async () => {{

        const button =
            document.getElementById(
                "runBtn"
            );

        setLoading(
            button,
            true
        );

        const output =
            document.getElementById(
                "result"
            );

        const summary =
            document.getElementById(
                "summary"
            );

        try {{

            const rawIds =
                document
                .getElementById(
                    "caseIds"
                )
                .value;

            const caseIds =
                rawIds
                .split(",")
                .map(x => x.trim())
                .filter(Boolean);

            const rawLimit =
                document
                .getElementById(
                    "limit"
                )
                .value;

            const payload = {{
                dataset:
                    document
                    .getElementById(
                        "dataset"
                    ).value,

                limit:
                    rawLimit
                    ? Number(rawLimit)
                    : null,

                case_ids:
                    caseIds
            }};

            const data =
                await postJSON(
                    "/eval/run",
                    payload
                );

            summary.innerHTML =
                `<span class="badge">
                    ${{data.dataset_name}}
                 </span>
                 <span class="badge">
                    passed=${{
                        data.passed_cases
                    }}/${{
                        data.total_cases
                    }}
                 </span>
                 <span class="badge">
                    run=${{data.run_id}}
                 </span>`;

            output.innerText =
                pretty(data);

        }}
        catch (error) {{

            output.innerText =
                String(error);

        }}
        finally {{

            setLoading(
                button,
                false
            );

        }}

    }}
);

</script>

</body>
</html>
'''


FILES[
    "frontend/badcase.html"
] = f'''<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>KnowFlow · Badcase</title>
    <link rel="stylesheet"
          href="/ui/styles.css">
</head>
<body>

{HEADER}

<main>

    <h1>Badcase</h1>

    <div class="subtitle">
        查看 S9/S10 自动评测产生的
        runtime badcase pool。
    </div>

    <div class="card">

        <div class="row">

            <input id="limit"
                   type="number"
                   min="1"
                   max="500"
                   value="50">

            <button id="loadBtn">
                刷新
            </button>

        </div>

    </div>

    <div class="card">

        <div id="summary"></div>

        <pre id="result">[]</pre>

    </div>

</main>

<script src="/ui/common.js"></script>

<script>

async function loadBadcases() {{

    const limit =
        document
        .getElementById(
            "limit"
        ).value;

    const data =
        await getJSON(
            `/ops/badcases?limit=${{
                encodeURIComponent(limit)
            }}`
        );

    document.getElementById(
        "summary"
    ).innerHTML =
        `<span class="badge">
            count=${{data.count}}
         </span>`;

    document.getElementById(
        "result"
    ).innerText =
        pretty(data.items);
}}


document
.getElementById("loadBtn")
.addEventListener(
    "click",
    async () => {{

        try {{
            await loadBadcases();
        }}
        catch (error) {{
            document.getElementById(
                "result"
            ).innerText =
                String(error);
        }}

    }}
);


loadBadcases();

</script>

</body>
</html>
'''


def main():

    for relative, content in (
        FILES.items()
    ):

        path = (
            ROOT
            / relative
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding="utf-8",
        )

        print(
            f"created: {path}"
        )

    print("")
    print(
        "S10 Minimal UI files created."
    )


if __name__ == "__main__":
    main()
