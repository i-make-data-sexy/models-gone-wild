/* ========================================================================
     About This File
   ======================================================================== */

/* The tooltip for glossary terms and info notes, one bubble that
   positionTip() places beside its trigger, held 10px inside the open
   poster or the reading column, and the window, on all four sides, and
   flipped below when it would run off the top. It hides on scroll,
   resize, and Escape, and the Threat Matrix redraws when its width
   changes. */



/* ========================================================================
     Tooltip
   ======================================================================== */

const tip     = document.getElementById("tip");
const TIP_GAP = 10;
let tipFor    = null;

function tipBounds(el){
    const box = (el.closest(".poster") || document.querySelector(".content")).getBoundingClientRect();
    return {
        left:   Math.max(TIP_GAP, box.left + TIP_GAP),
        right:  Math.min(window.innerWidth - TIP_GAP, box.right - TIP_GAP),
        top:    Math.max(TIP_GAP, box.top + TIP_GAP),
        bottom: Math.min(window.innerHeight - TIP_GAP, box.bottom - TIP_GAP)
    };
}

function positionTip(el){
    const text = el.dataset.def || el.dataset.tip;
    if(!text) return;
    tipFor = el;

    tip.innerHTML = text;
    tip.className = "tip " + (el.dataset.def ? "tip-def" : "tip-label")
        + (text.indexOf("tip-lede") > -1 ? " tip-scores" : "");

    tip.style.left = "0px";
    tip.style.top = "0px";
    tip.classList.add("show");

    const t    = (el.querySelector("circle.axis-icon") || el).getBoundingClientRect();
    const b    = tip.getBoundingClientRect();
    const edge = tipBounds(el);

    let x = t.left + t.width/2 - b.width/2;
    if(x + b.width > edge.right) x = edge.right - b.width;
    if(x < edge.left) x = edge.left;

    const roomAbove = t.top - TIP_GAP - edge.top;
    const roomBelow = edge.bottom - t.bottom - TIP_GAP;
    let y, placement;
    if(b.height <= roomAbove){
        y = t.top - b.height - TIP_GAP; placement = "above";
    } else if(b.height <= roomBelow){
        y = t.bottom + TIP_GAP; placement = "below";
    } else if(roomAbove >= roomBelow){
        y = t.top - b.height - TIP_GAP; placement = "above";
    } else {
        y = t.bottom + TIP_GAP; placement = "below";
    }
    y = Math.max(edge.top, Math.min(y, edge.bottom - b.height));

    tip.style.left = Math.round(x) + "px";
    tip.style.top  = Math.round(y) + "px";
    tip.classList.add(placement);

    const arrow = Math.min(Math.max(t.left + t.width/2 - x, 12), b.width - 12);
    tip.style.setProperty("--arrow", Math.round(arrow) + "px");
}

function hideTip(){
    tip.classList.remove("show","above","below");
    tipFor = null;
}

function bindTipEvents(){
    ["mouseenter","focus"].forEach(ev=>{
        document.addEventListener(ev, e=>{
            const el = e.target.closest && e.target.closest("[data-def],[data-tip]");
            if(el) positionTip(el);
        }, true);
    });
    ["mouseleave","blur"].forEach(ev=>{
        document.addEventListener(ev, e=>{
            const el = e.target.closest && e.target.closest("[data-def],[data-tip]");
            if(el && el === tipFor) hideTip();
        }, true);
    });

    window.addEventListener("scroll", hideTip, true);
    window.addEventListener("resize", hideTip);
    document.addEventListener("keydown", e=>{ if(e.key==="Escape") hideTip(); });
}



/* ========================================================================
     Threat Matrix Width
   ======================================================================== */

function watchScatterWidth(){
    let scatterResize = null, scatterWidth = 0;
    window.addEventListener("resize", ()=>{
        clearTimeout(scatterResize);
        scatterResize = setTimeout(()=>{
            const w = Math.floor(scatterHost.clientWidth);
            if(currentView==="matrix" && w !== scatterWidth){ scatterWidth = w; renderScatter(filtered()); }
        }, 150);
    });
}



/* ========================================================================
     Init
   ======================================================================== */

bindTipEvents();
watchScatterWidth();