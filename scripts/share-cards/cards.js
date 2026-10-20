/* ========================================================================
     About This File
   ======================================================================== */

/* Draws the three share cards in cards.html from the live case data:
   the lineup of one mugshot per lab, the Threat Matrix plotted from each
   case's complexity and harm, and the Cases by Lab bars, one segment per
   case in escape order. It reuses the app's own CASES, mug(), and
   cssToken(), then marks the page ready for scripts/share_cards.py. */



/* ========================================================================
     Lineup
   ======================================================================== */

function drawLineup(){
    const faces = ["sol", "claude", "gemini", "spark", "kimi"];
    const row   = document.querySelector("#lineup .row");

    faces.forEach(id => {
        const frame     = document.createElement("div");
        frame.className = "mug";
        frame.innerHTML = mug(id);
        row.appendChild(frame);
    });
}



/* ========================================================================
     Threat Matrix
   ======================================================================== */

function drawMatrix(){
    const ink  = cssToken("--ink");
    const rule = cssToken("--rule");
    const red  = cssToken("--stamp-red");
    const P    = 20, S = 480;
    const X    = v => P + 34 + (v - 1) / 9 * (S - 68);
    const Y    = v => P + S - 52 - (v - 1) / 9 * (S - 104);
    const seen = {};

    const corner = (x, y, text, anchor) =>
        `<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${red}" font-family="Courier Prime" font-size="17" text-decoration="underline">${text}</text>`;

    let svg = `<rect x="${P}" y="${P}" width="${S}" height="${S}" fill="none" stroke="${ink}" stroke-width="2.5"/>`
        + `<line x1="${P + S / 2}" y1="${P}" x2="${P + S / 2}" y2="${P + S}" stroke="${rule}" stroke-dasharray="5 5" stroke-width="1.5"/>`
        + `<line x1="${P}" y1="${P + S / 2}" x2="${P + S}" y2="${P + S / 2}" stroke="${rule}" stroke-dasharray="5 5" stroke-width="1.5"/>`
        + corner(P + 14, P + 30, "sleepwalking burglars", "start")
        + corner(P + S - 14, P + 30, "apex predators", "end")
        + corner(P + 14, P + S - 16, "escaped house cats", "start")
        + corner(P + S - 14, P + S - 16, "determined cheaters", "end");

    CASES.forEach(c => {
        const spot  = c.complexity + "," + c.harm;
        const shift = (seen[spot] = (seen[spot] || 0) + 1) - 1;
        const fill  = cssToken(c.disclosedBy.kind === "self" ? "--disc-self" : "--disc-tip");
        svg += `<circle cx="${X(c.complexity) + shift * 15}" cy="${Y(c.harm)}" r="10" fill="${fill}" stroke="${cssToken("--paper")}" stroke-width="2"/>`;
    });

    document.querySelector("#threat-matrix svg").innerHTML = svg;
}



/* ========================================================================
     Cases by Lab
   ======================================================================== */

function drawLabs(){
    const ink   = cssToken("--ink");
    const rule  = cssToken("--rule");
    const byLab = new Map();

    CASES.slice().sort((a, b) => a.order - b.order).forEach(c => {
        if(!byLab.has(c.lab)) byLab.set(c.lab, []);
        byLab.get(c.lab).push(c);
    });

    const rows = [...byLab.entries()].sort((a, b) => b[1].length - a[1].length || a[1][0].order - b[1][0].order);
    const most = Math.max(...rows.map(([, cases]) => cases.length));
    const padL = 160, W = 610, ROW = 86, BAR = 46;
    const top  = (470 - rows.length * ROW) / 2;
    const unit = (W - padL - 46) / most;
    const X    = n => padL + n * unit;

    let svg = `<line x1="${padL}" y1="${top}" x2="${padL}" y2="${top + rows.length * ROW}" stroke="${rule}" stroke-width="1.5" opacity=".6"/>`;

    rows.forEach(([lab, cases], r) => {
        const y     = top + r * ROW + (ROW - BAR) / 2;
        const label = (x, anchor, text) =>
            `<text x="${x}" y="${y + BAR / 2 + 8}" text-anchor="${anchor}" fill="${ink}" font-family="Oswald" font-weight="600" font-size="23">${text}</text>`;

        svg += label(padL - 16, "end", lab);

        cases.forEach((c, k) => {
            const fill = cssToken(c.disclosedBy.kind === "tip" ? "--disc-tip" : "--disc-self");
            svg += `<rect x="${X(k) + 1.5}" y="${y}" width="${unit - 3}" height="${BAR}" fill="${fill}"/>`;
        });

        svg += label(X(cases.length) + 12, "start", cases.length);
    });

    document.querySelector("#lab-counts svg").innerHTML = svg;
}



/* ========================================================================
     Init
   ======================================================================== */

function initCards(){
    drawLineup();
    drawMatrix();
    drawLabs();
    document.fonts.ready.then(() => { document.body.dataset.ready = "true"; });
}

document.addEventListener("DOMContentLoaded", initCards);