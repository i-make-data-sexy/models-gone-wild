# ========================================================================
#   About This File
# ========================================================================

"""Reports anything on the Threat Matrix that is drawn on top of
something else.

The other checks read the case data as text. This one renders the real
page in headless Chrome, so it sees what a reader sees: where each dot
landed, where its label went, and whether the axis icons sit clear of
their titles. It runs every combination of the Class, Lab, Outcome, and
Kind filters, since a label can collide in one filtered view and not in
another.

Text is measured by its ink rather than its line box. The line box of
a 13px label is taller than the glyphs in it, and comparing line boxes
would report stacked labels that never touch.

Writes a screenshot of the unfiltered chart to the path given with
--shot, for a look with your own eyes.

Exit status is 1 if anything overlaps or a dot label leaves the plot,
0 otherwise.
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import argparse
import functools
import html
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading



# ========================================================================
#   Global Variables
# ========================================================================

REPO   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = os.environ.get("CHROME") or next(
    (p for p in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
     + [shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser")]
     if p and os.path.exists(p)),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SUBPATH = "tools/models-gone-wild"



# ========================================================================
#   The Harness
# ========================================================================

HARNESS = r"""<!doctype html>
<html><head><meta charset="utf-8">
<style>html,body{margin:0}iframe{border:0;width:__WIDTH__px;height:1000px}</style>
</head><body>
<iframe id="app" src="/__SUBPATH__/"></iframe>
<pre id="out">PENDING</pre>
<script>
const frame = document.getElementById('app');
const shot = location.search.includes('shot');

// The ink box of a text element in SVG user units. Horizontal extent
// comes from getBBox, which already honours text-anchor and letter
// spacing. Vertical extent comes from the glyphs' own ascent and
// descent, measured in the same font on a canvas.
function inkBox(doc, el){
  const b = el.getBBox();
  const cs = doc.defaultView.getComputedStyle(el);
  const ctx = doc.createElement('canvas').getContext('2d');
  ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
  const m = ctx.measureText(el.textContent);
  const base = parseFloat(el.getAttribute('y'));
  return {x1:b.x, x2:b.x+b.width,
          y1:base-m.actualBoundingBoxAscent, y2:base+m.actualBoundingBoxDescent};
}

// A circle's box, ring included.
function dotBox(el){
  const cx = +el.getAttribute('cx'), cy = +el.getAttribute('cy');
  const r = +el.getAttribute('r') + (+el.getAttribute('stroke-width') || 0)/2;
  return {x1:cx-r, x2:cx+r, y1:cy-r, y2:cy+r};
}

function overlap(a, b){
  const w = Math.min(a.x2,b.x2) - Math.max(a.x1,b.x1);
  const h = Math.min(a.y2,b.y2) - Math.max(a.y1,b.y1);
  return (w>0 && h>0) ? [+w.toFixed(1), +h.toFixed(1)] : null;
}

