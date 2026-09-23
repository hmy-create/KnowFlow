from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


FILES: dict[str, str] = {}


FILES["frontend/styles.css"] = r'''* {
    box-sizing: border-box;
}

:root {
    --bg: #f5f7fb;
    --surface: #ffffff;
    --surface-soft: #f8faff;
    --line: #e5eaf2;
    --line-strong: #d8e0ec;
    --text: #172033;
    --text-2: #475467;
    --muted: #8a94a6;
    --primary: #2f6fed;
    --primary-dark: #1f5bd8;
    --primary-soft: #edf4ff;
    --green: #17a673;
    --green-soft: #ecfdf3;
    --yellow: #d89018;
    --yellow-soft: #fff8e8;
    --red: #e34b4b;
    --red-soft: #fff1f1;
    --purple: #7c5ce4;
    --purple-soft: #f4f0ff;
    --shadow: 0 10px 28px rgba(31, 45, 70, 0.06);
    --radius: 14px;
}

html,
body {
    margin: 0;
    min-height: 100%;
    font-family:
        Inter,
        "Microsoft YaHei",
        "PingFang SC",
        Arial,
        sans-serif;
    color: var(--text);
    background: var(--bg);
}

body {
    min-height: 100vh;
}

a {
    color: inherit;
}

button,
input,
select,
textarea {
    font: inherit;
}

button {
    cursor: pointer;
}

.app-shell {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 224px minmax(0, 1fr);
}

.sidebar {
    position: sticky;
    top: 0;
    height: 100vh;
    padding: 18px 14px 16px;
    background: var(--surface);
    border-right: 1px solid var(--line);
    display: flex;
    flex-direction: column;
    z-index: 10;
}

.logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 8px 20px;
}

.logo-mark {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    background: linear-gradient(145deg, #3f82ff, #245ee6);
    color: white;
    font-weight: 800;
    box-shadow: 0 8px 18px rgba(47, 111, 237, 0.25);
}

.logo-copy {
    line-height: 1.05;
}

.logo-copy strong {
    display: block;
    font-size: 15px;
    letter-spacing: -0.2px;
}

.logo-copy span {
    display: block;
    margin-top: 5px;
    font-size: 9px;
    letter-spacing: 1px;
    color: var(--muted);
}

.nav-section {
    margin: 8px 0 16px;
}

.nav-title {
    padding: 0 10px 7px;
    font-size: 10px;
    color: #a1a9b7;
    letter-spacing: 0.7px;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 38px;
    padding: 0 10px;
    border-radius: 9px;
    color: var(--text-2);
    text-decoration: none;
    font-size: 13px;
    margin: 2px 0;
}

.nav-link:hover {
    background: #f7f9fc;
}

.nav-link.active {
    color: var(--primary);
    background: var(--primary-soft);
    font-weight: 700;
}

.nav-icon {
    width: 18px;
    height: 18px;
    display: inline-grid;
    place-items: center;
    border-radius: 5px;
    font-size: 11px;
    border: 1px solid currentColor;
    opacity: 0.85;
}

.sidebar-footer {
    margin-top: auto;
    padding: 12px 10px 2px;
}

.user-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    border-radius: 10px;
    background: #f7f9fd;
}

.avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    background: #e6efff;
    color: var(--primary);
    font-weight: 800;
    font-size: 12px;
}

.user-meta strong {
    display: block;
    font-size: 12px;
}

.user-meta span {
    display: block;
    margin-top: 3px;
    font-size: 10px;
    color: var(--muted);
}

.workspace {
    min-width: 0;
}

.topbar {
    height: 58px;
    padding: 0 24px;
    border-bottom: 1px solid var(--line);
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 8;
}

.breadcrumb {
    font-size: 12px;
    color: var(--muted);
}

.breadcrumb strong {
    color: var(--text);
}

.top-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.env-chip,
.status-chip,
.soft-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    min-height: 28px;
    padding: 0 10px;
    border-radius: 999px;
    background: #f7f9fc;
    border: 1px solid var(--line);
    color: var(--text-2);
    font-size: 11px;
    font-weight: 600;
}

.content {
    padding: 24px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: flex-start;
    margin-bottom: 18px;
}

.page-title {
    margin: 0;
    font-size: 23px;
    letter-spacing: -0.5px;
}

.page-subtitle {
    margin: 7px 0 0;
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
}

.panel {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

.panel-flat {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
}

.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 15px 17px;
    border-bottom: 1px solid var(--line);
}

.panel-title {
    margin: 0;
    font-size: 13px;
    font-weight: 700;
}

.panel-body {
    padding: 17px;
}

.btn {
    min-height: 36px;
    padding: 0 15px;
    border: 1px solid transparent;
    border-radius: 8px;
    background: var(--primary);
    color: white;
    font-weight: 700;
    font-size: 12px;
    transition: 0.15s ease;
}

.btn:hover {
    background: var(--primary-dark);
}

.btn:disabled {
    opacity: 0.55;
    cursor: wait;
}

.btn.secondary {
    color: var(--text-2);
    background: white;
    border-color: var(--line-strong);
}

.btn.secondary:hover {
    background: #f8fafd;
}

.btn.ghost {
    color: var(--primary);
    background: var(--primary-soft);
}

.input,
.select,
.textarea {
    width: 100%;
    border: 1px solid var(--line-strong);
    border-radius: 9px;
    background: white;
    color: var(--text);
    outline: none;
    transition: 0.15s ease;
}

.input,
.select {
    height: 38px;
    padding: 0 11px;
}

.textarea {
    min-height: 88px;
    padding: 12px 13px;
    resize: vertical;
    line-height: 1.6;
}

.input:focus,
.select:focus,
.textarea:focus {
    border-color: #9dbcf7;
    box-shadow: 0 0 0 3px rgba(47, 111, 237, 0.08);
}

.form-label {
    display: block;
    margin: 0 0 6px;
    font-size: 11px;
    font-weight: 700;
    color: var(--text-2);
}

.grid-2 {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.grid-3 {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.grid-4 {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
}

.muted {
    color: var(--muted);
}

.code-box,
.raw-box {
    margin: 0;
    padding: 15px;
    border-radius: 10px;
    background: #111b2f;
    color: #dae4f4;
    white-space: pre-wrap;
    word-break: break-word;
    overflow: auto;
    max-height: 520px;
    font: 11px/1.65 "SFMono-Regular", Consolas, monospace;
}

.empty {
    text-align: center;
    color: var(--muted);
    padding: 34px 18px;
    font-size: 12px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 16px;
}

.kpi {
    padding: 16px;
    background: white;
    border: 1px solid var(--line);
    border-radius: 12px;
    box-shadow: var(--shadow);
}

.kpi-label {
    font-size: 11px;
    color: var(--muted);
}

.kpi-value {
    margin-top: 8px;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.kpi-note {
    margin-top: 6px;
    font-size: 10px;
    color: var(--muted);
}

.table-wrap {
    overflow: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
}

th {
    text-align: left;
    font-weight: 700;
    color: var(--muted);
    padding: 11px 10px;
    border-bottom: 1px solid var(--line);
    background: #fafbfe;
    white-space: nowrap;
}

td {
    padding: 11px 10px;
    border-bottom: 1px solid #eef1f6;
    color: var(--text-2);
    vertical-align: top;
}

tbody tr:hover {
    background: #fbfcff;
}

.table-action {
    color: var(--primary);
    font-weight: 700;
    text-decoration: none;
    cursor: pointer;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    min-height: 23px;
    padding: 0 8px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    background: #f3f5f9;
    color: var(--text-2);
}

.badge.answer,
.badge.pass,
.badge.success {
    background: var(--green-soft);
    color: var(--green);
}

.badge.clarify,
.badge.warning {
    background: var(--yellow-soft);
    color: var(--yellow);
}

.badge.conflict,
.badge.fail,
.badge.error {
    background: var(--red-soft);
    color: var(--red);
}

.badge.refuse {
    background: #fff3f1;
    color: #c9573b;
}

.badge.no_access {
    background: var(--purple-soft);
    color: var(--purple);
}

.decision-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: currentColor;
}

/* Chat */
.chat-content {
    padding: 0;
    height: calc(100vh - 58px);
    overflow: hidden;
}

.chat-grid {
    height: 100%;
    display: grid;
    grid-template-columns: 236px minmax(420px, 1fr) 314px;
    background: white;
}

.chat-history {
    border-right: 1px solid var(--line);
    background: #fbfcff;
    display: flex;
    flex-direction: column;
    min-height: 0;
}

.chat-history-head {
    padding: 15px 14px 11px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.history-list {
    padding: 0 9px 12px;
    overflow: auto;
}

.history-item {
    display: block;
    padding: 10px 9px;
    border-radius: 8px;
    text-decoration: none;
    margin-bottom: 3px;
}

.history-item:hover,
.history-item.active {
    background: white;
    box-shadow: 0 4px 14px rgba(31, 45, 70, 0.05);
}

.history-title {
    display: block;
    font-size: 11px;
    color: var(--text-2);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.history-time {
    display: block;
    margin-top: 4px;
    font-size: 9px;
    color: #a2aaba;
}

.chat-main {
    min-width: 0;
    background: #f8faff;
    display: flex;
    flex-direction: column;
}

.chat-scroll {
    flex: 1;
    min-height: 0;
    overflow: auto;
    padding: 22px 26px 18px;
}

.chat-empty {
    min-height: 100%;
    display: grid;
    place-items: center;
}

.chat-empty-inner {
    max-width: 540px;
    text-align: center;
}

.empty-icon {
    width: 46px;
    height: 46px;
    margin: 0 auto 13px;
    border-radius: 14px;
    display: grid;
    place-items: center;
    color: var(--primary);
    background: var(--primary-soft);
    font-size: 22px;
}

.chat-empty h2 {
    margin: 0;
    font-size: 21px;
}

.chat-empty p {
    margin: 8px 0 15px;
    color: var(--muted);
    font-size: 11px;
}

.domain-tabs,
.quick-list {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 7px;
}

.domain-tab,
.quick-btn {
    border: 1px solid var(--line);
    background: white;
    border-radius: 999px;
    padding: 7px 10px;
    color: var(--text-2);
    font-size: 10px;
}

.domain-tab.active {
    color: var(--primary);
    border-color: #b8cef9;
    background: var(--primary-soft);
    font-weight: 700;
}

.quick-list {
    margin-top: 14px;
}

.quick-btn:hover {
    color: var(--primary);
    border-color: #b8cef9;
}

.message-query {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 14px;
}

.query-bubble {
    max-width: 76%;
    padding: 10px 13px;
    background: #eef3fb;
    border-radius: 12px 12px 3px 12px;
    font-size: 12px;
    line-height: 1.55;
}

.answer-card {
    background: white;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 16px;
    box-shadow: var(--shadow);
}

.answer-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 12px;
}

.answer-state {
    display: flex;
    align-items: center;
    gap: 8px;
}

.answer-title {
    font-size: 12px;
    font-weight: 800;
}

.answer-meta {
    color: var(--muted);
    font-size: 9px;
}

.answer-text {
    color: #344054;
    font-size: 12px;
    line-height: 1.8;
}

.clarify-box,
.risk-box {
    margin-top: 12px;
    padding: 11px 12px;
    border-radius: 9px;
    background: #fffaf0;
    border: 1px solid #f6e3b8;
    font-size: 11px;
    line-height: 1.6;
}

.chat-composer-wrap {
    padding: 0 22px 18px;
}

.chat-composer {
    background: white;
    border: 1px solid var(--line-strong);
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(31, 45, 70, 0.06);
    padding: 12px;
}

.chat-composer .textarea {
    min-height: 54px;
    max-height: 120px;
    border: 0;
    padding: 2px 2px 8px;
    box-shadow: none;
}

.composer-footer {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
    border-top: 1px solid #f0f2f6;
    padding-top: 9px;
}

.composer-left {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.mini-select {
    height: 30px;
    border: 0;
    background: #f7f9fc;
    border-radius: 7px;
    color: var(--text-2);
    font-size: 10px;
    padding: 0 8px;
}

.switch-label {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    color: var(--text-2);
}

.advanced-config {
    margin-top: 10px;
    border-top: 1px dashed var(--line);
    padding-top: 9px;
}

.advanced-config summary {
    cursor: pointer;
    font-size: 10px;
    color: var(--muted);
}

.advanced-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin-top: 10px;
}

.advanced-grid .input {
    height: 32px;
    font-size: 10px;
}

.citation-panel {
    border-left: 1px solid var(--line);
    background: white;
    min-height: 0;
    display: flex;
    flex-direction: column;
}

.citation-list {
    padding: 12px;
    overflow: auto;
}

.citation-card {
    padding: 12px;
    border: 1px solid var(--line);
    border-radius: 10px;
    margin-bottom: 9px;
    background: #fff;
}

.citation-index {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 7px;
}

.citation-card h4 {
    margin: 0;
    font-size: 11px;
}

.citation-meta {
    margin-top: 5px;
    color: var(--muted);
    font-size: 9px;
    line-height: 1.5;
}

.citation-text {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #f0f2f6;
    color: var(--text-2);
    font-size: 10px;
    line-height: 1.55;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Trace */
.trace-toolbar,
.eval-toolbar,
.badcase-toolbar {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto auto;
    gap: 9px;
    padding: 14px;
}

.trace-summary {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 14px;
}

.trace-step {
    position: relative;
    display: grid;
    grid-template-columns: 34px minmax(0, 1fr);
    gap: 12px;
    padding: 14px 15px;
    background: white;
    border: 1px solid var(--line);
    border-radius: 11px;
    margin-bottom: 10px;
}

.trace-step-num {
    width: 30px;
    height: 30px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: var(--primary-soft);
    color: var(--primary);
    font-weight: 800;
    font-size: 11px;
}

.trace-step h4 {
    margin: 1px 0 6px;
    font-size: 12px;
}

.trace-step p {
    margin: 0;
    font-size: 10px;
    color: var(--text-2);
    line-height: 1.65;
}

.trace-data-line {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}

/* Eval */
.metric-board {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 15px;
}

.metric-card {
    background: white;
    border: 1px solid var(--line);
    border-radius: 11px;
    padding: 14px;
}

.metric-name {
    font-size: 10px;
    color: var(--muted);
}

.metric-main {
    margin-top: 8px;
    font-size: 22px;
    font-weight: 800;
}

.metric-bar {
    height: 5px;
    border-radius: 999px;
    background: #eef2f7;
    overflow: hidden;
    margin-top: 10px;
}

.metric-bar > span {
    display: block;
    height: 100%;
    background: var(--primary);
    border-radius: inherit;
}

.eval-toolbar {
    grid-template-columns: 160px 130px minmax(0, 1fr) auto;
}

/* Badcase */
.badcase-layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 340px;
    gap: 14px;
}

.badcase-toolbar {
    grid-template-columns: minmax(0, 1fr) 110px auto;
}

.badcase-row {
    cursor: pointer;
}

.badcase-row.selected {
    background: #f2f6ff;
}

.detail-section {
    padding: 13px 15px;
    border-bottom: 1px solid var(--line);
}

.detail-section:last-child {
    border-bottom: 0;
}

.detail-label {
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    color: var(--muted);
    margin-bottom: 6px;
}

.detail-value {
    font-size: 11px;
    line-height: 1.65;
    color: var(--text-2);
    word-break: break-word;
}

.loading-overlay {
    position: fixed;
    inset: 0;
    background: rgba(245, 247, 251, 0.72);
    display: none;
    place-items: center;
    z-index: 50;
    backdrop-filter: blur(2px);
}

.loading-overlay.show {
    display: grid;
}

.loading-card {
    width: min(360px, calc(100vw - 36px));
    background: white;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 20px 50px rgba(31, 45, 70, 0.14);
}

.spinner {
    width: 28px;
    height: 28px;
    margin: 0 auto 12px;
    border: 3px solid #e5edfb;
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@media (max-width: 1180px) {
    .app-shell {
        grid-template-columns: 190px minmax(0, 1fr);
    }

    .chat-grid {
        grid-template-columns: 210px minmax(360px, 1fr) 280px;
    }

    .kpi-grid,
    .metric-board,
    .trace-summary {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 900px) {
    .app-shell {
        display: block;
    }

    .sidebar {
        display: none;
    }

    .chat-content {
        height: calc(100vh - 58px);
    }

    .chat-grid {
        grid-template-columns: 1fr;
    }

    .chat-history,
    .citation-panel {
        display: none;
    }

    .badcase-layout {
        grid-template-columns: 1fr;
    }

    .eval-toolbar,
    .trace-toolbar,
    .badcase-toolbar {
        grid-template-columns: 1fr;
    }

    .grid-2,
    .grid-3,
    .grid-4 {
        grid-template-columns: 1fr;
    }
}
'''


