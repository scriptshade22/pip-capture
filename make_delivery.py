from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit, ImageReader
from PIL import Image
import numpy as np

MUSH = Image.open("assets/mushroom.png").convert("RGBA")
LEAF = Image.open("assets/leaf.png").convert("RGBA")

def faded(img, factor):
    a = np.array(img)
    a[:, :, 3] = (a[:, :, 3] * factor).astype("uint8")
    return Image.fromarray(a)

def place_img(c, pil, cx, cy, h, angle=0, opacity=1.0):
    img = pil if opacity >= 0.999 else faded(pil, opacity)
    if angle:
        img = img.rotate(angle, expand=True, resample=Image.BICUBIC)
    w = h * img.size[0] / img.size[1]
    c.drawImage(ImageReader(img), cx - w/2, cy - h/2, w, h, mask="auto")

BASE   = HexColor("#0F1F1A")
MID    = HexColor("#1F3A2F")
ACCENT = HexColor("#7FB069")
CREAM  = HexColor("#F4E8D0")
PLUM   = HexColor("#2D1F3A")
MUTED  = HexColor("#B9C9B0")

pdfmetrics.registerFont(TTFont("Cormorant", "assets/fonts/Cormorant.ttf"))
pdfmetrics.registerFont(TTFont("Cormorant-Italic", "assets/fonts/Cormorant-Italic.ttf"))

W, H = letter
CX = W / 2.0
margin = 46

PLATFORMS = {
    "etsy":    {"label": "Etsy",    "url": "whisperingwoodsbooks.com/founders/etsy"},
    "gumroad": {"label": "Gumroad", "url": "whisperingwoodsbooks.com/founders/gumroad"},
    "kofi":    {"label": "Ko-fi",   "url": "whisperingwoodsbooks.com/founders/kofi"},
}

def mushroom(c, cx, cy, s):
    c.saveState()
    c.setFillColor(ACCENT)
    p = c.beginPath()
    p.moveTo(cx - 1.4*s, cy)
    p.curveTo(cx - 1.4*s, cy + 1.6*s, cx + 1.4*s, cy + 1.6*s, cx + 1.4*s, cy)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.roundRect(cx - 0.45*s, cy - 1.3*s, 0.9*s, 1.45*s, 0.25*s, fill=1, stroke=0)
    c.setFillColor(BASE)
    c.circle(cx - 0.55*s, cy + 0.45*s, 0.22*s, fill=1, stroke=0)
    c.circle(cx + 0.55*s, cy + 0.55*s, 0.18*s, fill=1, stroke=0)
    c.circle(cx + 0.05*s, cy + 0.95*s, 0.15*s, fill=1, stroke=0)
    c.restoreState()

def para(c, text, x, y, font, size, color, leading, max_w, align="center"):
    c.setFont(font, size); c.setFillColor(color)
    for ln in simpleSplit(text, font, size, max_w):
        if align == "center": c.drawCentredString(x, y, ln)
        else: c.drawString(x, y, ln)
        y -= leading
    return y

