import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

BACKEND_DIR = (
    REPO_ROOT
    / "backend"
)

if (
    str(BACKEND_DIR)
    not in sys.path
):
    sys.path.insert(
        0,
        str(BACKEND_DIR),
    )


from app.services.eval_service import (  # noqa: E402
    run_eval,
)


def build_parser():

    parser = argparse.ArgumentParser(
        description=(
            "KnowFlow S9 automated "
            "evaluation runner"
        )
    )

    parser.add_argument(
        "--dataset",
        default="core_61",
        choices=[
            "core_61",
            "gold_v1",
        ],
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Only run first N cases. "
            "For development only."
        ),
    )

    parser.add_argument(
        "--case-id",
        action="append",
        dest="case_ids",
        default=None,
        help=(
            "Run a specific case. "
            "Can be repeated."
        ),
    )

    return parser


def main():

    args = (
        build_parser()
        .parse_args()
    )

    print()
    print("=" * 90)
    print(
        "KnowFlow S9 Automated Eval"
    )
    print("=" * 90)

    print(
        f"dataset={args.dataset}"
    )

    if args.limit:
        print(
            f"limit={args.limit}"
        )

    if args.case_ids:
        print(
            "case_ids="
            + ",".join(
                args.case_ids
            )
        )

    print("=" * 90)
    print()

    summary = run_eval(
        dataset_name=(
            args.dataset
        ),
        limit=args.limit,
        case_ids=args.case_ids,
        progress=True,
    )

    print()
    print("=" * 90)
    print(
        "KnowFlow Eval Summary"
    )
    print("=" * 90)

    print(
        f"run_id: "
        f"{summary['run_id']}"
    )

    print(
        f"dataset: "
        f"{summary['dataset_name']}"
    )

    print(
        f"total: "
        f"{summary['total_cases']}"
    )

    print(
        f"passed: "
        f"{summary['passed_cases']}"
    )

    print(
        f"failed: "
        f"{summary['failed_cases']}"
    )

    print(
        f"pass_rate: "
        f"{summary['pass_rate']:.4f}"
    )

    print()
    print("metrics:")

    for (
        key,
        value,
    ) in (
        summary[
            "metrics"
        ].items()
    ):

        print(
            f"  {key}: "
            f"{value}"
        )

    print()
    print("reports:")

    for (
        key,
        value,
    ) in (
        summary[
            "report_paths"
        ].items()
    ):

        print(
            f"  {key}: "
            f"{value}"
        )

    print("=" * 90)

    # 方便脚本消费
    print()
    print(
        json.dumps(
            {
                "run_id":
                    summary[
                        "run_id"
                    ],

                "passed_cases":
                    summary[
                        "passed_cases"
                    ],

                "failed_cases":
                    summary[
                        "failed_cases"
                    ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()