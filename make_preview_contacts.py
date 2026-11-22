from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

root = Path(r"D:/scam-detector/outputs/01a1f88b-8092-7493-9320-64f6cf99cc36/test-cases/previews")
for sprint in range(1, 6):
    files = sorted(root.glob(f"s{sprint}_*.png"))
    cards = []
    for file in files:
        img = Image.open(file).convert("RGB")
        img.thumbnail((760, 520))
        card = Image.new("RGB", (800, 580), "white")
        x = (800 - img.width) // 2
        y = 42 + (520 - img.height) // 2
        card.paste(img, (x, y))
        draw = ImageDraw.Draw(card)
        draw.text((16, 14), file.stem, fill="black")
        card = ImageOps.expand(card, border=1, fill="#B7C9DC")
        cards.append(card)
    cols = 2
    rows = (len(cards) + cols - 1) // cols
    contact = Image.new("RGB", (cols * 802, rows * 582), "#E5E7EB")
    for i, card in enumerate(cards):
        contact.paste(card, ((i % cols) * 802, (i // cols) * 582))
    contact.save(root / f"contact_s{sprint}.png")
    print(root / f"contact_s{sprint}.png")