def build(platform):
    info = PLATFORMS[platform]
    out = f"out/whispering-woods-access-{platform}.pdf"
    c = canvas.Canvas(out, pagesize=letter)

    c.setFillColor(BASE); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(PLUM); c.setLineWidth(2)
    c.rect(margin, margin, W-2*margin, H-2*margin, fill=0, stroke=1)
    c.setStrokeColor(ACCENT); c.setLineWidth(0.6)
    c.rect(margin+7, margin+7, W-2*margin-14, H-2*margin-14, fill=0, stroke=1)

    # ---- corner leaf accents (echo the site decorations) ----
    place_img(c, LEAF,  98, 118, 50, angle=158, opacity=0.50)
    place_img(c, LEAF, 126,  96, 36, angle=112, opacity=0.36)
    place_img(c, LEAF, 516, 690, 50, angle=-22, opacity=0.50)
    place_img(c, LEAF, 540, 660, 36, angle=34, opacity=0.36)

    # ---- header ----
    place_img(c, MUSH, CX, H-100, 74)
    c.setFont("Cormorant-Italic", 33); c.setFillColor(CREAM)
    c.drawCentredString(CX, H-172, "Whispering Woods Books")
    c.setFont("Cormorant-Italic", 13); c.setFillColor(ACCENT)
    c.drawCentredString(CX, H-192, "Magical stories for curious kids")
    c.setStrokeColor(MID); c.setLineWidth(1)
    c.line(CX-120, H-210, CX+120, H-210)

    # ---- headline + intro ----
    c.setFont("Cormorant-Italic", 40); c.setFillColor(CREAM)
    c.drawCentredString(CX, H-256, "Your book is ready.")
    y = para(c,
        "Thank you for becoming one of the first readers of Pip and the Magic "
        "Mushroom Rings. Harper and I made this one together, and you're holding "
        "the very first chapter of what we're building.",
        CX, H-290, "Cormorant-Italic", 16.5, CREAM, 21, W-2*margin-90)

    # ---- CTA ----
    pill_w, pill_h = 340, 48
    pill_x, pill_y = CX-pill_w/2, y-30
    c.setFillColor(ACCENT); c.roundRect(pill_x, pill_y, pill_w, pill_h, pill_h/2, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 14); c.setFillColor(BASE)
    c.drawCentredString(CX, pill_y+pill_h/2-5, "OPEN YOUR BOOK")
    link = "https://" + info["url"]
    c.linkURL(link, (pill_x, pill_y, pill_x+pill_w, pill_y+pill_h), relative=0)
    c.setFont("Helvetica", 11.5); c.setFillColor(CREAM)
    url_y = pill_y - 19
    c.drawCentredString(CX, url_y, info["url"])
    tw = c.stringWidth(info["url"], "Helvetica", 11.5)
    c.linkURL(link, (CX-tw/2, url_y-3, CX+tw/2, url_y+11), relative=0)

    # ---- steps ----
    sy = url_y - 32
    c.setFont("Cormorant-Italic", 19); c.setFillColor(ACCENT)
    c.drawCentredString(CX, sy, "How it works")
    sy -= 24
    steps = [
        "Tap the button above (or type the link into any browser).",
        "Add your first name and email to unlock the book and lock in your Founders perks.",
        "Read it together — phone, tablet, laptop. No app, no download.",
    ]
    for i, s in enumerate(steps, 1):
        c.setFont("Helvetica-Bold", 12); c.setFillColor(ACCENT)
        c.drawString(margin+60, sy, f"{i}.")
        ny = para(c, s, margin+78, sy, "Helvetica", 12, CREAM, 16, W-2*margin-138, align="left")
        sy = ny - 6

    # ---- bottom block (fixed anchors, bottom-up) ----
    # footer
    c.setStrokeColor(MID); c.setLineWidth(1)
    c.line(CX-120, 100, CX+120, 100)
    c.setFont("Helvetica", 10); c.setFillColor(CREAM)
    c.drawCentredString(CX, 82, "Questions? hello@whisperingwoodsbooks.com")
    c.setFont("Cormorant-Italic", 11); c.setFillColor(ACCENT)
    c.drawCentredString(CX, 65, f"Delivered via {info['label']}   \u00b7   Stefon Kye & Harper")
    # disclaimer
    para(c,
        "This PDF is your key, not the book itself. The book is a web-based interactive "
        "experience \u2014 you'll receive a private link to access it on any browser. It is NOT a "
        "downloadable PDF or printable file. The book lives online and works on phones, "
        "tablets, and computers.",
        CX, 156, "Helvetica-Oblique", 9.5, MUTED, 12.5, W-2*margin-110)
    # founders box
    box_h, box_y = 66, 176
    box_x, box_w = margin+30, W-2*margin-60
    c.setFillColor(PLUM); c.roundRect(box_x, box_y, box_w, box_h, 10, fill=1, stroke=0)
    c.setStrokeColor(ACCENT); c.setLineWidth(0.8)
    c.roundRect(box_x, box_y, box_w, box_h, 10, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 11.5); c.setFillColor(ACCENT)
    c.drawCentredString(CX, box_y+box_h-22, "FOUNDERS BONUS")
    para(c,
        "As one of the first 100 buyers, you get all future updates to this book for free \u2014 "
        "and you'll be the first to know when new Whispering Woods books arrive.",
        CX, box_y+box_h-40, "Helvetica", 10.5, CREAM, 14, box_w-40)

    c.showPage(); c.save()
    return out

for p in PLATFORMS:
    print("wrote", build(p))