FILES["frontend/common.js"] = r'''async function getJSON(url) {
    const response = await fetch(url);

    if (!response.ok) {
        const text = await response.text();
        throw new Error(`${response.status} ${text}`);
    }

    return await response.json();
}


async function postJSON(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const text = await response.text();
        throw new Error(`${response.status} ${text}`);
    }

    return await response.json();
}


function pretty(data) {
    return JSON.stringify(data, null, 2);
}


function setLoading(button, loading) {
    if (!button) return;

    button.disabled = loading;
    button.dataset.oldText =
        button.dataset.oldText || button.innerText;

    button.innerText = loading
        ? "处理中..."
        : button.dataset.oldText;
}


function escapeHTML(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function safeText(value, fallback = "-") {
    if (value === null || value === undefined || value === "") {
        return fallback;
    }
    return String(value);
}


function pick(obj, keys, fallback = "-") {
    if (!obj) return fallback;

    for (const key of keys) {
        if (obj[key] !== undefined && obj[key] !== null && obj[key] !== "") {
            return obj[key];
        }
    }

    return fallback;
}


function badge(value, extra = "") {
    const text = safeText(value);
    const cls = String(value || "")
        .toLowerCase()
        .replaceAll(" ", "_");

    return `<span class="badge ${cls} ${extra}">${escapeHTML(text)}</span>`;
}


function formatPercent(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return "-";
    if (n <= 1) return `${(n * 100).toFixed(1)}%`;
    return `${n.toFixed(1)}%`;
}


function formatNumber(value, digits = 2) {
    const n = Number(value);
    if (!Number.isFinite(n)) return safeText(value);
    return n.toFixed(digits);
}


function applyActiveNav() {
    const page = document.body.dataset.page;

    document.querySelectorAll("[data-nav]").forEach((node) => {
        if (node.dataset.nav === page) {
            node.classList.add("active");
        }
    });
}


document.addEventListener("DOMContentLoaded", applyActiveNav);
'''