function measure(doc){
  const svg = doc.querySelector('.scatter-svg');
  if(!svg) return {items:0, hits:[]};
  const hits = [];
  const items = [];
  svg.querySelectorAll('.pt').forEach(g=>{
    const id = g.dataset.id;
    items.push({name:`dot ${id}`, box:dotBox(g.querySelector('circle'))});
    items.push({name:`label ${id}`, box:inkBox(doc, g.querySelector('text')), label:true});
  });
  // A leader line ties a crowded label to its dot. Passing over any
  // other dot would point the reader at the wrong case.
  const dots = [...svg.querySelectorAll('.pt')].map(g=>({id:g.dataset.id, c:g.querySelector('circle')}));
  svg.querySelectorAll('.pt').forEach(g=>{
    const line = g.querySelector('line.leader');
    if(!line) return;
    const a = {x:+line.getAttribute('x1'), y:+line.getAttribute('y1')};
    const b = {x:+line.getAttribute('x2'), y:+line.getAttribute('y2')};
    const dx = b.x-a.x, dy = b.y-a.y;
    dots.forEach(o=>{
      if(o.id === g.dataset.id) return;
      const px = +o.c.getAttribute('cx'), py = +o.c.getAttribute('cy');
      const r = +o.c.getAttribute('r') + 1;
      const t = Math.max(0, Math.min(1, ((px-a.x)*dx + (py-a.y)*dy) / (dx*dx + dy*dy || 1)));
      if(Math.hypot(a.x + t*dx - px, a.y + t*dy - py) < r)
        hits.push(`leader ${g.dataset.id} crosses dot ${o.id}`);
    });
    // Nor may it pass through another case's label
    svg.querySelectorAll('.pt').forEach(o=>{
      if(o === g) return;
      const box = inkBox(doc, o.querySelector('text'));
      for(let s=0; s<=1; s+=0.02){
        const x = a.x + s*dx, y = a.y + s*dy;
        if(x > box.x1 && x < box.x2 && y > box.y1 && y < box.y2){
          hits.push(`leader ${g.dataset.id} crosses label ${o.dataset.id}`);
          break;
        }
      }
    });
  });
  svg.querySelectorAll('.svg-note').forEach(t=>{
    items.push({name:`quadrant "${t.textContent}"`, box:inkBox(doc, t)});
  });
  for(let i=0;i<items.length;i++){
    for(let j=i+1;j<items.length;j++){
      const o = overlap(items[i].box, items[j].box);
      if(o) hits.push(`${items[i].name} overlaps ${items[j].name} by ${o[0]} x ${o[1]}`);
    }
  }
  // Dot labels stay inside the plot frame, the first rect in the SVG.
  const f = svg.querySelector('rect');
  const fx = +f.getAttribute('x'), fy = +f.getAttribute('y');
  const frameBox = {x1:fx, y1:fy, x2:fx + +f.getAttribute('width'), y2:fy + +f.getAttribute('height')};
  items.filter(it=>it.label).forEach(it=>{
    const b = it.box;
    if(b.x1<frameBox.x1 || b.x2>frameBox.x2 || b.y1<frameBox.y1 || b.y2>frameBox.y2)
      hits.push(`${it.name} runs outside the plot frame`);
  });
  // Each axis title against its own info icon and arrow. Compared inside
  // the group, which carries the rotation for the vertical axis.
  svg.querySelectorAll('.axis-note').forEach(g=>{
    const title = g.querySelector('.axis-text');
    const ring = g.querySelector('circle.axis-icon');
    const arrow = g.querySelector('.axis-arrow');
    const name = `axis "${title.textContent}"`;
    if(!ring){ hits.push(`${name} has no info icon`); return; }
    const parts = [['title', inkBox(doc, title)], ['icon', dotBox(ring)], ['arrow', inkBox(doc, arrow)]];
    for(let i=0;i<parts.length;i++) for(let j=i+1;j<parts.length;j++){
      const o = overlap(parts[i][1], parts[j][1]);
      if(o) hits.push(`${name}: ${parts[i][0]} overlaps ${parts[j][0]} by ${o[0]} x ${o[1]}`);
    }
  });
  return {items:items.length, hits};
}

