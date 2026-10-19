/* ========================================================================
     About This File
   ======================================================================== */

/* The overlap check check_overlaps.py runs in headless Chrome. Once the
   app loads in the iframe, it shows every combination of the Class, Lab,
   Outcome, and Kind filters, measures the Threat Matrix in each view, and
   writes the results as JSON into #out for the script to read.

   Text is measured by its ink rather than its line box. getBBox gives the
   horizontal extent, already honoring text-anchor and letter spacing, and
   a canvas in the same font gives the glyphs' ascent and descent.

   A leader line ties a crowded label to its dot, so it may not cross any
   other case's dot or label. Each axis title is compared with its own
   icon and arrow inside the group that carries its rotation. The tabs are
   clicked after every filter change, since revealing the matrix is what
   places the axis icons. */



/* ========================================================================
     Boxes
   ======================================================================== */

function inkBox(doc, el){
    const b   = el.getBBox();
    const cs  = doc.defaultView.getComputedStyle(el);
    const ctx = doc.createElement("canvas").getContext("2d");

    ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;

    const m    = ctx.measureText(el.textContent);
    const base = parseFloat(el.getAttribute("y"));

    return {
        x1: b.x,
        x2: b.x + b.width,
        y1: base - m.actualBoundingBoxAscent,
        y2: base + m.actualBoundingBoxDescent,
    };
}

function dotBox(el){
    const cx = +el.getAttribute("cx");
    const cy = +el.getAttribute("cy");
    const r  = +el.getAttribute("r") + (+el.getAttribute("stroke-width") || 0) / 2;

    return {x1: cx - r, x2: cx + r, y1: cy - r, y2: cy + r};
}

function overlap(a, b){
    const w = Math.min(a.x2, b.x2) - Math.max(a.x1, b.x1);
    const h = Math.min(a.y2, b.y2) - Math.max(a.y1, b.y1);

    return (w > 0 && h > 0) ? [+w.toFixed(1), +h.toFixed(1)] : null;
}



/* ========================================================================
     Measuring
   ======================================================================== */

function chartItems(doc, svg){
    const items = [];

    svg.querySelectorAll(".pt").forEach(g=>{
        items.push({name: `dot ${g.dataset.id}`, box: dotBox(g.querySelector("circle"))});
        items.push({name: `label ${g.dataset.id}`, box: inkBox(doc, g.querySelector("text")), label: true});
    });

    svg.querySelectorAll(".svg-note").forEach(t=>{
        items.push({name: `quadrant "${t.textContent}"`, box: inkBox(doc, t)});
    });

    return items;
}

function leaderHits(doc, svg){
    const hits = [];
    const pts  = [...svg.querySelectorAll(".pt")];
    const dots = pts.map(g=>({id: g.dataset.id, c: g.querySelector("circle")}));

    pts.forEach(g=>{
        const line = g.querySelector("line.leader");
        if(!line) return;

        const a  = {x: +line.getAttribute("x1"), y: +line.getAttribute("y1")};
        const b  = {x: +line.getAttribute("x2"), y: +line.getAttribute("y2")};
        const dx = b.x - a.x;
        const dy = b.y - a.y;

        dots.forEach(o=>{
            if(o.id === g.dataset.id) return;

            const px = +o.c.getAttribute("cx");
            const py = +o.c.getAttribute("cy");
            const r  = +o.c.getAttribute("r") + 1;
            const t  = Math.max(0, Math.min(1, ((px - a.x) * dx + (py - a.y) * dy) / (dx * dx + dy * dy || 1)));

            if(Math.hypot(a.x + t * dx - px, a.y + t * dy - py) < r){
                hits.push(`leader ${g.dataset.id} crosses dot ${o.id}`);
            }
        });

        pts.forEach(o=>{
            if(o === g) return;

            const box = inkBox(doc, o.querySelector("text"));

            for(let s = 0; s <= 1; s += 0.02){
                const x = a.x + s * dx;
                const y = a.y + s * dy;

                if(x > box.x1 && x < box.x2 && y > box.y1 && y < box.y2){
                    hits.push(`leader ${g.dataset.id} crosses label ${o.dataset.id}`);
                    break;
                }
            }
        });
    });

    return hits;
}