CHAT_HTML = r'''<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>KnowFlow · 智能问答</title>
    <link rel="stylesheet" href="/ui/styles.css">
</head>
<body data-page="chat">
<div class="app-shell">
    <aside class="sidebar">
        <div class="logo">
            <div class="logo-mark">K</div>
            <div class="logo-copy">
                <strong>KnowFlow</strong>
                <span>KNOWLEDGE AGENT</span>
            </div>
        </div>

        <div class="nav-section">
            <div class="nav-title">工作台</div>
            <a class="nav-link" data-nav="chat" href="/ui/chat.html">
                <span class="nav-icon">问</span>智能问答
            </a>
            <a class="nav-link" data-nav="trace" href="/ui/trace.html">
                <span class="nav-icon">迹</span>Trace 追踪
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-title">治理与评测</div>
            <a class="nav-link" data-nav="eval" href="/ui/eval.html">
                <span class="nav-icon">评</span>评测中心
            </a>
            <a class="nav-link" data-nav="badcase" href="/ui/badcase.html">
                <span class="nav-icon">错</span>Badcase 池
            </a>
        </div>

        <div class="sidebar-footer">
            <div class="user-card">
                <div class="avatar">演</div>
                <div class="user-meta">
                    <strong>演示员工</strong>
                    <span>demo@company.com</span>
                </div>
            </div>
        </div>
    </aside>

    <section class="workspace">
        <header class="topbar">
            <div class="breadcrumb">KnowFlow / <strong>智能问答</strong></div>
            <div class="top-actions">
                <span class="env-chip">演示企业 · 私有可信知识域</span>
            </div>
        </header>

        <main class="chat-content">
            <div class="chat-grid">
                <aside class="chat-history">
                    <div class="chat-history-head">
                        <strong style="font-size:12px">会话历史</strong>
                        <span class="soft-chip">+</span>
                    </div>
                    <div class="history-list">
                        <a class="history-item active" href="#">
                            <span class="history-title">差旅报销需要哪些材料？</span>
                            <span class="history-time">10分钟前</span>
                        </a>
                        <a class="history-item" href="#">
                            <span class="history-title">新员工转正流程是什么？</span>
                            <span class="history-time">1小时前</span>
                        </a>
                        <a class="history-item" href="#">
                            <span class="history-title">产品 A 最新退款规则是什么？</span>
                            <span class="history-time">昨天</span>
                        </a>
                        <a class="history-item" href="#">
                            <span class="history-title">客服话术模板在哪里？</span>
                            <span class="history-time">3天前</span>
                        </a>
                        <a class="history-item" href="#">
                            <span class="history-title">2025 福利假期政策</span>
                            <span class="history-time">上周</span>
                        </a>
                    </div>
                </aside>

                <section class="chat-main">
                    <div class="chat-scroll" id="chatScroll">
                        <div class="chat-empty" id="emptyState">
                            <div class="chat-empty-inner">
                                <div class="empty-icon">□</div>
                                <h2>今天想查什么？</h2>
                                <p>已连接企业可信治理知识体系，可放心提问</p>
                                <div class="domain-tabs">
                                    <button class="domain-tab active" type="button">全部</button>
                                    <button class="domain-tab" type="button">HR</button>
                                    <button class="domain-tab" type="button">财务</button>
                                    <button class="domain-tab" type="button">产品</button>
                                    <button class="domain-tab" type="button">客服</button>
                                </div>
                                <div class="quick-list">
                                    <button class="quick-btn" data-query="现在一线城市出差住宿上限是多少？" type="button">一线城市住宿上限？</button>
                                    <button class="quick-btn" data-query="试用期多久？" type="button">试用期多久？</button>
                                    <button class="quick-btn" data-query="产品A付款10天，核心付费功能用了2次，可以退款吗？" type="button">产品 A 退款规则</button>
                                    <button class="quick-btn" data-query="公司今年会不会裁员？" type="button">无依据问题测试</button>
                                </div>
                            </div>
                        </div>

                        <div id="conversation" style="display:none"></div>
                    </div>

                    <div class="chat-composer-wrap">
                        <div class="chat-composer">
                            <textarea id="query" class="textarea" placeholder="输入您的问题，如：试用期如何计算？">试用期多久？</textarea>
                            <div class="composer-footer">
                                <div class="composer-left">
                                    <select id="preset" class="mini-select">
                                        <option value="hr">HR 普通员工</option>
                                        <option value="finance">Finance 普通员工</option>
                                        <option value="product">Product 普通员工</option>
                                        <option value="service">Service 普通员工</option>
                                        <option value="finance_manager">Finance Manager</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                    <span class="switch-label">● 严格基于知识库判断</span>
                                </div>
                                <button id="sendBtn" class="btn" type="button">发送问题</button>
                            </div>

                            <details class="advanced-config">
                                <summary>演示身份与权限设置</summary>
                                <div class="advanced-grid">
                                    <input id="userId" class="input" value="UI001" placeholder="User ID">
                                    <input id="department" class="input" value="hr" placeholder="Department">
                                    <input id="role" class="input" value="employee" placeholder="Role">
                                    <input id="kbIds" class="input" value="KB_HR_PUBLIC" placeholder="Authorized KB IDs">
                                </div>
                            </details>
                        </div>
                    </div>
                </section>

                <aside class="citation-panel">
                    <div class="panel-header">
                        <h3 class="panel-title">来源依据与引用</h3>
                        <span class="soft-chip" id="citationCount">0</span>
                    </div>
                    <div class="citation-list" id="citationList">
                        <div class="empty">生成判断后，相关可信证据将在此处展示。</div>
                    </div>
                </aside>
            </div>
        </main>
    </section>
</div>

<script src="/ui/common.js"></script>
<script>
const PRESETS = {
    hr: { department: "hr", role: "employee", kb: ["KB_HR_PUBLIC"] },
    finance: { department: "finance", role: "employee", kb: ["KB_FINANCE_PUBLIC"] },
    product: { department: "product", role: "employee", kb: ["KB_PRODUCT_PUBLIC"] },
    service: { department: "service", role: "employee", kb: ["KB_SERVICE_PUBLIC"] },
    finance_manager: {
        department: "finance",
        role: "finance_manager",
        kb: ["KB_FINANCE_PUBLIC", "KB_FINANCE_PRIVATE"]
    },
    admin: {
        department: "admin",
        role: "admin",
        kb: ["KB_FINANCE_PUBLIC", "KB_HR_PUBLIC", "KB_PRODUCT_PUBLIC", "KB_SERVICE_PUBLIC", "KB_FINANCE_PRIVATE"]
    }
};

const STATE_TEXT = {
    answer: "证据充分 · 可回答",
    clarify: "需要补充确认",
    conflict: "发现知识冲突",
    refuse: "暂无可靠依据",
    no_access: "无访问权限"
};

function updatePreset(key) {
    const p = PRESETS[key];
    if (!p) return;
    document.getElementById("department").value = p.department;
    document.getElementById("role").value = p.role;
    document.getElementById("kbIds").value = p.kb.join(",");
}

function renderCitations(data) {
    const list = document.getElementById("citationList");
    const count = document.getElementById("citationCount");
    const citations = Array.isArray(data.citations) ? data.citations : [];

    count.textContent = String(citations.length);

    if (!citations.length) {
        const noAccess = data.decision === "no_access";
        list.innerHTML = `<div class="empty">${noAccess
            ? "由于权限受限，未检索或加载相关原文内容。"
            : "当前判断没有可展示的 Citation。"}</div>`;
        return;
    }

    list.innerHTML = citations.map((item, index) => {
        const title = pick(item, ["title", "document_title", "document_id"], "企业知识文档");
        const version = pick(item, ["version_no", "version"], "-");
        const section = pick(item, ["section"], "-");
        const page = pick(item, ["page"], "-");
        const text = pick(item, ["original_text", "text"], "");

        return `
            <div class="citation-card">
                <div class="citation-index">
                    <h4>[${index + 1}] ${escapeHTML(title)}</h4>
                    ${badge("已引用", "success")}
                </div>
                <div class="citation-meta">版本：${escapeHTML(version)} · 章节：${escapeHTML(section)} · 页码：${escapeHTML(page)}</div>
                <div class="citation-text">${escapeHTML(text)}</div>
            </div>
        `;
    }).join("");
}

function renderConversation(query, data) {
    document.getElementById("emptyState").style.display = "none";
    const conversation = document.getElementById("conversation");
    conversation.style.display = "block";

    const decision = data.decision || "-";
    const title = STATE_TEXT[decision] || decision;
    const version = data.version_mode || "-";
    const trace = data.trace_id || "-";
    const reason = data.reason || data.message || "-";
    const clarify = data.clarifying_question || "";
    const flags = Array.isArray(data.risk_flags) ? data.risk_flags : [];

    conversation.innerHTML = `
        <div class="message-query"><div class="query-bubble">${escapeHTML(query)}</div></div>
        <div class="answer-card">
            <div class="answer-head">
                <div class="answer-state">
                    ${badge(decision)}
                    <div>
                        <div class="answer-title">${escapeHTML(title)}</div>
                        <div class="answer-meta">${escapeHTML(data.domain || "-")} · ${escapeHTML(version)}</div>
                    </div>
                </div>
                <span class="soft-chip">${escapeHTML(trace)}</span>
            </div>
            <div class="answer-text">${escapeHTML(reason)}</div>
            ${clarify ? `<div class="clarify-box"><strong>需要您补充：</strong><br>${escapeHTML(clarify)}</div>` : ""}
            ${flags.length ? `<div class="risk-box"><strong>Risk Flags：</strong> ${flags.map(escapeHTML).join(" / ")}</div>` : ""}
        </div>
    `;

    renderCitations(data);
    document.getElementById("chatScroll").scrollTop = 0;
}

async function submitQuestion() {
    const button = document.getElementById("sendBtn");
    const query = document.getElementById("query").value.trim();

    if (!query) return;

    setLoading(button, true);

    try {
        const kbIds = document.getElementById("kbIds").value
            .split(",")
            .map((v) => v.trim())
            .filter(Boolean);

        const payload = {
            query,
            user: {
                user_id: document.getElementById("userId").value,
                department: document.getElementById("department").value,
                role: document.getElementById("role").value,
                authorized_kb_ids: kbIds
            }
        };

        const data = await postJSON("/chat", payload);
        renderConversation(query, data);
    } catch (error) {
        renderConversation(query, {
            decision: "refuse",
            reason: `请求失败：${String(error)}`,
            citations: []
        });
    } finally {
        setLoading(button, false);
    }
}

document.getElementById("preset").addEventListener("change", (event) => {
    updatePreset(event.target.value);
});

document.getElementById("sendBtn").addEventListener("click", submitQuestion);

document.getElementById("query").addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        submitQuestion();
    }
});

document.querySelectorAll(".quick-btn").forEach((button) => {
    button.addEventListener("click", () => {
        document.getElementById("query").value = button.dataset.query || "";
        submitQuestion();
    });
});
</script>
</body>
</html>
'''


