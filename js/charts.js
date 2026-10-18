/* ========================================================================
     About This File
   ======================================================================== */

/* The Threat Matrix scatter and the Cases by Lab chart, both drawn as
   inline SVG. The scatter places each case by complexity and harm,
   spreads dots that share a spot, and places each label clear of every
   dot and every other label. */



/* ========================================================================
     Charts
   ======================================================================== */

/* ================================================
     Render Scatter
   ================================================ */

const scatterHost = document.getElementById('scatter');


/* ===============================
     Dot and Label Layout
   =============================== */

const measureCtx = document.createElement('canvas').getContext('2d');
function textWidth(text, font){
    measureCtx.font = font;
    return measureCtx.measureText(text).width;
}

const DOT_R      = 11;
const DOT_CLEAR  = 15;
const LABEL_FONT = "400 13px 'Oswald', sans-serif";
const NOTE_FONT  = "12px 'Special Elite', monospace";

const INK_UP = 10, INK_DOWN = 3, PAD = 3;

const LABEL_GAP = 12;

const LABEL_GAP_Y = 2;

const OWN_PENALTY = 400;

const LEADER_RINGS = [48, 64, 80, 96, 112, 130, 150, 175, 200, 230, 260];
const LEADER_CROSS = 5000;

function segToPoint(a, b, p){
    const dx = b.x-a.x, dy = b.y-a.y;
    const t  = Math.max(0, Math.min(1, ((p.x-a.x)*dx + (p.y-a.y)*dy) / (dx*dx + dy*dy || 1)));
    return Math.hypot(a.x + t*dx - p.x, a.y + t*dy - p.y);
}

function segsCross(a, b, c, d){
    const side = (p, q, r) => Math.sign((q.x-p.x)*(r.y-p.y) - (q.y-p.y)*(r.x-p.x));
    return side(a,b,c) !== side(a,b,d) && side(c,d,a) !== side(c,d,b);
}

function segHitsBox(a, b, box){
    for(let t=0; t<=1; t+=0.05){
        const x = a.x + t*(b.x-a.x), y = a.y + t*(b.y-a.y);
        if(x > box.x1 && x < box.x2 && y > box.y1 && y < box.y2) return true;
    }
    return false;
}


/* ===============================
     Axis Spacing Tokens
   =============================== */

const AXIS = {
    GAP:  38,
    CAP:  INK_UP,
    TICK: 18,
    EDGE: 16
};

const axisMargin = ticks => (ticks ? AXIS.TICK : 0) + AXIS.GAP + AXIS.CAP + AXIS.EDGE;

const axisTitleAt = (plotEdge, ticks) => plotEdge + (ticks ? AXIS.TICK : 0) + AXIS.GAP + AXIS.CAP;

const LABEL_SPOTS = [
    {anchor:'start',  dx: 14, dy:  4},
    {anchor:'end',    dx:-14, dy:  4},
    {anchor:'start',  dx:  8, dy:-15},
    {anchor:'start',  dx:  8, dy: 26},
    {anchor:'end',    dx: -8, dy:-15},
    {anchor:'end',    dx: -8, dy: 26},
    {anchor:'middle', dx:  0, dy:-18},
    {anchor:'middle', dx:  0, dy: 30},
    {anchor:'start',  dx: 14, dy: 34},
    {anchor:'end',    dx:-14, dy: 34},
    {anchor:'start',  dx: 14, dy:-26},
    {anchor:'end',    dx:-14, dy:-26}
];

function boxesHit(a, b){
    return a.x1 < b.x2 && b.x1 < a.x2 && a.y1 < b.y2 && b.y1 < a.y2;
}

function overlapArea(a, b){
    const w = Math.min(a.x2,b.x2) - Math.max(a.x1,b.x1);
    const h = Math.min(a.y2,b.y2) - Math.max(a.y1,b.y1);
    return (w>0 && h>0) ? w*h : 0;
}

