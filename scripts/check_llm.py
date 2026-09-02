"""Check the Colab LLM endpoint. Run from repo root: python scripts/check_llm.py"""
import base64, io, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from openai import OpenAI
from autofab.agents import _call_qwen, _extract_json, PLANNER_SYSTEM, get_token_usage

BASE, KEY = os.getenv("QWEN_BASE_URL"), os.getenv("QWEN_API_KEY")
MODEL, VMODEL = os.getenv("QWEN_MODEL"), os.getenv("QWEN_VISION_MODEL")
print("base_url     :", BASE)
print("api_key      :", (KEY[:8] + "...") if KEY else None)
print("model        :", MODEL)
print("vision_model :", VMODEL)
for k, v in {"QWEN_BASE_URL": BASE, "QWEN_API_KEY": KEY,
             "QWEN_MODEL": MODEL, "QWEN_VISION_MODEL": VMODEL}.items():
    if not v:
        sys.exit(f"FAIL: {k} missing from .env")

client = OpenAI(api_key=KEY, base_url=BASE, timeout=1200.0, max_retries=2)

print("\n[1] /v1/models ...", end=" ", flush=True)
t = time.time(); print([m.id for m in client.models.list().data], f"({time.time()-t:.1f}s)")

print("[2] text ...", end=" ", flush=True)
t = time.time(); print(repr(_call_qwen("Reply with exactly: OK", "ping", max_tokens=10)),
                       f"({time.time()-t:.1f}s)")

print("[3] planner JSON ...", end=" ", flush=True)
t = time.time()
plan = _extract_json(_call_qwen(PLANNER_SYSTEM, "A 20mm cube with a 5mm hole through the centre."))
print(sorted(plan), f"({time.time()-t:.1f}s)")

print("[4] vision ...", end=" ", flush=True)
from PIL import Image, ImageDraw
img = Image.new("RGB", (512, 256), "white"); d = ImageDraw.Draw(img)
for cx in (100, 256, 412):
    d.ellipse([cx-45, 83, cx+45, 173], fill="black")
buf = io.BytesIO(); img.save(buf, format="PNG")
b64 = base64.standard_b64encode(buf.getvalue()).decode()
t = time.time()
r = client.chat.completions.create(model=VMODEL, max_tokens=20, temperature=0.0,
    messages=[{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        {"type": "text", "text": "How many black circles are in this image? Reply with only the digit."}]}])
ans = r.choices[0].message.content.strip()
print(repr(ans), "(expected 3)", f"({time.time()-t:.1f}s)")
if "3" not in ans:
    print("    WARNING: vision path unreliable — the Judge will be too.")

print("\ntokens:", get_token_usage())