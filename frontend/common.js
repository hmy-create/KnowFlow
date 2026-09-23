async function getJSON(url) {
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