function labelBox(x, y, w, spot){
    const tx   = x + spot.dx, base = y + spot.dy;
    const left = spot.anchor==='start' ? tx : spot.anchor==='end' ? tx-w : tx-w/2;
    return {x1:left-PAD, x2:left+w+PAD, y1:base-INK_UP-PAD, y2:base+INK_DOWN+PAD, tx, base};
}

function jitterDots(list, X, Y, obstacles){
    const placed = [];
    const SEP    = DOT_R*2 + 4;

    const boxGap = (x,y,b) => Math.hypot(Math.max(b.x1-x, 0, x-b.x2), Math.max(b.y1-y, 0, y-b.y2));
    return list.map(c=>{
        const x0   = X(c.complexity), y0 = Y(c.harm);
        const free = (x,y) => placed.every(p => Math.hypot(p.x-x, p.y-y) >= SEP)
            && (obstacles || []).every(b => boxGap(x,y,b) >= DOT_R + 1);
        let pos    = {x:x0, y:y0};
        if(!free(x0,y0)){
            found:
            for(const r of [SEP*0.6, SEP, SEP*1.4]){
                for(let k=0;k<8;k++){
                    const a = -Math.PI/2 + k*Math.PI/4;
                    const x = x0 + r*Math.cos(a), y = y0 + r*Math.sin(a);
                    if(free(x,y)){ pos = {x,y}; break found; }
                }
            }
        }
        placed.push(pos);
        return {c, x:pos.x, y:pos.y};
    });
}

