/* ========================================================================
     About This File
   ======================================================================== */

/* The search box at the top of the options menu. A plain search keeps
   the cases whose text holds every word typed, in any case. Advanced
   opens Match case, Match whole word, and Regex match, and any of them
   reads the whole box as one pattern. The search rides in the address
   as q, with case, word, and re for the three switches, and each card
   highlights what matched in its alias and charge. */



/* ========================================================================
     Search
   ======================================================================== */

/* ================================================
     Search State
   ================================================ */

const searchForm     = document.getElementById("searchForm");
const searchInput    = document.getElementById("searchInput");
const searchError    = document.getElementById("searchError");
const advancedToggle = document.getElementById("advancedToggle");
const advancedModes  = document.getElementById("advancedModes");
const matchCase      = document.getElementById("matchCase");
const matchWord      = document.getElementById("matchWord");
const matchRegex     = document.getElementById("matchRegex");

const SEARCH_MODES   = [["case",matchCase],["word",matchWord],["re",matchRegex]];
const ADVANCED_KEY   = "mgw:advanced-search";
const SEARCH_FIELDS  = ["alias","aka","lab","org","charge","wantedFor","mo","caution","escapedFrom","lastSeen","whyComplexity","whyHarm","date","disclosed"];

let searchQuery       = "";
let searchMatcher     = null;
let searchHighlighter = null;

function anyModeOn(){
    return SEARCH_MODES.some(([,box])=>box.checked);
}


/* ================================================
     Case Text
   ================================================ */

const caseText = new Map();

function searchableText(c){
    if(!caseText.has(c.id)){
        const parts = SEARCH_FIELDS.flatMap(k=>c[k] ?? []);
        [c.source?.outlet, c.disclosedBy?.who, c.notice?.who, c.notice?.how].forEach(v=>{ if(v) parts.push(v); });
        caseText.set(c.id, parts.map(String));
    }
    return caseText.get(c.id);
}


/* ================================================
     Matching
   ================================================ */

function escapeRegex(text){
    return text.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");
}

function buildMatcher(query){
    if(!anyModeOn()){
        const words = [...new Set(query.toLowerCase().split(/\s+/).filter(Boolean))];
        return texts=>{
            const all = texts.join("\n").toLowerCase();
            return words.every(w=>all.includes(w));
        };
    }

    const rx = new RegExp(literalPattern(query), matchCase.checked ? "" : "i");
    return texts=>texts.some(t=>rx.test(t));
}

function literalPattern(query){
    const pattern = matchRegex.checked ? query : escapeRegex(query);
    return matchWord.checked ? "\\b(?:"+pattern+")\\b" : pattern;
}

function buildHighlighter(query){
    if(anyModeOn()) return new RegExp(literalPattern(query), matchCase.checked ? "g" : "gi");
    const words = [...new Set(query.toLowerCase().split(/\s+/).filter(Boolean))]
        .sort((a,b)=>b.length-a.length)
        .map(escapeRegex);
    return new RegExp(words.join("|"),"gi");
}

function matchesSearch(c){
    return !searchMatcher || searchMatcher(searchableText(c));
}

function updateMatcher(){
    const query = searchInput.value.trim();
    searchQuery       = "";
    searchMatcher     = null;
    searchHighlighter = null;

    searchError.hidden = true;
    searchInput.removeAttribute("aria-invalid");
    if(!query) return;

    try{
        searchMatcher     = buildMatcher(query);
        searchHighlighter = buildHighlighter(query);
        searchQuery       = query;
    }catch(_){
        searchError.textContent = "That regex has an error in it, so the search isn't applied yet.";
        searchError.hidden = false;
        searchInput.setAttribute("aria-invalid","true");
    }
}


/* ================================================
     Highlighting
   ================================================ */

function markText(node){
    const text = node.nodeValue;
    const rx   = searchHighlighter;
    const frag = document.createDocumentFragment();
    let last   = 0;
    let match;

    rx.lastIndex = 0;
    while((match = rx.exec(text))){
        if(!match[0]){ rx.lastIndex++; continue; }
        const mark = document.createElement("mark");
        mark.className   = "search-hit";
        mark.textContent = match[0];
        frag.append(text.slice(last,match.index), mark);
        last = match.index+match[0].length;
    }
    if(!last) return;

    frag.append(text.slice(last));
    node.replaceWith(frag);
}

function highlightMatches(root){
    if(!searchHighlighter) return;
    root.querySelectorAll(".card-alias, .card-charge").forEach(el=>{
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        const nodes  = [];
        while(walker.nextNode()) nodes.push(walker.currentNode);
        nodes.forEach(markText);
    });
}


/* ================================================
     Empty Note
   ================================================ */

function emptyNote(){
    const filtersOn = !!(classSelect.value || selectedLabs().length || outcomeSelect.value || kindSelect.value);
    const text      = searchQuery && filtersOn ? "No files match the current search and filters."
                    : searchQuery              ? "No files match this search."
                    :                            "No files match the current filters.";
    return `<p class="empty-note">${text}</p>`;
}


/* ================================================
     Address Bar
   ================================================ */

function readSearchUrl(){
    const params = new URLSearchParams(window.location.search);
    searchInput.value = params.get("q") || "";
    SEARCH_MODES.forEach(([name,box])=>{ box.checked = params.get(name)==="1"; });

    let advancedOn = anyModeOn();
    try{ if(sessionStorage.getItem(ADVANCED_KEY)==="on") advancedOn = true; }catch(_){}
    advancedToggle.checked = advancedOn;
    advancedModes.hidden   = !advancedOn;

    updateMatcher();
}

function syncSearchUrl(){
    if(!window.history || !history.replaceState) return;
    const url   = new URL(window.location.href);
    const query = searchInput.value.trim();
    if(query) url.searchParams.set("q",query);
    else url.searchParams.delete("q");
    SEARCH_MODES.forEach(([name,box])=>{
        if(box.checked) url.searchParams.set(name,"1");
        else url.searchParams.delete(name);
    });
    if(url.href!==window.location.href) history.replaceState(history.state,"",url);
}

function runSearch(){
    updateMatcher();
    syncSearchUrl();
    applyFilters();
}

function clearSearch(){
    searchInput.value = "";
    SEARCH_MODES.forEach(([,box])=>{ box.checked = false; });
    updateMatcher();
    syncSearchUrl();
}


/* ================================================
     Search Events
   ================================================ */

searchForm.addEventListener("submit", e=>{
    e.preventDefault();
    runSearch();
});

searchInput.addEventListener("keydown", e=>{
    if(e.key!=="Escape" || !searchInput.value) return;
    e.preventDefault();
    searchInput.value = "";
    runSearch();
});

searchInput.addEventListener("input", ()=>{
    if(!searchInput.value.trim() && (searchQuery || !searchError.hidden)) runSearch();
});

SEARCH_MODES.forEach(([,box])=>box.addEventListener("change",runSearch));

advancedToggle.addEventListener("change", ()=>{
    advancedModes.hidden = !advancedToggle.checked;
    try{
        if(advancedToggle.checked) sessionStorage.setItem(ADVANCED_KEY,"on");
        else sessionStorage.removeItem(ADVANCED_KEY);
    }catch(_){}

    if(advancedToggle.checked || !anyModeOn()) return;
    SEARCH_MODES.forEach(([,box])=>{ box.checked = false; });
    runSearch();
});