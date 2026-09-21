from app.core.domain_router import (
    classify_domain,
)
from app.core.frozen_router_guards import (
    apply_finance_sensitivity_guard,
    apply_frozen_domain_guard,
    apply_frozen_version_guard,
)
from app.core.sensitivity_router import (
    classify_finance_sensitivity,
)
from app.core.version_resolver import (
    resolve_hr_version,
    resolve_finance_version,
    resolve_product_version,
)


def route_query(
    query: str,
) -> dict:

    # ============================================================
    # S3-A Domain Router
    #
    # 第二轮暂时不修改 Domain Router。
    # 仍然完全使用原冻结 Domain 分类逻辑。
    # ============================================================
    # ============================================================
    # Frozen Domain Guard
    #
    # 对已经冻结确认的高置信 Domain 语义，
    # 使用确定性规则。
    #
    # 未命中时继续使用原 Domain Router。
    # ============================================================
    domain_guard = (
        apply_frozen_domain_guard(
            query
        )
    )

    if (
        domain_guard
        is not None
    ):

        domain = (
            domain_guard
        )

        print(
            "[Router Debug] "
            "domain_source=frozen_rule"
            f" | query={query}"
            f" | domain={domain}"
        )

    else:

        domain = (
            classify_domain(
                query
            )
        )

    sensitivity = None
    version_mode = None

    # ============================================================
    # Finance
    # ============================================================
    if domain == "Finance":

        # --------------------------------------------------------
        # Finance Sensitivity
        #
        # 第一轮已经完成：
        # Frozen deterministic guard 优先，
        # 未命中时继续使用原 LLM Sensitivity Router。
        # --------------------------------------------------------
        sensitivity_guard = (
            apply_finance_sensitivity_guard(
                query
            )
        )

        if (
            sensitivity_guard
            is not None
        ):

            sensitivity = (
                sensitivity_guard
            )

            print(
                "[Router Debug] "
                "sensitivity_source="
                "frozen_rule"
                f" | query={query}"
                f" | sensitivity="
                f"{sensitivity}"
            )

        else:

            sensitivity = (
                classify_finance_sensitivity(
                    query
                )
            )

        # --------------------------------------------------------
        # Finance Normal
        #
        # Normal 才进入 Version Resolver。
        #
        # 第二轮增加：
        #
        # Frozen Version Guard
        # ↓
        # 未命中
        # ↓
        # 原 Finance Version Resolver
        #
        # 典型修复：
        #
        # V101:
        # 2026-04-30
        # → Historical
        #
        # V102:
        # 2026-05-01
        # → Current
        # --------------------------------------------------------
        if sensitivity == "Normal":

            version_guard = (
                apply_frozen_version_guard(
                    query=query,
                    domain=domain,
                )
            )

            if (
                version_guard
                is not None
            ):

                version_mode = (
                    version_guard
                )

                print(
                    "[Router Debug] "
                    "version_source="
                    "frozen_rule"
                    f" | query={query}"
                    f" | version="
                    f"{version_mode}"
                )

            else:

                version_mode = (
                    resolve_finance_version(
                        query
                    )
                )

        # --------------------------------------------------------
        # Finance Restricted
        #
        # Frozen POC：
        #
        # Restricted
        # → 不进入 Version Resolver
        # → S4 Permission
        #
        # 所以这里必须保持 version_mode=None。
        # --------------------------------------------------------

    # ============================================================
    # HR
    # ============================================================
    elif domain == "HR":

        # --------------------------------------------------------
        # 第二轮加入 Frozen Version Guard。
        #
        # 例如：
        #
        # “2025年社会招聘员工试用期多久？”
        # → Historical
        #
        # 未命中时继续使用原 HR Version Resolver。
        # --------------------------------------------------------
        version_guard = (
            apply_frozen_version_guard(
                query=query,
                domain=domain,
            )
        )

        if (
            version_guard
            is not None
        ):

            version_mode = (
                version_guard
            )

            print(
                "[Router Debug] "
                "version_source="
                "frozen_rule"
                f" | query={query}"
                f" | version="
                f"{version_mode}"
            )

        else:

            version_mode = (
                resolve_hr_version(
                    query
                )
            )

    # ============================================================
    # Product
    # ============================================================
    elif domain == "Product":

        # --------------------------------------------------------
        # 第二轮加入 Frozen Version Guard。
        #
        # 关键修复：
        #
        # “付款后10天”
        # 是退款条件，
        # 不是 Historical 时间语义。
        #
        # “明年”
        # 也不是 Historical，
        # 而是未来语义；
        # 当前先进入 Current，
        # 后续 Evidence State 再决定是否 refuse。
        # --------------------------------------------------------
        version_guard = (
            apply_frozen_version_guard(
                query=query,
                domain=domain,
            )
        )

        if (
            version_guard
            is not None
        ):

            version_mode = (
                version_guard
            )

            print(
                "[Router Debug] "
                "version_source="
                "frozen_rule"
                f" | query={query}"
                f" | version="
                f"{version_mode}"
            )

        else:

            version_mode = (
                resolve_product_version(
                    query
                )
            )

    # ============================================================
    # Service
    #
    # Frozen POC 中 Service 没有独立 Version Resolver。
    # ============================================================
    elif domain == "Service":

        pass

    # ============================================================
    # Other
    # ============================================================
    elif domain == "Other":

        pass

    # ============================================================
    # Structured Router Output
    # ============================================================
    return {
        "domain": domain,
        "sensitivity": sensitivity,
        "version_mode": version_mode,
    }