function placeLabels(dots, bounds, fixed){
    const dotBoxes = dots.map(d=>({x1:d.x-DOT_CLEAR, x2:d.x+DOT_CLEAR, y1:d.y-DOT_CLEAR, y2:d.y+DOT_CLEAR}));
    const order    = dots.map((d,i)=>i).sort((i,j)=> dots[i].x - dots[j].x || dots[i].y - dots[j].y);
    const labels   = dots.map(d=>d.c.scatterLabel || d.c.alias);
    const widths   = labels.map(l=>textWidth(l, LABEL_FONT));
    const placed   = new Array(dots.length).fill(null);

    let waiting = new Set();
    const live  = (k, i) => k !== i && placed[k] && !waiting.has(k);

    const reach = (b, d) => Math.hypot(Math.max(b.x1-d.x, 0, d.x-b.x2), Math.max(b.y1-d.y, 0, d.y-b.y2));

    function clash(i, cand){
        const {b, leader} = cand;
        if(b.x1 < bounds.x1 || b.x2 > bounds.x2 || b.y1 < bounds.y1 || b.y2 > bounds.y2) return Infinity;
        const d    = dots[i];
        const wide = {x1:b.x1-LABEL_GAP, x2:b.x2+LABEL_GAP, y1:b.y1-LABEL_GAP_Y, y2:b.y2+LABEL_GAP_Y};
        let c      = 0;
        if(!leader){
            const ink = {x1:b.x1+PAD, x2:b.x2-PAD, y1:b.y1+PAD, y2:b.y2-PAD};
            c += overlapArea(ink, {x1:d.x-DOT_R-1, x2:d.x+DOT_R+1, y1:d.y-DOT_R-1, y2:d.y+DOT_R+1});
            const mine = reach(b, d);
            dots.forEach((o,k)=>{ if(k!==i && reach(b, o) < mine - 2) c += OWN_PENALTY; });
        }
        dotBoxes.forEach((o,k)=>{ if(k!==i || leader) c += overlapArea(b, o); });
        fixed.forEach(o=>{ c += overlapArea(wide, o); });
        placed.forEach((p,k)=>{
            if(!live(k, i)) return;
            c += overlapArea(wide, p.b);
            if(p.leader && segHitsBox(p.leader.from, p.leader.to, b)) c += LEADER_CROSS;
            if(leader && segHitsBox(leader.from, leader.to, p.b)) c += LEADER_CROSS;
            if(leader && p.leader && segsCross(leader.from, leader.to, p.leader.from, p.leader.to)) c += LEADER_CROSS;
        });
        if(leader) dots.forEach((o,k)=>{ if(k!==i && segToPoint(leader.from, leader.to, o) < DOT_R+2) c += LEADER_CROSS; });
        return c;
    }

    function besideSpot(i){
        const d  = dots[i];
        let best = null;
        for(const spot of LABEL_SPOTS){
            const b = labelBox(d.x, d.y, widths[i], spot);
            const c = clash(i, {b});
            if(!best || c < best.clash) best = {anchor:spot.anchor, b, leader:null, clash:c, score:c};
            if(c === 0) break;
        }
        return best;
    }

    function leaderSpot(i){
        const d  = dots[i];
        let best = null;
        for(const r of LEADER_RINGS){
            for(let k=0; k<48; k++){
                const a      = k*Math.PI/24;
                const px     = d.x + r*Math.cos(a), py = d.y + r*Math.sin(a);
                const anchor = Math.cos(a) >= 0 ? 'start' : 'end';
                const left   = anchor==='start' ? px : px - widths[i];
                const b      = {x1:left-PAD, x2:left+widths[i]+PAD, y1:py+4-INK_UP-PAD, y2:py+4+INK_DOWN+PAD, tx:px, base:py+4};
                const leader = {from:{x:d.x + (DOT_R+2)*Math.cos(a), y:d.y + (DOT_R+2)*Math.sin(a)},
                                                to:{x:anchor==='start' ? b.x1+PAD-3 : b.x2-PAD+3, y:py}};
                const c      = clash(i, {b, leader});
                const score  = c*10 + r*0.5;
                if(!best || score < best.score) best = {anchor, b, leader, clash:c, score};
            }

            if(best && best.clash === 0) break;
        }
        return best;
    }

    const clashNow = i => clash(i, placed[i]);

    order.forEach(i=>{ placed[i] = besideSpot(i); });
    for(let pass=0; pass<12; pass++){
        let moved = false;
        order.forEach(i=>{
            if(clashNow(i) === 0) return;
            const next = besideSpot(i);
            if(next.clash < clashNow(i)){ placed[i] = next; moved = true; }
        });
        if(!moved) break;
    }

    waiting = new Set(order.filter(i=>clashNow(i) > 0));
    [...waiting].forEach(i=>{
        waiting.delete(i);
        const now = clashNow(i), next = leaderSpot(i);
        if(next && next.clash < now) placed[i] = next;
    });
    for(let pass=0; pass<4; pass++){
        let moved = false;
        order.forEach(i=>{
            const now = clashNow(i);
            if(now === 0) return;
            const options = [besideSpot(i), leaderSpot(i)].filter(Boolean).sort((x,y)=>x.clash-y.clash);
            if(options[0].clash < now){ placed[i] = options[0]; moved = true; }
        });
        if(!moved) break;
    }

    return placed.map((p,i)=>{
        const q = p.clash === Infinity ? {anchor:LABEL_SPOTS[0].anchor, b:labelBox(dots[i].x, dots[i].y, widths[i], LABEL_SPOTS[0]), leader:null} : p;
        return {label:labels[i], anchor:q.anchor, x:q.b.tx, y:q.b.base, leader:q.leader};
    });
}

