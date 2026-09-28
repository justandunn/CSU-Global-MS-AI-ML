from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

folder = Path(__file__).resolve().parent / "docx_render"
pages = sorted(folder.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[1]))
for group_index in range(3):
    group = pages[group_index * 4 : (group_index + 1) * 4]
    sheet = Image.new("RGB", (3000, 1010), "white")
    draw = ImageDraw.Draw(sheet)
    for page_index, page_path in enumerate(group):
        image = ImageOps.contain(Image.open(page_path).convert("RGB"), (750, 970))
        sheet.paste(image, (page_index * 750, 35))
        draw.text((page_index * 750 + 8, 8), page_path.name, fill="black")
    sheet.save(folder / f"contact-{group_index + 1}.png")