TRACE_HTML = r'''<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>KnowFlow · Trace</title>
    <link rel="stylesheet" href="/ui/styles.css">
</head>
<body data-page="trace">
<div class="app-shell">
    <aside class="sidebar">
        <div class="logo">
            <div class="logo-mark">K</div>
            <div class="logo-copy"><strong>KnowFlow</strong><span>KNOWLEDGE AGENT</span></div>
        </div>
        <div class="nav-section">
            <div class="nav-title">工作台</div>
            <a class="nav-link" data-nav="chat" href="/ui/chat.html"><span class="nav-icon">问</span>智能问答</a>
            <a class="nav-link" data-nav="trace" href="/ui/trace.html"><span class="nav-icon">迹</span>Trace 追踪</a>
        </div>
        <div class="nav-section">
            <div class="nav-title">KnowledgeOps</div>
            <a class="nav-link" data-nav="badcase" href="/ui/badcase.html"><span class="nav-icon">错</span>Badcase 池</a>
        </div>
        <div class="nav-section">
            <div class="nav-title">评测中心</div>
            <a class="nav-link" data-nav="eval" href="/ui/eval.html"><span class="nav-icon">评</span>评测任务</a>
        </div>
        <div class="sidebar-footer">
            <div class="user-card"><div class="avatar">管</div><div class="user-meta"><strong>演示企业管理员</strong><span>admin@company.com</span></div></div>
        </div>
    </aside>

    <section class="workspace">
        <header class="topbar">
            <div class="breadcrumb">KnowFlow / 追踪诊断 / <strong>Trace</strong></div>
            <div class="top-actions"><span class="env-chip">当前知识库 · 全部文档</span></div>
        </header>

        <main class="content">
            <div class="page-header">
                <div>
                    <h1 class="page-title">请求链路追踪</h1>
                    <p class="page-subtitle">还原 Domain、Permission、Version、Retrieval、Evidence State 与 Citation，快速定位 Badcase 根因。</p>
                </div>
            </div>

            <section class="panel" style="margin-bottom:14px">
                <div class="trace-toolbar">
                    <input id="traceId" class="input" placeholder="输入 trace_id，例如 TR-...">
                    <button id="loadBtn" class="btn">查询 Trace</button>
                    <button id="recentBtn" class="btn secondary">最近 20 条</button>
                </div>
            </section>

            <div id="traceView">
                <div class="panel"><div class="empty">输入 trace_id，或查看最近 20 条请求。</div></div>
            </div>
        </main>
    </section>
</div>

<script src="/ui/common.js"></script>
<script>
const traceView = document.getElementById("traceView");

function len(value) {
    return Array.isArray(value) ? value.length : 0;
}

function renderTrace(item) {
    const retrieved = item.retrieved_chunks || [];
    const citations = item.citations || [];
    const permission = item.permission_filter || {};
    const version = item.version_filter || {};

    traceView.innerHTML = `
        <div class="trace-summary">
            <div class="kpi"><div class="kpi-label">Domain</div><div class="kpi-value" style="font-size:18px">${escapeHTML(item.domain || "-")}</div><div class="kpi-note">路由结果</div></div>
            <div class="kpi"><div class="kpi-label">Decision</div><div class="kpi-value" style="font-size:18px">${escapeHTML(item.decision || "-")}</div><div class="kpi-note">Evidence State</div></div>
            <div class="kpi"><div class="kpi-label">Retrieved</div><div class="kpi-value">${len(retrieved)}</div><div class="kpi-note">进入 Trace 的 chunks</div></div>
            <div class="kpi"><div class="kpi-label">Latency</div><div class="kpi-value" style="font-size:18px">${escapeHTML(safeText(item.latency_ms))} ms</div><div class="kpi-note">端到端耗时</div></div>
        </div>

        <div class="panel" style="margin-bottom:14px">
            <div class="panel-header"><h3 class="panel-title">Query</h3>${badge(item.trace_id || "trace")}</div>
            <div class="panel-body" style="font-size:13px;line-height:1.7">${escapeHTML(item.query || "-")}</div>
        </div>

        <div class="trace-step">
            <div class="trace-step-num">1</div>
            <div>
                <h4>Domain Router</h4>
                <p>确定问题进入哪个企业知识域。</p>
                <div class="trace-data-line">${badge(item.domain || "-")}</div>
            </div>
        </div>

        <div class="trace-step">
            <div class="trace-step-num">2</div>
            <div>
                <h4>Permission & Version Scope</h4>
                <p>在检索前完成访问权限和版本范围约束。</p>
                <div class="trace-data-line">
                    ${badge(pick(permission, ["permission_decision", "decision"], "allowed"))}
                    ${badge(item.version_mode || pick(version, ["version_mode"], "-"))}
                    ${item.query_date ? badge(`query_date=${item.query_date}`) : ""}
                </div>
            </div>
        </div>

        <div class="trace-step">
            <div class="trace-step-num">3</div>
            <div>
                <h4>Retrieval & Rerank</h4>
                <p>记录进入最终判断的 Chunk 与排序信息。</p>
                <div class="trace-data-line">
                    ${badge(`${len(retrieved)} chunks`)}
                    ${badge(`${len(item.rerank_scores || [])} rerank scores`)}
                </div>
            </div>
        </div>

        <div class="trace-step">
            <div class="trace-step-num">4</div>
            <div>
                <h4>Evidence State & Citation</h4>
                <p>最终判断以及可追溯证据。</p>
                <div class="trace-data-line">
                    ${badge(item.decision || "-")}
                    ${badge(`${len(citations)} citations`)}
                    ${item.prompt_version ? badge(item.prompt_version) : ""}
                </div>
            </div>
        </div>

        <details class="panel" style="margin-top:14px">
            <summary class="panel-header" style="cursor:pointer"><h3 class="panel-title">Raw Trace JSON</h3></summary>
            <div class="panel-body"><pre class="raw-box">${escapeHTML(pretty(item))}</pre></div>
        </details>
    `;
}

function renderRecent(data) {
    const items = data.items || [];
    traceView.innerHTML = `
        <section class="panel">
            <div class="panel-header"><h3 class="panel-title">最近请求</h3><span class="soft-chip">${items.length} 条</span></div>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>Trace ID</th><th>Query</th><th>Domain</th><th>Decision</th><th>Latency</th><th>操作</th></tr></thead>
                    <tbody>
                        ${items.map((item) => `
                            <tr>
                                <td>${escapeHTML(item.trace_id || "-")}</td>
                                <td>${escapeHTML(item.query || "-")}</td>
                                <td>${badge(item.domain || "-")}</td>
                                <td>${badge(item.decision || "-")}</td>
                                <td>${escapeHTML(safeText(item.latency_ms))} ms</td>
                                <td><a class="table-action" data-trace="${escapeHTML(item.trace_id || "")}">查看</a></td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        </section>
    `;

    traceView.querySelectorAll("[data-trace]").forEach((node) => {
        node.addEventListener("click", async () => {
            const id = node.dataset.trace;
            document.getElementById("traceId").value = id;
            const item = await getJSON(`/ops/traces/${encodeURIComponent(id)}`);
            renderTrace(item);
        });
    });
}

document.getElementById("loadBtn").addEventListener("click", async () => {
    try {
        const id = document.getElementById("traceId").value.trim();
        if (!id) return;
        const data = await getJSON(`/ops/traces/${encodeURIComponent(id)}`);
        renderTrace(data);
    } catch (error) {
        traceView.innerHTML = `<div class="panel"><div class="empty" style="color:var(--red)">${escapeHTML(String(error))}</div></div>`;
    }
});

document.getElementById("recentBtn").addEventListener("click", async () => {
    try {
        const data = await getJSON("/ops/traces?limit=20");
        renderRecent(data);
    } catch (error) {
        traceView.innerHTML = `<div class="panel"><div class="empty" style="color:var(--red)">${escapeHTML(String(error))}</div></div>`;
    }
});
</script>
</body>
</html>
'''