function renderScatter(list){
    const W  = Math.max(700, Math.floor(scatterHost.clientWidth)),H=800, padL=axisMargin(false),padR=2,padT=40,padB=axisMargin(false);
    const pw = W-padL-padR, ph=H-padT-padB;
    const X  = v=>padL+(v/10)*pw;
    const Y  = v=>padT+(1-v/10)*ph;

    const grid=[];
    for(let g=0;g<=10;g+=2.5){
        if(g===5) continue;
        grid.push(`<line x1="${X(g)}" y1="${padT}" x2="${X(g)}" y2="${padT+ph}" stroke="#4a4438" stroke-width="1" opacity="0.18"/>`);
        grid.push(`<line x1="${padL}" y1="${Y(g)}" x2="${padL+pw}" y2="${Y(g)}" stroke="#4a4438" stroke-width="1" opacity="0.18"/>`);
    }
    const mid=`<line x1="${X(5)}" y1="${padT}" x2="${X(5)}" y2="${padT+ph}" stroke="#4a4438" stroke-width="1.5" stroke-dasharray="4 4" opacity="0.5"/>
               <line x1="${padL}" y1="${Y(5)}" x2="${padL+pw}" y2="${Y(5)}" stroke="#4a4438" stroke-width="1.5" stroke-dasharray="4 4" opacity="0.5"/>`;
    const qlabel = (x,y,fill,op,text) =>
        `<text x="${x}" y="${y}" text-anchor="middle" fill="${fill}" font-family="'Special Elite',monospace"
           font-size="12" opacity="${op}" class="svg-note" tabindex="0" role="note"
           data-def="${escAttr(QUADRANT_NOTE[text])}">${text}</text>`;
    const ql=
        qlabel(X(2.5), Y(9.4), "#8f1d16", "0.8", "sleepwalking burglars")
    + qlabel(X(7.5), Y(9.4), "#8f1d16", "0.8", "apex predators")
    + qlabel(X(2.5), Y(0.5), "#5a6b2a", "0.8", "escaped house cats")
    + qlabel(X(7.5), Y(0.5), "#5a6b2a", "0.8", "determined cheaters");
    const axisLabel = (x,y,rot,note,text) =>
        `<g class="axis-note" tabindex="0" role="note" data-def="${escAttr(note)}"${rot?` transform="${rot}"`:''}>
           <text class="axis-text" x="${x}" y="${y}" text-anchor="middle" fill="#3a362c"
             font-family="'Oswald',sans-serif" font-weight="600" font-size="13" letter-spacing="2">${text}</text>
           <text class="axis-arrow" x="${x}" y="${y}" text-anchor="start" fill="#3a362c"
             font-family="'Oswald',sans-serif" font-weight="600" font-size="13">&#8594;</text>
         </g>`;
    const yTitleX = padL - AXIS.GAP;
    const axes =
            axisLabel(padL+pw/2, axisTitleAt(padT+ph, false), '', METRIC_NOTE.complexity, 'ESCAPE COMPLEXITY')
        + axisLabel(yTitleX, padT+ph/2, `rotate(-90 ${yTitleX} ${padT+ph/2})`, METRIC_NOTE.harm, 'HARM POTENTIAL');

    const quadBox   = (x,y,text) => {
        const w = textWidth(text, NOTE_FONT);
        return {x1:x-w/2-PAD, x2:x+w/2+PAD, y1:y-10-PAD, y2:y+3+PAD};
    };
    const quadBoxes = [
        quadBox(X(2.5), Y(9.4), "sleepwalking burglars"),
        quadBox(X(7.5), Y(9.4), "apex predators"),
        quadBox(X(2.5), Y(0.5), "escaped house cats"),
        quadBox(X(7.5), Y(0.5), "determined cheaters")
    ];

    const dots   = jitterDots(list, X, Y, quadBoxes);
    const labels = placeLabels(dots,
        {x1:padL+2, x2:padL+pw-2, y1:padT+2, y2:padT+ph-2}, quadBoxes);

    const pts=dots.map((d,i)=>{
        const c=d.c, cx=d.x, cy=d.y;
        const {label, anchor} = labels[i];
        const scoreCard =
            `<p class="tip-lede">Below are the scores and rationale for the metrics we created using the details of the misdeed.</p>`
            + (c.outcome==='attempt' ? `<p class="tip-row"><b>Outcome:</b> Failed attempt</p>` : '')
            + `<p class="tip-metric">Escape complexity</p>`
            + `<p class="tip-row"><b>Score:</b> ${c.complexity}</p>`
            + `<p class="tip-row"><b>Justification:</b> ${c.whyComplexity}</p>`
            + `<p class="tip-metric">Harm potential</p>`
            + `<p class="tip-row"><b>Score:</b> ${c.harm}</p>`
            + `<p class="tip-row"><b>Justification:</b> ${c.whyHarm}</p>`;

        const tipped = c.disclosedBy && c.disclosedBy.kind==='tip';

        const disc    = `fill="${tipped ? DISC_FILL.tip : DISC_FILL.self}" stroke="#e6ddc6" stroke-width="2"`;
        const discSay = (tipped ? ' Tipped off.' : ' Self-reported.')
            + (c.outcome==='attempt' ? ' Failed attempt.' : '');
        return `<g class="pt" data-id="${c.id}" tabindex="0" role="button"
            data-def="${escAttr(scoreCard)}"
            aria-label="${label}, complexity ${c.complexity} of 10, harm potential ${c.harm} of 10.${discSay} Open the wanted poster.">
            ${labels[i].leader ? `<line class="leader" x1="${labels[i].leader.from.x}" y1="${labels[i].leader.from.y}" x2="${labels[i].leader.to.x}" y2="${labels[i].leader.to.y}" stroke="#4a4438" stroke-width="1" opacity="0.6"/>` : ''}
            <circle cx="${cx}" cy="${cy}" r="${DOT_R}" ${disc}/>
            <text x="${labels[i].x}" y="${labels[i].y}" text-anchor="${anchor}">${label}</text>
        </g>`;
    }).join("");

    scatterHost.innerHTML = list.length
        ? `<svg class="scatter-svg" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
                <rect x="${padL}" y="${padT}" width="${pw}" height="${ph}" fill="none" stroke="#1c1a15" stroke-width="1.5"/>
                ${grid.join("")}${mid}${ql}${axes}${pts}
            </svg>`
        : '<p class="empty-note">No files match the current filters.</p>';

    placeAxisIcons();

    scatterHost.querySelectorAll('.pt').forEach(g=>{
        g.addEventListener('click',()=>openCase(g.dataset.id));
        g.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){e.preventDefault();openCase(g.dataset.id);} });
    });
}

