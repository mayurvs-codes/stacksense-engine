"""Takes real screenshots of the running web UI (headless Chrome against `python -m stacksense serve`) for the report.
Each screenshot runs the scenario through the UI and the engine; images are auto-cropped to the content.
Views: r = result only, w = warnings/notes only (components hidden), f = full page with form."""
import base64
import importlib
import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "gate"))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 8791
OUT = ROOT / "report" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def load_round(n, mod):
    m = importlib.import_module(mod)
    fn = getattr(m, f"build{n}", None) or getattr(m, "build")
    return {s["scenario_id"]: {k: v for k, v in s.items() if k != "_class"} for s in fn()}


def shot(name, scn, view="r", width=1100, height=4200, crop=None):
    q = base64.urlsafe_b64encode(json.dumps(scn).encode()).decode()
    url = f"http://127.0.0.1:{PORT}/?s={q}&t=light&v={view}"
    path = OUT / f"{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2", f"--window-size={width},{height}", "--virtual-time-budget=8000",
                    f"--screenshot={path}", url], capture_output=True, timeout=120)
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((2, im.size[1] - 3)))
    bbox = ImageChops.difference(im, bg).getbbox()
    if bbox:
        im = im.crop((0, 0, im.size[0], min(im.size[1], bbox[3] + 48)))
    if crop:
        im = im.crop((0, 0, im.size[0], min(im.size[1], crop * 2)))
    im.save(path)
    return path


if __name__ == "__main__":
    pub = {s["scenario_id"]: s for s in json.load(open(ROOT / "data/scenarios/public_scenarios.json", encoding="utf-8"))}
    srv = subprocess.Popen([sys.executable, "-m", "stacksense", "serve", "--port", str(PORT)], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    try:
        for sid, s in pub.items():
            shot(f"{sid}_full", s)
            shot(f"{sid}_top", s, crop=1330)
        shot("form_P2", pub["P2"], view="f", width=1400, height=1500)
        r1 = load_round(1, "review_round")
        edge = {"edge_missing_fields": "R1-03", "edge_invalid_values": "R1-02", "edge_contradiction": "R1-05", "edge_overengineering": "R1-07",
                "edge_regulatory": "R1-11", "edge_restricted": "R1-16", "edge_skill_mismatch": "R1-20", "edge_deprecated": "R1-14", "edge_existing": "R1-15"}
        for name, sid in edge.items():
            shot(name, r1[sid], view="w", height=2400)
        print("done", len(list(OUT.glob("*.png"))), "images")
    finally:
        srv.terminate()