EVAL_HTML = r'''<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>KnowFlow · Eval</title>
    <link rel="stylesheet" href="/ui/styles.css">
</head>
<body data-page="eval">
<div class="app-shell">
    <aside class="sidebar">
        <div class="logo"><div class="logo-mark">K</div><div class="logo-copy"><strong>KnowFlow</strong><span>KNOWLEDGE AGENT</span></div></div>
        <div class="nav-section">
            <div class="nav-title">工作台</div>
            <a class="nav-link" data-nav="chat" href="/ui/chat.html"><span class="nav-icon">问</span>智能问答</a>
            <a class="nav-link" data-nav="trace" href="/ui/trace.html"><span class="nav-icon">迹</span>Trace 追踪</a>
        </div>
        <div class="nav-section">
            <div class="nav-title">KnowledgeOps</div>
            <a class="nav-link" data-nav="badcase" href="/ui/badcase.html"><span class="nav-icon">错</span>Badcase 池</a>
        </div>
        <div class="nav-section">
            <div class="nav-title">评测中心</div>
            <a class="nav-link" data-nav="eval" href="/ui/eval.html"><span class="nav-icon">评</span>评测任务</a>
        </div>
        <div class="sidebar-footer"><div class="user-card"><div class="avatar">管</div><div class="user-meta"><strong>演示企业管理员</strong><span>admin@company.com</span></div></div></div>
    </aside>

    <section class="workspace">
        <header class="topbar">
            <div class="breadcrumb">KnowFlow / 评测中心 / <strong>自动评测</strong></div>
            <div class="top-actions"><span class="env-chip">Frozen Eval · S9/S10</span></div>
        </header>

        <main class="content">
            <div class="page-header">
                <div>
                    <h1 class="page-title">评测中心</h1>
                    <p class="page-subtitle">运行 Core61 / Gold100，验证 Domain、Version、Permission、Evidence State、Citation 与 Trace 是否发生回归。</p>
                </div>
            </div>

            <section class="panel" style="margin-bottom:15px">
                <div class="eval-toolbar">
                    <select id="dataset" class="select">
                        <option value="core_61">Core61</option>
                        <option value="gold_v1">Gold100</option>
                    </select>
                    <input id="limit" class="input" type="number" min="1" placeholder="Limit（可空）">
                    <input id="caseIds" class="input" placeholder="Case IDs，逗号分隔；完整运行请留空">
                    <button id="runBtn" class="btn">运行评测</button>
                </div>
            </section>

            <div id="evalView">
                <div class="kpi-grid">
                    <div class="kpi"><div class="kpi-label">Core61</div><div class="kpi-value">61/61</div><div class="kpi-note">Frozen regression baseline</div></div>
                    <div class="kpi"><div class="kpi-label">Gold100</div><div class="kpi-value">100/100</div><div class="kpi-note">Portfolio final regression</div></div>
                    <div class="kpi"><div class="kpi-label">Unauthorized Retrieval</div><div class="kpi-value">0.0</div><div class="kpi-note">权限隔离指标</div></div>
                    <div class="kpi"><div class="kpi-label">Citation Alignment</div><div class="kpi-value">1.0</div><div class="kpi-note">引用与证据一致性</div></div>
                </div>
                <div class="panel"><div class="empty">选择 Dataset 并运行评测。完整 Gold100 请将 Case IDs 与 Limit 留空。</div></div>
            </div>
        </main>
    </section>
</div>

<div class="loading-overlay" id="loadingOverlay">
    <div class="loading-card">
        <div class="spinner"></div>
        <strong>正在运行评测</strong>
        <div class="muted" style="font-size:11px;margin-top:7px">Gold100 完整回归可能需要较长时间，请保持页面打开。</div>
    </div>
</div>

<script src="/ui/common.js"></script>
<script>
const evalView = document.getElementById("evalView");
const overlay = document.getElementById("loadingOverlay");

function metricWidth(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return 0;
    const pct = n <= 1 ? n * 100 : n;
    return Math.max(0, Math.min(100, pct));
}

function renderEval(data) {
    const total = Number(data.total_cases || 0);
    const passed = Number(data.passed_cases || 0);
    const failed = Number(data.failed_cases || Math.max(0, total - passed));
    const passRate = data.pass_rate !== undefined
        ? formatPercent(data.pass_rate)
        : (total ? formatPercent(passed / total) : "-");
    const metrics = data.metrics || {};

    const metricEntries = Object.entries(metrics)
        .filter(([, value]) => typeof value === "number" || typeof value === "string")
        .slice(0, 12);

    evalView.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi"><div class="kpi-label">Total Cases</div><div class="kpi-value">${total}</div><div class="kpi-note">${escapeHTML(data.dataset_name || data.dataset || "-")}</div></div>
            <div class="kpi"><div class="kpi-label">Passed</div><div class="kpi-value" style="color:var(--green)">${passed}</div><div class="kpi-note">通过用例</div></div>
            <div class="kpi"><div class="kpi-label">Failed</div><div class="kpi-value" style="color:${failed ? "var(--red)" : "var(--green)"}">${failed}</div><div class="kpi-note">失败用例</div></div>
            <div class="kpi"><div class="kpi-label">Pass Rate</div><div class="kpi-value">${escapeHTML(passRate)}</div><div class="kpi-note">run=${escapeHTML(data.run_id || "-")}</div></div>
        </div>

        <section class="panel" style="margin-bottom:14px">
            <div class="panel-header"><h3 class="panel-title">核心指标</h3>${badge(failed ? "存在失败样本" : "全部通过", failed ? "fail" : "pass")}</div>
            <div class="panel-body">
                <div class="metric-board">
                    ${metricEntries.length ? metricEntries.map(([name, value]) => `
                        <div class="metric-card">
                            <div class="metric-name">${escapeHTML(name)}</div>
                            <div class="metric-main">${escapeHTML(safeText(value))}</div>
                            <div class="metric-bar"><span style="width:${metricWidth(value)}%"></span></div>
                        </div>
                    `).join("") : `<div class="empty" style="grid-column:1/-1">本次响应未返回独立 metrics 字段。</div>`}
                </div>
            </div>
        </section>

        <section class="panel">
            <div class="panel-header"><h3 class="panel-title">运行结果</h3><span class="soft-chip">${escapeHTML(data.run_id || "-")}</span></div>
            <div class="panel-body"><pre class="raw-box">${escapeHTML(pretty(data))}</pre></div>
        </section>
    `;
}

document.getElementById("runBtn").addEventListener("click", async () => {
    const button = document.getElementById("runBtn");
    setLoading(button, true);
    overlay.classList.add("show");

    try {
        const rawIds = document.getElementById("caseIds").value;
        const caseIds = rawIds.split(",").map((x) => x.trim()).filter(Boolean);
        const rawLimit = document.getElementById("limit").value;

        const payload = {
            dataset: document.getElementById("dataset").value,
            limit: rawLimit ? Number(rawLimit) : null,
            case_ids: caseIds
        };

        const data = await postJSON("/eval/run", payload);
        renderEval(data);
    } catch (error) {
        evalView.innerHTML = `<div class="panel"><div class="empty" style="color:var(--red)">评测失败：${escapeHTML(String(error))}</div></div>`;
    } finally {
        setLoading(button, false);
        overlay.classList.remove("show");
    }
});
</script>
</body>
</html>
'''