function placeAxisIcons(){
    const ns='http://www.w3.org/2000/svg';

    const R=3.7, GAP=2.5;
    scatterHost.querySelectorAll('.axis-note').forEach(g=>{
        g.querySelectorAll('.axis-icon').forEach(n=>n.remove());
        const label = g.querySelector('.axis-text');
        const arrow = g.querySelector('.axis-arrow');
        if(!label||!arrow) return;

        const centre   = parseFloat(label.getAttribute('x'));
        const baseline = parseFloat(label.getAttribute('y'));
        label.setAttribute('x', centre);
        arrow.setAttribute('x', -9999);
        const lw = label.getBBox().width;
        const aw = arrow.getBBox().width;

        const total = lw + GAP + R*2 + GAP + aw;
        const start = centre - total/2;
        label.setAttribute('x', start + lw/2);
        const iconX = start + lw + GAP + R;
        arrow.setAttribute('x', start + lw + GAP + R*2 + GAP);

        const iconY = baseline - 7;
        const ring  = document.createElementNS(ns,'circle');
        ring.setAttribute('class','axis-icon');
        ring.setAttribute('cx',iconX); ring.setAttribute('cy',iconY); ring.setAttribute('r',R);
        ring.setAttribute('fill','none'); ring.setAttribute('stroke','#3a362c'); ring.setAttribute('stroke-width','0.85');
        const i=document.createElementNS(ns,'text');
        i.setAttribute('class','axis-icon');
        i.setAttribute('x',iconX); i.setAttribute('y',iconY+1.9);
        i.setAttribute('text-anchor','middle'); i.setAttribute('fill','#3a362c');
        i.setAttribute('font-family',"'Oswald',sans-serif");
        i.setAttribute('font-size','5.4'); i.setAttribute('font-weight','600');
        i.textContent='i';
        g.appendChild(ring); g.appendChild(i);
    });
}


/* ================================================
     Render Lab Chart
   ================================================ */

const labHost = document.getElementById('labChart');

