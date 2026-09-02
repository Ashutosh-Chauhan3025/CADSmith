"""Stage-by-stage smoke test. Run from repo root: python scripts/check_pipeline.py"""
import sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "outputs" / "smoke"; OUT.mkdir(parents=True, exist_ok=True)

print("[1] executor / cadquery ...", end=" ", flush=True)
from autofab.executor import Executor
CODE = 'import cadquery as cq\nresult = cq.Workplane("XY").box(20,20,20).faces(">Z").workplane().hole(5)\n'
r = Executor(output_dir=str(OUT), timeout_seconds=60).execute(CODE, name="smoke")
assert r.success, f"FAIL: {r.error}"
stl = OUT / "smoke.stl"; assert stl.exists(), "FAIL: no STL exported"
print(f"ok ({stl.stat().st_size} bytes)")

print("[2] vtk render ...", end=" ", flush=True)
from autofab.render import render_stl_to_png
png = OUT / "smoke.png"
render_stl_to_png(str(stl), str(png))
assert png.exists() and png.stat().st_size > 5000, "FAIL: render empty/missing"
from PIL import Image
print(f"ok {Image.open(png).size} -> {png}")

print("[3] metrics (self vs self) ...", end=" ", flush=True)
from autofab.metrics import compare_stl
m = compare_stl(str(stl), str(stl), normalize=False).to_dict()
print(f"CD={m['chamfer_distance']:.4f} F1={m['f1_score']:.4f} IoU={m['volumetric_iou']:.4f}  (expect ~0 / ~1 / ~1)")

print("[4] full pipeline ...", flush=True)
from autofab.pipeline import Pipeline
from autofab import agents
agents.reset_token_usage(); t = time.time()
res = Pipeline(output_dir=str(OUT), max_error_retries=2, max_refinement_iterations=1,
               verbose=True, use_vision=True).run(
    "A 40mm x 30mm x 5mm rectangular plate with a 6mm hole at its centre.", name="smoke_part")
print(f"\nconverged={res.converged} iters={len(res.iterations)} "
      f"calls={res.total_llm_calls} wall={time.time()-t:.0f}s")
print("geometry:", res.final_geometry)
print("tokens  :", agents.get_token_usage())