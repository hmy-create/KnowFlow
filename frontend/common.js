async function getJSON(url) {
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
