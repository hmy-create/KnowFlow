from app.models import (
    EvalCase,
    EvalUser,
)
from app.services.eval_service import (
    _evaluate_sensitivity_match,
)
from app.services.eval_service import (
    _build_eval_runtime_user,
)

def build_case(
    domain: str,
    sensitivity: str | None,
    frozen_domain_actual: str | None = None,
):
    return EvalCase(
        case_id="TEST001",
        set_name="test",
        category="test",
        query="test",

        user=EvalUser(
            user_id="TEST_USER",
            department="test",
            role="employee",
            authorized_kb_ids=[],
        ),

        expected_domain=domain,

        expected_sensitivity=(
            sensitivity
        ),

        expected_version_mode=None,

        expected_permission_decision=None,

        expected_decision="answer",

        frozen_domain_actual=(
            frozen_domain_actual
        ),

        frozen_actual_decision="answer",

        frozen_pass=True,
    )


def test_finance_normal_sensitivity_matches():

    case = build_case(
        domain="Finance",
        sensitivity="Normal",
        frozen_domain_actual="Finance",
    )

    result = (
        _evaluate_sensitivity_match(
            case=case,
            actual_sensitivity="Normal",
        )
    )

    assert result is True


def test_finance_wrong_sensitivity_fails():

    case = build_case(
        domain="Finance",
        sensitivity="Restricted",
        frozen_domain_actual="Finance",
    )

    result = (
        _evaluate_sensitivity_match(
            case=case,
            actual_sensitivity="Normal",
        )
    )

    assert result is False


def test_hr_sensitivity_is_not_applicable():

    case = build_case(
        domain="HR",
        sensitivity="Normal",
        frozen_domain_actual="HR",
    )

    result = (
        _evaluate_sensitivity_match(
            case=case,
            actual_sensitivity=None,
        )
    )

    assert result is None


def test_product_sensitivity_is_not_applicable():

    case = build_case(
        domain="Product",
        sensitivity="Normal",
        frozen_domain_actual="Product",
    )

    result = (
        _evaluate_sensitivity_match(
            case=case,
            actual_sensitivity=None,
        )
    )

    assert result is None


def test_service_sensitivity_is_not_applicable():

    case = build_case(
        domain="Service",
        sensitivity="Normal",
        frozen_domain_actual="Service",
    )

    result = (
        _evaluate_sensitivity_match(
            case=case,
            actual_sensitivity=None,
        )
    )

    assert result is None



def test_frozen_actual_domain_controls_applicability():

    # 例如冻结数据中：
    # ideal domain = Finance
    # frozen actual = HR
    #
    # FastAPI migration 应保持 frozen parity，
    # 因此该 Case 不应强制检查 Finance sensitivity。
    case = build_case(
        domain="Finance",
        sensitivity="Normal",
        frozen_domain_actual="HR",
    )

    result = (
        _evaluate_sensitivity_match(
            case=case,
            actual_sensitivity=None,
        )
    )

    assert result is None

from app.services.eval_service import (
    _evaluate_version_match,
)


def test_service_version_is_not_applicable():

    case = build_case(
        domain="Service",
        sensitivity="Normal",
        frozen_domain_actual="Service",
    )

    case.expected_version_mode = "Current"

    result = (
        _evaluate_version_match(
            case=case,
            actual_version_mode=None,
        )
    )

    assert result is None


def test_other_version_is_not_applicable():

    case = build_case(
        domain="Other",
        sensitivity=None,
        frozen_domain_actual="Other",
    )

    case.expected_version_mode = "Current"

    result = (
        _evaluate_version_match(
            case=case,
            actual_version_mode=None,
        )
    )

    assert result is None


def test_finance_restricted_version_is_not_applicable():

    case = build_case(
        domain="Finance",
        sensitivity="Restricted",
        frozen_domain_actual="Finance",
    )

    case.expected_version_mode = "Current"

    result = (
        _evaluate_version_match(
            case=case,
            actual_version_mode=None,
        )
    )

    assert result is None


def test_finance_normal_version_is_checked():

    case = build_case(
        domain="Finance",
        sensitivity="Normal",
        frozen_domain_actual="Finance",
    )

    case.expected_version_mode = "Current"

    result = (
        _evaluate_version_match(
            case=case,
            actual_version_mode="Current",
        )
    )

    assert result is True


def test_finance_wrong_version_fails():

    case = build_case(
        domain="Finance",
        sensitivity="Normal",
        frozen_domain_actual="Finance",
    )

    case.expected_version_mode = "Historical"

    result = (
        _evaluate_version_match(
            case=case,
            actual_version_mode="Current",
        )
    )

    assert result is False


def test_hr_version_is_checked():

    case = build_case(
        domain="HR",
        sensitivity="Normal",
        frozen_domain_actual="HR",
    )

    case.expected_version_mode = "Historical"

    result = (
        _evaluate_version_match(
            case=case,
            actual_version_mode="Historical",
        )
    )

    assert result is True


def test_product_version_is_checked():

    case = build_case(
        domain="Product",
        sensitivity="Normal",
        frozen_domain_actual="Product",
    )

    case.expected_version_mode = "Current"

    result = (
        _evaluate_version_match(
            case=case,
            actual_version_mode="Current",
        )
    )

    assert result is True

def test_cross_domain_frozen_route_adds_public_kb():

    case = build_case(
        domain="Finance",
        sensitivity="Normal",
        frozen_domain_actual="HR",
    )

    case.user.department = "finance"

    case.user.authorized_kb_ids = [
        "KB_FINANCE_PUBLIC"
    ]

    user = (
        _build_eval_runtime_user(
            case
        )
    )

    assert (
        "KB_FINANCE_PUBLIC"
        in user[
            "authorized_kb_ids"
        ]
    )

    assert (
        "KB_HR_PUBLIC"
        in user[
            "authorized_kb_ids"
        ]
    )


def test_cross_domain_fixture_never_adds_private_kb():

    case = build_case(
        domain="Finance",
        sensitivity="Normal",
        frozen_domain_actual="HR",
    )

    case.user.authorized_kb_ids = [
        "KB_FINANCE_PUBLIC"
    ]

    user = (
        _build_eval_runtime_user(
            case
        )
    )

    assert (
        "KB_FINANCE_PRIVATE"
        not in user[
            "authorized_kb_ids"
        ]
    )