frame.addEventListener('load', async ()=>{
  const win = frame.contentWindow, doc = frame.contentDocument;
  if(doc.fonts) await doc.fonts.ready;
  const cls = doc.getElementById('classFilter');
  // The Lab filter is a checkbox list, so a lab view is one box ticked
  // and the unfiltered view is none
  const labBoxes = [...doc.querySelectorAll('#labList input')];
  const out = doc.getElementById('outcomeFilter');
  const kind = doc.getElementById('kindFilter');
  const set = (c,l,o,k)=>{
    cls.value = c; if(out) out.value = o || ''; if(kind) kind.value = k || '';
    labBoxes.forEach(b=>{ b.checked = (b.value === l); });
    cls.dispatchEvent(new win.Event('change'));
    // Revealing the matrix is what places the axis icons, so click the
    // tab after every filter change, the way a reader's view is built.
    doc.getElementById('tab-timeline').click();
    doc.getElementById('tab-matrix').click();
  };
  const results = [];
  const outs = out ? [...out.options].map(o=>o.value) : [''];
  const kinds = kind ? [...kind.options].map(o=>o.value) : [''];
  for(const c of [...cls.options].map(o=>o.value)){
    for(const l of ['', ...labBoxes.map(b=>b.value)]){
      for(const o of outs){
        for(const k of kinds){
          set(c,l,o,k);
          results.push({classFilter:c||'all', labFilter:l||'all', outcomeFilter:o||'all', kindFilter:k||'all', ...measure(doc)});
        }
      }
    }
  }
  set('','','','');
  if(shot) doc.getElementById('scatter').scrollIntoView({block:'center'});
  document.getElementById('out').textContent = JSON.stringify(results);
});
</script>
</body></html>
"""



# ========================================================================
#   Running Chrome
# ========================================================================

def serve(root: str) -> tuple:
    """
    Serves a directory over HTTP on a free local port, in a background thread

    Args:
        root (str): The directory to serve

    Returns:
        tuple: The server, so it can be shut down, and the port it bound
    """

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            """
            Drops the per-request log line so the report stays readable

            Args:
                *args (object): The format string and values the base class would log

            Returns:
                None
            """

            pass

    handler = functools.partial(Quiet, directory=root)
    server  = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    return server, server.server_address[1]


def chrome(args: list) -> str:
    """
    Runs headless Chrome with the given flags and a generous time budget for the fonts to arrive

    Args:
        args (list): Flags and the URL, appended after the fixed flags

    Returns:
        str: Whatever Chrome printed to stdout
    """

    base = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--window-size=1300,1000", "--virtual-time-budget=20000"]
    run  = subprocess.run(base + args, capture_output=True, text=True, timeout=120)

    return run.stdout


def build_site(width: int) -> str:
    """
    Lays out a throwaway web root with the repo at its production subpath and the harness at the top

    Args:
        width (int): The page width to render at, in pixels

    Returns:
        str: The path of the web root
    """

    root = tempfile.mkdtemp(prefix="mgw-overlap-")
    os.makedirs(os.path.join(root, os.path.dirname(SUBPATH)))
    os.symlink(REPO, os.path.join(root, SUBPATH))

    with open(os.path.join(root, "harness.html"), "w") as f:
        f.write(HARNESS.replace("__SUBPATH__", SUBPATH).replace("__WIDTH__", str(width)))

    return root



# ========================================================================
#   Main
# ========================================================================

def main() -> int:
    """
    Renders the chart under every filter combination and prints each overlap found

    Args:
        None

    Returns:
        int: 1 if anything overlapped or left the plot, 0 if the chart is clean
    """

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--shot", help="Write a PNG of the unfiltered chart to this path")
    ap.add_argument("--width", type=int, default=1300,
                    help="Page width in pixels. The chart fills its column, so check a phone width (390) as well")

    opts = ap.parse_args()

    if not os.path.exists(CHROME):
        print(f"Chrome not found at {CHROME}. Set CHROME to its path.")
        return 1

    root = build_site(opts.width)
    server, port = serve(root)

    try:
        url   = f"http://127.0.0.1:{port}/harness.html"
        dom   = chrome(["--dump-dom", url])
        found = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
        raw   = html.unescape(found.group(1)) if found else "PENDING"

        if raw == "PENDING":
            print("The harness never finished. The page may have thrown, or the fonts never loaded.")
            return 1

        results = json.loads(raw)

        if opts.shot:
            chrome([f"--screenshot={os.path.abspath(opts.shot)}", url + "?shot"])
    finally:
        server.shutdown()
        shutil.rmtree(root, ignore_errors=True)

    bad = 0

    for r in results:
        view = f"class {r['classFilter']}, lab {r['labFilter']}, outcome {r.get('outcomeFilter', 'all')}, kind {r.get('kindFilter', 'all')}"

        if r["hits"]:
            bad += 1
            print(f"  OVERLAP  {view}  ({r['items']} items)")

            for h in r["hits"]:
                print(f"           {h}")
        else:
            print(f"  OK       {view}  ({r['items']} items)")

    print(f"\n{len(results)} filter views checked, {bad} with overlaps")

    if opts.shot:
        print(f"screenshot: {opts.shot}")

    return 1 if bad else 0



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    sys.exit(main())