BADCASE_HTML = r'''<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>KnowFlow · Badcase</title>
    <link rel="stylesheet" href="/ui/styles.css">
</head>
<body data-page="badcase">
<div class="app-shell">
    <aside class="sidebar">
        <div class="logo"><div class="logo-mark">K</div><div class="logo-copy"><strong>KnowFlow</strong><span>KNOWLEDGE AGENT</span></div></div>
        <div class="nav-section">
            <div class="nav-title">工作台</div>
            <a class="nav-link" data-nav="chat" href="/ui/chat.html"><span class="nav-icon">问</span>智能问答</a>
            <a class="nav-link" data-nav="trace" href="/ui/trace.html"><span class="nav-icon">迹</span>Trace 追踪</a>
        </div>
        <div class="nav-section">
            <div class="nav-title">KnowledgeOps</div>
            <a class="nav-link" data-nav="badcase" href="/ui/badcase.html"><span class="nav-icon">错</span>Badcase 池</a>
        </div>
        <div class="nav-section">
            <div class="nav-title">评测中心</div>
            <a class="nav-link" data-nav="eval" href="/ui/eval.html"><span class="nav-icon">评</span>评测任务</a>
        </div>
        <div class="sidebar-footer"><div class="user-card"><div class="avatar">管</div><div class="user-meta"><strong>演示企业管理员</strong><span>admin@company.com</span></div></div></div>
    </aside>

    <section class="workspace">
        <header class="topbar">
            <div class="breadcrumb">KnowFlow / KnowledgeOps / <strong>Badcase 池</strong></div>
            <div class="top-actions"><span class="env-chip">Eval Runtime Feedback Pool</span></div>
        </header>

        <main class="content">
            <div class="page-header">
                <div>
                    <h1 class="page-title">Badcase 治理反馈池</h1>
                    <p class="page-subtitle">汇总自动评测产生的失败样本，结合 Trace 进行 Root Cause Analysis 与回归治理。</p>
                </div>
            </div>

            <div class="kpi-grid" id="badcaseKpis">
                <div class="kpi"><div class="kpi-label">Runtime Badcases</div><div class="kpi-value">-</div><div class="kpi-note">当前加载数量</div></div>
                <div class="kpi"><div class="kpi-label">Decision / Logic</div><div class="kpi-value">-</div><div class="kpi-note">决策相关样本</div></div>
                <div class="kpi"><div class="kpi-label">Runtime Error</div><div class="kpi-value">-</div><div class="kpi-note">运行时异常</div></div>
                <div class="kpi"><div class="kpi-label">Trace Linked</div><div class="kpi-value">-</div><div class="kpi-note">可追踪样本</div></div>
            </div>

            <section class="panel" style="margin-bottom:14px">
                <div class="badcase-toolbar">
                    <input id="search" class="input" placeholder="搜索 Case ID / Query / Error">
                    <input id="limit" class="input" type="number" min="1" max="500" value="50">
                    <button id="loadBtn" class="btn">刷新</button>
                </div>
            </section>

            <div class="badcase-layout">
                <section class="panel">
                    <div class="panel-header"><h3 class="panel-title">Badcase 列表</h3><span class="soft-chip" id="badcaseCount">0</span></div>
                    <div class="table-wrap">
                        <table>
                            <thead><tr><th>Case</th><th>Query</th><th>Expected</th><th>Actual</th><th>Trace</th></tr></thead>
                            <tbody id="badcaseBody"><tr><td colspan="5"><div class="empty">正在加载...</div></td></tr></tbody>
                        </table>
                    </div>
                </section>

                <aside class="panel" id="detailPanel">
                    <div class="panel-header"><h3 class="panel-title">Badcase 排查链路</h3></div>
                    <div class="empty">选择左侧一条 Badcase 查看详情。</div>
                </aside>
            </div>
        </main>
    </section>
</div>

<script src="/ui/common.js"></script>
<script>
let badcases = [];
let selectedIndex = -1;

function expectedDecision(item) {
    return pick(item, ["expected_decision", "frozen_actual_decision", "expected"], "-");
}

function actualDecision(item) {
    return pick(item, ["actual_decision", "decision", "actual"], "-");
}

function renderKpis(items) {
    const logic = items.filter((x) => actualDecision(x) !== "-" || expectedDecision(x) !== "-").length;
    const runtime = items.filter((x) => String(pick(x, ["error"], "")).trim()).length;
    const linked = items.filter((x) => String(pick(x, ["trace_id"], "")).trim()).length;

    document.getElementById("badcaseKpis").innerHTML = `
        <div class="kpi"><div class="kpi-label">Runtime Badcases</div><div class="kpi-value">${items.length}</div><div class="kpi-note">当前加载数量</div></div>
        <div class="kpi"><div class="kpi-label">Decision / Logic</div><div class="kpi-value">${logic}</div><div class="kpi-note">具备决策对比字段</div></div>
        <div class="kpi"><div class="kpi-label">Runtime Error</div><div class="kpi-value">${runtime}</div><div class="kpi-note">包含 error 字段</div></div>
        <div class="kpi"><div class="kpi-label">Trace Linked</div><div class="kpi-value">${linked}</div><div class="kpi-note">具备 trace_id</div></div>
    `;
}

function renderTable(items) {
    const body = document.getElementById("badcaseBody");
    document.getElementById("badcaseCount").textContent = String(items.length);

    if (!items.length) {
        body.innerHTML = `<tr><td colspan="5"><div class="empty">当前没有匹配的 Badcase。</div></td></tr>`;
        return;
    }

    body.innerHTML = items.map((item, index) => {
        const id = pick(item, ["case_id", "source_case_id", "badcase_id"], `#${index + 1}`);
        const query = pick(item, ["query", "question"], "-");
        const expected = expectedDecision(item);
        const actual = actualDecision(item);
        const trace = pick(item, ["trace_id"], "-");

        return `
            <tr class="badcase-row ${index === selectedIndex ? "selected" : ""}" data-index="${index}">
                <td><strong>${escapeHTML(id)}</strong></td>
                <td>${escapeHTML(query)}</td>
                <td>${badge(expected)}</td>
                <td>${badge(actual)}</td>
                <td>${trace !== "-" ? `<span class="table-action">${escapeHTML(trace)}</span>` : "-"}</td>
            </tr>
        `;
    }).join("");

    body.querySelectorAll("[data-index]").forEach((row) => {
        row.addEventListener("click", () => {
            selectedIndex = Number(row.dataset.index);
            renderTable(items);
            renderDetail(items[selectedIndex]);
        });
    });
}

function renderDetail(item) {
    const panel = document.getElementById("detailPanel");
    const query = pick(item, ["query", "question"], "-");
    const id = pick(item, ["case_id", "source_case_id", "badcase_id"], "-");
    const trace = pick(item, ["trace_id"], "-");
    const error = pick(item, ["error"], "");
    const checks = pick(item, ["checks_json", "checks"], "-");
    const expected = expectedDecision(item);
    const actual = actualDecision(item);

    panel.innerHTML = `
        <div class="panel-header"><h3 class="panel-title">Badcase 排查链路</h3>${badge(id)}</div>
        <div class="detail-section">
            <div class="detail-label">Query</div>
            <div class="detail-value"><strong>${escapeHTML(query)}</strong></div>
        </div>
        <div class="detail-section">
            <div class="detail-label">Decision Comparison</div>
            <div class="detail-value">Expected ${badge(expected)} &nbsp; Actual ${badge(actual)}</div>
        </div>
        <div class="detail-section">
            <div class="detail-label">Trace</div>
            <div class="detail-value">${trace !== "-" ? `<a class="table-action" href="/ui/trace.html">${escapeHTML(trace)}</a>` : "No trace linked"}</div>
        </div>
        ${error ? `<div class="detail-section"><div class="detail-label">Runtime Error</div><div class="detail-value" style="color:var(--red)">${escapeHTML(error)}</div></div>` : ""}
        <div class="detail-section">
            <div class="detail-label">Checks</div>
            <div class="detail-value">${escapeHTML(typeof checks === "string" ? checks : pretty(checks))}</div>
        </div>
        <div class="detail-section">
            <div class="detail-label">Raw Badcase</div>
            <pre class="raw-box" style="max-height:260px">${escapeHTML(pretty(item))}</pre>
        </div>
    `;
}

function applySearch() {
    const keyword = document.getElementById("search").value.trim().toLowerCase();
    const filtered = keyword
        ? badcases.filter((item) => pretty(item).toLowerCase().includes(keyword))
        : badcases;
    selectedIndex = -1;
    renderTable(filtered);
}

async function loadBadcases() {
    const limit = document.getElementById("limit").value || "50";
    const data = await getJSON(`/ops/badcases?limit=${encodeURIComponent(limit)}`);
    badcases = data.items || [];
    renderKpis(badcases);
    applySearch();
}

document.getElementById("loadBtn").addEventListener("click", async () => {
    try {
        await loadBadcases();
    } catch (error) {
        document.getElementById("badcaseBody").innerHTML = `<tr><td colspan="5"><div class="empty" style="color:var(--red)">${escapeHTML(String(error))}</div></td></tr>`;
    }
});

document.getElementById("search").addEventListener("input", applySearch);

loadBadcases().catch((error) => {
    document.getElementById("badcaseBody").innerHTML = `<tr><td colspan="5"><div class="empty" style="color:var(--red)">${escapeHTML(String(error))}</div></td></tr>`;
});
</script>
</body>
</html>
'''


FILES["frontend/chat.html"] = CHAT_HTML
FILES["frontend/trace.html"] = TRACE_HTML
FILES["frontend/eval.html"] = EVAL_HTML
FILES["frontend/badcase.html"] = BADCASE_HTML


def main() -> None:
    print("KnowFlow S10 UI adapter")
    print("This script only updates frontend UI files.")
    print("Existing backend/API code will NOT be overwritten.")
    print("")

    for relative, content in FILES.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"updated: {path}")

    print("")
    print("UI adaptation complete.")
    print("Updated files:")
    for relative in FILES:
        print(f"- {relative}")


if __name__ == "__main__":
    main()