function overlapHits(items){
    const hits = [];

    for(let i = 0; i < items.length; i++){
        for(let j = i + 1; j < items.length; j++){
            const o = overlap(items[i].box, items[j].box);

            if(o){
                hits.push(`${items[i].name} overlaps ${items[j].name} by ${o[0]} x ${o[1]}`);
            }
        }
    }

    return hits;
}

function frameHits(svg, items){
    const hits  = [];
    const f     = svg.querySelector("rect");
    const fx    = +f.getAttribute("x");
    const fy    = +f.getAttribute("y");
    const frame = {x1: fx, y1: fy, x2: fx + +f.getAttribute("width"), y2: fy + +f.getAttribute("height")};

    items.filter(it=>it.label).forEach(it=>{
        const b = it.box;

        if(b.x1 < frame.x1 || b.x2 > frame.x2 || b.y1 < frame.y1 || b.y2 > frame.y2){
            hits.push(`${it.name} runs outside the plot frame`);
        }
    });

    return hits;
}

function axisHits(doc, svg){
    const hits = [];

    svg.querySelectorAll(".axis-note").forEach(g=>{
        const title = g.querySelector(".axis-text");
        const ring  = g.querySelector("circle.axis-icon");
        const arrow = g.querySelector(".axis-arrow");
        const name  = `axis "${title.textContent}"`;

        if(!ring){
            hits.push(`${name} has no info icon`);
            return;
        }

        const parts = [["title", inkBox(doc, title)], ["icon", dotBox(ring)], ["arrow", inkBox(doc, arrow)]];

        for(let i = 0; i < parts.length; i++){
            for(let j = i + 1; j < parts.length; j++){
                const o = overlap(parts[i][1], parts[j][1]);

                if(o){
                    hits.push(`${name}: ${parts[i][0]} overlaps ${parts[j][0]} by ${o[0]} x ${o[1]}`);
                }
            }
        }
    });

    return hits;
}

function measure(doc){
    const svg = doc.querySelector(".scatter-svg");
    if(!svg) return {items: 0, hits: []};

    const items = chartItems(doc, svg);
    const hits  = [
        ...leaderHits(doc, svg),
        ...overlapHits(items),
        ...frameHits(svg, items),
        ...axisHits(doc, svg),
    ];

    return {items: items.length, hits};
}



/* ========================================================================
     Filter Views
   ======================================================================== */

async function checkViews(frame){
    const win = frame.contentWindow;
    const doc = frame.contentDocument;

    if(doc.fonts) await doc.fonts.ready;

    const cls      = doc.getElementById("classFilter");
    const labBoxes = [...doc.querySelectorAll("#labList input")];
    const out      = doc.getElementById("outcomeFilter");
    const kind     = doc.getElementById("kindFilter");
    const outs     = out ? [...out.options].map(o=>o.value) : [""];
    const kinds    = kind ? [...kind.options].map(o=>o.value) : [""];
    const results  = [];

    const showView = (c, l, o, k)=>{
        cls.value = c;
        if(out) out.value = o || "";
        if(kind) kind.value = k || "";
        labBoxes.forEach(b=>{ b.checked = (b.value === l); });
        cls.dispatchEvent(new win.Event("change"));
        doc.getElementById("tab-timeline").click();
        doc.getElementById("tab-matrix").click();
    };

    for(const c of [...cls.options].map(o=>o.value)){
        for(const l of ["", ...labBoxes.map(b=>b.value)]){
            for(const o of outs){
                for(const k of kinds){
                    showView(c, l, o, k);
                    results.push({
                        classFilter:   c || "all",
                        labFilter:     l || "all",
                        outcomeFilter: o || "all",
                        kindFilter:    k || "all",
                        ...measure(doc),
                    });
                }
            }
        }
    }

    showView("", "", "", "");

    if(location.search.includes("shot")){
        doc.getElementById("scatter").scrollIntoView({block: "center"});
    }

    document.getElementById("out").textContent = JSON.stringify(results);
}



/* ========================================================================
     Startup
   ======================================================================== */

function init(){
    const frame = document.getElementById("app");

    frame.addEventListener("load", ()=>checkViews(frame));
}

init();