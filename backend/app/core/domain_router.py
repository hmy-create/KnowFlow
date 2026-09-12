from app.core.llm_classifier import classify_label


DOMAIN_LABELS = [
    "HR",
    "Finance",
    "Product",
    "Service",
    "Other",
]


# 完全来自 Frozen Dify Domain_Classifier 的类别描述。
# 这里只做明确业务域信号匹配，不新增 Domain。
FROZEN_DOMAIN_TERMS = {
    "HR": (
        "入职",
        "转正",
        "试用期",
        "请假",
        "考勤",
        "人事制度",
        "新员工",
        "信息安全基础规范",
    ),

    "Finance": (
        "差旅",
        "住宿",
        "交通",
        "餐补",
        "报销",
        "发票",
        "预算",
        "财务审批",
    ),

    "Product": (
        "产品A",
        "产品 A",
        "退款",
        "取消订阅",
        "产品政策",
        "产品使用规则",
    ),

    "Service": (
        "客服",
        "投诉",
        "售后",
        "客户服务",
        "工单",
        "首次响应",
        "账号客服FAQ",
        "账号客服 FAQ",
    ),
}


def match_frozen_domain(query: str) -> str | None:
    """
    根据冻结版 Dify Domain 描述进行强信号匹配。

    只有唯一 Domain 命中时才直接返回。
    如果没有命中或同时命中多个 Domain，
    交给 LLM fallback，避免强行裁决模糊问题。
    """

    matched_domains: list[str] = []

    for domain, terms in FROZEN_DOMAIN_TERMS.items():
        if any(term in query for term in terms):
            matched_domains.append(domain)

    if len(matched_domains) == 1:
        return matched_domains[0]

    return None


def classify_domain(query: str) -> str:
    frozen_match = match_frozen_domain(query)

    if frozen_match is not None:
        print(
            f"[Router Debug] "
            f"domain_source=frozen_rule | "
            f"query={query} | "
            f"domain={frozen_match}"
        )

        return frozen_match

    print(
        f"[Router Debug] "
        f"domain_source=llm_fallback | "
        f"query={query}"
    )

    return classify_label(
        query=query,
        prompt_filename="domain.txt",
        allowed_labels=DOMAIN_LABELS,
    )