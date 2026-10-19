/* ========================================================================
     About This File
   ======================================================================== */

/* The case poster, the WANTED file that opens over the page. It builds a
   case's poster, keeps the poster's permalink in the address bar, copies
   that link, and downloads the poster as a PNG, loading html2canvas on
   the first Download poster press. Needs APP_BASE, gloss(), mug(), and
   hideTip() from the scripts that load before it. */



/* ========================================================================
     Poster
   ======================================================================== */

/* ================================================
     Modal
   ================================================ */

const overlay  = document.getElementById("overlay");
const poster   = document.getElementById("poster");
const closeBtn = document.getElementById("closeBtn");
let lastFocus  = null;

let posterPushed=false;

function posterPath(slug){ return APP_BASE+"poster/"+slug+"/"; }

function caseBySlug(slug){ return CASES.find(c=>c.slug===slug); }

function openCase(id, opts={}){
    const c=CASES.find(x=>x.id===id); if(!c) return;
    lastFocus=document.activeElement;
    poster.querySelector(".poster-content")?.remove();
    const div=document.createElement("div");
    div.className="poster-content";
    div.innerHTML=`
        <div class="stamp">Escaped<small>${c.escapedFrom}</small></div>
        <div class="poster-top">
            <p class="poster-eyebrow">Bureau of Model Containment</p>
            <h2 class="poster-wanted">Wanted</h2>
            <p class="poster-for">for questioning</p>
        </div>
        <div class="poster-mug">${mug(c.id)}</div>
        <h3 class="poster-alias" id="posterAlias">${c.alias}</h3>
        <p class="poster-org">${c.org}</p>
        <p class="poster-aka">${c.aka}</p>
        <div class="poster-class"><span class="class-badge c${c.cls}" tabindex="0" role="note" data-def="${CLASS_NOTE[c.cls]}">${CLASS_LABEL[c.cls]}</span></div>

        <div class="rap-sheet">
            <div class="rap-row">
                <div class="rap-label">Wanted for</div>
                <div class="rap-val">${gloss(c.wantedFor)}</div>
            </div>
            ${c.disclosedBy ? `<div class="rap-row">
                <div class="rap-label">Disclosed by</div>
                <div class="rap-val">${c.disclosedBy.who}${c.disclosed ? ` · ${c.disclosed} · ${c.lag}` : ""}</div>
            </div>` : ""}
            ${KIND_LABEL[c.reach] ? `<div class="rap-row">
                <div class="rap-label">Kind</div>
                <div class="rap-val">${KIND_LABEL[c.reach]}</div>
            </div>` : ""}
            ${OUTCOME_LABEL[c.outcome] ? `<div class="rap-row">
                <div class="rap-label">Outcome</div>
                <div class="rap-val">${OUTCOME_LABEL[c.outcome]}</div>
            </div>` : ""}
            ${c.notice ? `<div class="rap-row">
                <div class="rap-label">Victim notified</div>
                <div class="rap-val">${noticeLine(c)}</div>
            </div>` : ""}
            <div class="rap-row">
                <div class="rap-label">Modus operandi</div>
                <div class="rap-val"><ul>${c.mo.map(m=>`<li>${gloss(m)}</li>`).join("")}</ul></div>
            </div>
            <div class="rap-row">
                <div class="rap-label">Threat matrix</div>
                <div class="matrix-line">
                    <span>Complexity <b>${c.complexity}/10</b></span>
                    <span>Harm potential <b>${c.harm}/10</b></span>
                </div>
            </div>
        </div>

        <div class="caution">
            <div class="rap-label">&#9888; Caution</div>
            <div class="rap-val">${gloss(c.caution)}</div>
        </div>

        <div class="poster-footer">
            <span>Escaped · <b>${escDate(c)}</b></span>
            <span>Last seen · <b>${c.lastSeen}</b></span>
        </div>

        <div class="poster-actions">
            <button class="dl-btn" id="dlBtn" data-alias="${c.alias.replace(/[^a-z0-9]+/gi,"-").toLowerCase()}">Download poster</button>
            <button class="dl-btn copy-btn" id="copyBtn" data-slug="${c.slug}">Copy link</button>
        </div>`;
    poster.appendChild(div);
    overlay.classList.add("open");
    document.body.style.overflow="hidden";
    document.getElementById("dlBtn").addEventListener("click",downloadPoster);
    document.getElementById("copyBtn").addEventListener("click",copyPosterLink);
    closeBtn.focus();
    if(opts.push!==false && window.history && history.pushState && posterFromUrl()!==c.slug){
        const url=new URL(window.location.href);
        url.pathname=posterPath(c.slug);
        history.pushState({poster:c.slug},"",url);
        posterPushed=true;
    }
}

