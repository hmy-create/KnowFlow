from app.core.domain_router import classify_domain
from app.core.sensitivity_router import (
    classify_finance_sensitivity,
)
from app.core.version_resolver import (
    resolve_hr_version,
    resolve_finance_version,
    resolve_product_version,
)


def route_query(query: str) -> dict:

    domain = classify_domain(query)

    sensitivity = None
    version_mode = None

    if domain == "Finance":

        sensitivity = classify_finance_sensitivity(query)

        if sensitivity == "Normal":
            version_mode = resolve_finance_version(query)

        # Restricted 不进入 Finance Version
        # 下一阶段 S4 才进行权限判断

    elif domain == "HR":

        version_mode = resolve_hr_version(query)

    elif domain == "Product":

        version_mode = resolve_product_version(query)

    elif domain == "Service":

        # Frozen POC 中 Service 没有 Version Classifier
        pass

    elif domain == "Other":

        pass

    return {
        "domain": domain,
        "sensitivity": sensitivity,
        "version_mode": version_mode,
    }