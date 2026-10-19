/* ========================================================================
     About This File
   ======================================================================== */

/* The filters and the timeline view. It reads the class, lab, outcome,
   and kind filters, keeps the lab picker's summary current, and renders
   the timeline of case cards. filtered() returns the cases the filters
   keep, which every view reads. */



/* ========================================================================
     Timeline
   ======================================================================== */

/* ================================================
     Filter State
   ================================================ */

const classSelect   = document.getElementById("classFilter");
const labPicker     = document.getElementById("labFilter");
const labSummary    = document.getElementById("labSummary");
const labList       = document.getElementById("labList");
const outcomeSelect = document.getElementById("outcomeFilter");
const kindSelect    = document.getElementById("kindFilter");

function selectedLabs(){
    return [...labList.querySelectorAll("input:checked")].map(b=>b.value);
}

function filtered(){
    const labs = selectedLabs();
    return CASES.filter(c =>
        (!classSelect.value   || String(c.cls)===classSelect.value) &&
        (!labs.length         || labs.includes(c.lab)) &&
        (!outcomeSelect.value || c.outcome===outcomeSelect.value) &&
        (!kindSelect.value    || c.reach===kindSelect.value)
    ).sort((a,b)=>a.order-b.order);
}


/* ================================================
     Build Lab Options
   ================================================ */

[...new Set(CASES.map(c=>c.lab))].forEach(l=>{
    const row=document.createElement("label");
    row.className="multi-select-option";
    const box=document.createElement("input");
    box.type="checkbox"; box.value=l;
    row.append(box, document.createTextNode(l));
    labList.appendChild(row);
});

function updateLabSummary(labs){
    labSummary.textContent = !labs.length ? "All labs"
        : labs.length===1 ? labs[0]
        : `${labs.length} labs`;
    labSummary.classList.toggle("is-active", labs.length>0);
}

function discChip(c){
    const d = c.disclosedBy;
    if(!d || !DISCLOSURE_LABEL[d.kind]) return "";
    return `<span class="disc-chip d-${d.kind}" tabindex="0" role="note"
       data-def="${escAttr(DISCLOSURE_NOTE[d.kind])}">${DISCLOSURE_LABEL[d.kind]}</span>`;
}


/* ================================================
     Render Timeline
   ================================================ */

const tl = document.getElementById("timeline");
function renderTimeline(list){
    tl.innerHTML="";
    if(!list.length){ tl.innerHTML='<p class="empty-note">No files match the current filters.</p>'; return; }
    list.forEach((c,i)=>{
        const side = i%2===0 ? "left":"right";
        const el   = document.createElement("div");
        el.className = `event ${side} c${c.cls}`;
        const src = c.source && c.source.url
            ? `<a class="icon-btn" href="${c.source.url}" target="_blank" rel="noopener"
                        data-tip="Story &middot; ${c.source.outlet||"read more"}"
                        aria-label="Read the story that broke this case${c.source.outlet?", "+c.source.outlet:""}, opens in a new tab">${ICON.story}</a>`
            : "";
        el.innerHTML = `
            <div class="node"></div>
            <div class="date-tag">${escDate(c)}</div>
            ${c.disclosed ? `<div class="lag-tag">Disclosed ${c.date===UNDATED ? c.disclosed : c.lag}</div>` : ""}
            ${noticeTag(c)}
            <div class="card" data-id="${c.id}">
                <div class="card-body">
                    <div class="spine c${c.cls}"><span>${c.lab}</span></div>
                    <div class="card-text">
                        <div class="card-actions">
                            ${src}
                            <button class="icon-btn" data-open="${c.id}" aria-haspopup="dialog"
                                            data-tip="Wanted poster" aria-label="Open the wanted poster for ${c.alias}">${ICON.poster}</button>
                        </div>
                        <p class="card-alias">${c.alias}</p>
                        <p class="card-charge">${gloss(c.charge)}</p>
                        <div class="card-tags">
                            <span class="class-badge c${c.cls}" tabindex="0" role="note" data-def="${CLASS_NOTE[c.cls]}">${CLASS_LABEL[c.cls]}</span>
                            ${discChip(c)}
                        </div>
                    </div>
                </div>
            </div>`;
        tl.appendChild(el);
    });

    tl.querySelectorAll(".icon-btn[data-open]").forEach(btn=>{
        btn.addEventListener("click",()=>openCase(btn.dataset.open));
    });
}