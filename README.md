# Pip Capture

A code-generated capture and marketing-asset pipeline for “Pip and the Magic Mushroom Rings,” the interactive reader from Whispering Woods Books.

- Reader: https://pip-book.vercel.app/pip
- Main site: https://whisperingwoodsbooks.com/
- This repo generates capture/demo and delivery assets around that experience.

## What's here

- `gen_gallery.py` — renders the gallery frame and badge artwork with Pillow and NumPy.
- `make_delivery.py` — renders branded buyer-delivery PDFs with ReportLab.
- `capture.js` — uses Playwright to record the interactive reader.
- `probe.js` — diagnoses the reader's page-flip integration.
- `build.sh` — uses ffmpeg to composite a capture into a finished listing video.

## Stack

Playwright · Pillow · NumPy · ReportLab · ffmpeg · Node.js

## Run

```bash
npm install
npx playwright install chromium
pip install -r requirements.txt

python3 gen_gallery.py
python3 make_delivery.py

# Defaults to http://localhost:3000/pip?capture=1
PIP_CAPTURE_URL='http://localhost:3000/pip?capture=1' node capture.js

# Optional diagnostic; defaults to https://pip-book.vercel.app/pip
PIP_PROBE_URL='https://pip-book.vercel.app/pip' node probe.js

# Uses the first recording and a 14-second duration by default.
./build.sh

# Override the input recording and duration (seconds).
./build.sh recording/example.webm 14
```

`recording/` contains raw Playwright captures and is ignored. `out/` contains generated deliverables and is also ignored. Generated outputs are reproducible from the source scripts and assets in this repo.

## Licensing

Third-party fonts: The bundled Cormorant font files are licensed under the SIL Open Font License 1.1. See `assets/fonts/OFL.txt`.

The project itself remains UNLICENSED unless otherwise stated.