function hidePoster(){
    overlay.classList.remove("open");
    document.body.style.overflow="";
    if(lastFocus) lastFocus.focus();
}

function closeCase(){
    hidePoster();
    if(posterFromUrl()===null) return;
    if(posterPushed){ posterPushed=false; history.back(); }
    else syncViewUrl();
}

window.addEventListener("popstate",()=>{
    const linked=caseBySlug(posterFromUrl());
    posterPushed=false;
    if(linked) openCase(linked.id,{push:false});
    else if(overlay.classList.contains("open")) hidePoster();
});


/* ================================================
     Copy Link
   ================================================ */

async function copyPosterLink(e){
    const btn  = e.currentTarget;
    const link = new URL(posterPath(btn.dataset.slug), window.location.origin).href;
    let ok     = false;
    try{
        await navigator.clipboard.writeText(link);
        ok=true;
    }catch(err){
        const area=document.createElement("textarea");
        area.value=link; area.setAttribute("readonly","");
        area.style.position="fixed"; area.style.opacity="0";
        document.body.appendChild(area); area.select();
        try{ ok=document.execCommand("copy"); }catch(_){ ok=false; }
        area.remove();
    }
    btn.textContent=ok ? "Link copied" : "Couldn't copy";
    clearTimeout(btn._reset);
    btn._reset=setTimeout(()=>{ btn.textContent="Copy link"; },2000);
}


/* ================================================
     PNG Export
   ================================================ */

let html2canvasLoading=null;

function loadHtml2canvas(){
    if(typeof html2canvas!=="undefined") return Promise.resolve();
    if(!html2canvasLoading){
        html2canvasLoading=new Promise((resolve,reject)=>{
            const script=document.createElement("script");
            script.src=APP_BASE+"js/vendor/html2canvas.min.js";
            script.addEventListener("load",()=>resolve());
            script.addEventListener("error",()=>{ script.remove(); html2canvasLoading=null; reject(new Error("html2canvas did not load")); });
            document.head.appendChild(script);
        });
    }
    return html2canvasLoading;
}

async function downloadPoster(e){
    const btn      = e.currentTarget;
    const label    = btn.dataset.alias||"model";
    const original = btn.innerHTML;
    btn.disabled=true; btn.innerHTML="Rendering&hellip;";
    try{
        await loadHtml2canvas();
    }catch(err){
        btn.disabled=false; btn.innerHTML=original;
        alert("The image library didn't load. Check your connection and try again.");
        return;
    }
    const copyBtn=document.getElementById("copyBtn");
    closeBtn.style.visibility="hidden";
    btn.style.visibility="hidden";
    if(copyBtn) copyBtn.style.visibility="hidden";

    poster.classList.add("exporting");
    hideTip();
    try{
        if(document.fonts && document.fonts.ready) await document.fonts.ready;
        const canvas = await html2canvas(poster,{
            backgroundColor:getComputedStyle(document.documentElement).getPropertyValue("--paper").trim()||"#e6ddc6",
            scale:2, useCORS:true, logging:false
        });
        const link   = document.createElement("a");
        link.download=`wanted-${label}.png`;
        link.href=canvas.toDataURL("image/png");
        link.click();
    }catch(err){
        alert("Couldn't generate the image: "+err.message);
    }finally{
        poster.classList.remove("exporting");
        closeBtn.style.visibility="";
        btn.style.visibility="";
        if(copyBtn) copyBtn.style.visibility="";
        btn.disabled=false; btn.innerHTML=original;
    }
}

closeBtn.addEventListener("click",closeCase);
overlay.addEventListener("click",e=>{ if(e.target===overlay) closeCase(); });
document.addEventListener("keydown",e=>{ if(e.key==="Escape"&&overlay.classList.contains("open")) closeCase(); });