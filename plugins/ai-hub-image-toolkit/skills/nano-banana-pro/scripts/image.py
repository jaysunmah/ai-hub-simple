#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-aiplatform-helper",
#     "google-genai",
#     "pillow",
# ]
#
# [[tool.uv.index]]
# url = "https://artifactory.paypalcorp.com/artifactory/api/pypi/paypal-python-all/simple"
# ///
"""
Generate images using Gemini 3 Pro Image (Nano Banana Pro).

Usage:
    uv run generate_image.py --prompt "A colorful abstract pattern" --output "./hero.png"
    uv run generate_image.py --prompt "Minimalist icon" --output "./icon.png" --aspect landscape
    uv run generate_image.py --prompt "Similar style image" --output "./new.png" --reference "./existing.png"
"""

import argparse
import json
import os
import sys
import tempfile

import paypal.aiplatform.helper as helper
from paypal.aiplatform.helper.genai import genai_defaults
from PIL import Image


def get_aspect_instruction(aspect: str) -> str:
    """Return aspect ratio instruction for the prompt."""
    aspects = {
        "square": "Generate a square image (1:1 aspect ratio).",
        "landscape": "Generate a landscape/wide image (16:9 aspect ratio).",
        "portrait": "Generate a portrait/tall image (9:16 aspect ratio).",
    }
    return aspects.get(aspect, aspects["square"])


def generate_image(
    prompt: str, output_path: str, aspect: str = "square", reference: str | None = None
) -> None:
    """Generate an image using Gemini 3 Pro Image and save to output_path."""
    gcp_project = os.environ.get("GCP_PROJECT_NAME")
    if not gcp_project:
        print("Error: GCP_PROJECT_NAME environment variable not set", file=sys.stderr)
        print("Set it to your team's GCP project (e.g., us-ce1-test-apps-smbfs-engops)", file=sys.stderr)
        sys.exit(1)

    config = {
        "version": 2,
        "auth_method": "user",
        "environment": "dev",
        "gcp_project_name": gcp_project,
        "gcp_project_location": "global",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        config_path = f.name

    try:
        helper.init(config_path)
        client = genai_defaults.get_client()
    finally:
        os.unlink(config_path)

    aspect_instruction = get_aspect_instruction(aspect)
    full_prompt = f"{aspect_instruction} {prompt}"

    # Build contents with optional reference image
    contents: list = []
    if reference:
        if not os.path.exists(reference):
            print(f"Error: Reference image not found: {reference}", file=sys.stderr)
            sys.exit(1)
        ref_image = Image.open(reference)
        contents.append(ref_image)
        full_prompt = f"{full_prompt} Use the provided image as a reference for style, composition, or content."
    contents.append(full_prompt)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
    )

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Extract image from response
    for part in response.parts:
        if part.text is not None:
            print(f"Model response: {part.text}")
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            print(f"Image saved to: {output_path}")
            return

    print("Error: No image data in response", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Gemini 3 Pro Image (Nano Banana Pro)"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Description of the image to generate",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path (PNG format)",
    )
    parser.add_argument(
        "--aspect",
        choices=["square", "landscape", "portrait"],
        default="square",
        help="Aspect ratio (default: square)",
    )
    parser.add_argument(
        "--reference",
        help="Path to a reference image for style/composition guidance (optional)",
    )

    args = parser.parse_args()
    generate_image(args.prompt, args.output, args.aspect, args.reference)


if __name__ == "__main__":
    main()