function renderLabChart(list){
    if(!list.length){
        labHost.innerHTML = '<p class="empty-note">No files match the current filters.</p>';
        return;
    }

    const byLab = new Map();
    list.slice().sort((a,b)=>a.order-b.order).forEach(c=>{
        if(!byLab.has(c.lab)) byLab.set(c.lab, []);
        byLab.get(c.lab).push(c);
    });
    const rows = [...byLab.entries()].sort((a,b)=>
        b[1].length - a[1].length || a[1][0].order - b[1][0].order);

    const allCounts = {};
    CASES.forEach(c=>{ allCounts[c.lab] = (allCounts[c.lab]||0) + 1; });
    const maxAll = Math.max(...Object.values(allCounts));

    const labelW = Math.max(...rows.map(([lab])=>textWidth(lab, LABEL_FONT)));
    const ROW    = 46, BAR = 26, GAP_SEG = 2;
    const W      = 700, padL = Math.ceil(labelW) + 18, padR = 40, padT = 12, padB = axisMargin(true);
    const pw     = W - padL - padR;
    const H      = padT + rows.length*ROW + padB;
    const unit   = pw / maxAll;
    const X      = n => padL + n*unit;

    const step = maxAll > 24 ? 5 : maxAll > 12 ? 2 : 1;
    let grid   = '';
    for(let n=0; n<=maxAll; n+=step){
        grid += `<line x1="${X(n)}" y1="${padT}" x2="${X(n)}" y2="${padT+rows.length*ROW}" stroke="#4a4438" stroke-width="1" opacity="${n===0?0.6:0.18}"/>`
                    + `<text x="${X(n)}" y="${padT+rows.length*ROW+AXIS.TICK}" text-anchor="middle" fill="#3a362c"
                         font-family="'Oswald',sans-serif" font-size="12">${n}</text>`;
    }
    const axis = `<text x="${padL+pw/2}" y="${axisTitleAt(padT+rows.length*ROW, true)}" text-anchor="middle" fill="#3a362c"
            font-family="'Oswald',sans-serif" font-weight="600" font-size="13" letter-spacing="2">CASES, OLDEST TO NEWEST &#8594;</text>`;

    const bars = rows.map(([lab, cases], r)=>{
        const y      = padT + r*ROW + (ROW-BAR)/2;
        const tipped = cases.filter(c=>c.disclosedBy && c.disclosedBy.kind==='tip').length;
        const segs   = cases.map((c,k)=>{
            const route = c.disclosedBy && c.disclosedBy.kind==='tip' ? 'tip' : 'self';
            const name  = c.scatterLabel || c.alias;
            const card  = `<p class="tip-metric">${name}</p>`
                + `<p class="tip-row"><b>Escaped:</b> ${escDate(c)}</p>`
                + `<p class="tip-row"><b>Disclosure:</b> ${DISCLOSURE_LABEL[route]}</p>`
                + `<p class="tip-row">Select to open the wanted poster.</p>`;

            return `<g class="seg" data-id="${c.id}" tabindex="0" role="button"
                    data-def="${escAttr(card)}"
                    aria-label="${name}, ${lab}, escaped ${escDate(c)}, ${DISCLOSURE_LABEL[route]}. Open the wanted poster.">
                    <rect x="${X(k)+GAP_SEG/2}" y="${y}" width="${Math.max(unit-GAP_SEG, 1)}" height="${BAR}" fill="${DISC_FILL[route]}"/>
                </g>`;
        }).join('');
        return `<text class="lab-name" x="${padL-10}" y="${y+BAR/2+4.5}" text-anchor="end">${lab}</text>
            ${segs}
            <text class="lab-total" x="${X(cases.length)+8}" y="${y+BAR/2+4.5}"
                aria-label="${cases.length} ${cases.length===1?'case':'cases'}, ${tipped} tipped off">${cases.length}</text>`;
    }).join('');

    labHost.innerHTML =
        `<svg class="scatter-svg lab-svg" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
            ${grid}${bars}${axis}
        </svg>`;

    labHost.querySelectorAll('.seg').forEach(g=>{
        g.addEventListener('click',()=>openCase(g.dataset.id));
        g.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){e.preventDefault();openCase(g.dataset.id);} });
    });
}