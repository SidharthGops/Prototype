from __future__ import annotations

import argparse
from pathlib import Path

from gradio_client import Client, handle_file


SPACE = "yisol/IDM-VTON"


def file_data(path: str):
    return handle_file(str(Path(path).expanduser().resolve()))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Call yisol/IDM-VTON with the same payload shape used by its Gradio UI."
    )
    parser.add_argument("--human", required=True, help="Person image path.")
    parser.add_argument("--garment", required=True, help="Garment image path.")
    parser.add_argument("--description", required=True, help="Garment description.")
    parser.add_argument("--steps", type=int, default=30, help="Denoising steps, UI default 30.")
    parser.add_argument("--seed", type=int, default=42, help="Seed, UI default 42.")
    parser.add_argument(
        "--auto-crop",
        action="store_true",
        help="Match the UI's optional auto-crop checkbox. Default is off.",
    )
    parser.add_argument(
        "--manual-mask",
        help="Optional mask layer image. If set, disables auto-generated mask.",
    )
    args = parser.parse_args()

    auto_mask = args.manual_mask is None
    human_editor_value = {
        "background": file_data(args.human),
        "layers": [] if auto_mask else [file_data(args.manual_mask)],
        "composite": None,
    }

    client = Client(SPACE)
    output_image, masked_preview = client.predict(
        human_editor_value,
        file_data(args.garment),
        args.description,
        auto_mask,
        args.auto_crop,
        args.steps,
        args.seed,
        api_name="/tryon",
    )

    print("output_image:", output_image)
    print("masked_preview:", masked_preview)


if __name__ == "__main__":
    main()
