"""Convert a BDBag export into model-ready format.

Usage:
    uv run python data/prepare.py --bag ./data/bags/<bag-name>
"""
import argparse
from pathlib import Path


def prepare(bag_path: Path, output_path: Path) -> None:
    # TODO: implement dataset preparation for this subproject
    raise NotImplementedError(
        "Implement prepare() for this subproject. "
        "See docs/guides/etl-workflow.md for guidance."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bag", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/prepared"))
    args = parser.parse_args()
    prepare(args.bag, args.output)
