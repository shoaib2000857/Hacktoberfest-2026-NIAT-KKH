"""Create legible fictional document PNGs and text; no generated analysis."""
import json
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from PIL import Image, ImageDraw, ImageFont
from app.advanced_samples import DATASETS, SAMPLES, document

SAMPLES.mkdir(exist_ok=True)
fonts = ["/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
font_path = next((f for f in fonts if Path(f).exists()), None)
font = ImageFont.truetype(font_path, 26) if font_path else ImageFont.load_default(size=26)
heading = ImageFont.truetype(font_path, 38) if font_path else ImageFont.load_default(size=38)
expected = {}
for scenario, documents in DATASETS.items():
    for item in documents:
        text = document(item)
        (SAMPLES / (item["name"] + ".txt")).write_text(text)
        image = Image.new("RGB", (1240, 1500), "#f7f9fa")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 1240, 190), fill="#101f30")
        draw.text((64, 38), "PROMISETRAP / FICTIONAL DEMO", fill="#70dcd0", font=font)
        draw.text((64, 100), item["title"], fill="white", font=heading)
        y = 244
        for paragraph in text.splitlines():
            for line in textwrap.wrap(paragraph, width=70) or [""]:
                draw.text((64, y), line.replace("₹", "INR "), fill="#172d40", font=font)
                y += 44
        image.save(SAMPLES / (item["name"] + ".png"))
    expected[scenario] = {"claims": sum(len(d["claims"]) for d in documents), "expected": {"internship": ["contradiction", "contradiction", "contradiction"], "scholarship": ["contradiction"], "optional": ["insufficient_evidence"], "deadline": ["changed_term"]}[scenario]}
(SAMPLES / "expected.json").write_text(json.dumps(expected, indent=2))
print("Generated fictional PNG and TXT sources for four scenarios.")

