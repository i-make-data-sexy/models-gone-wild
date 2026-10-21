/* ========================================================================
     About This File
   ======================================================================== */

/* The search box at the top of the options menu. A plain search keeps
   the cases whose text holds every word typed, in any case. Advanced
   opens Match case, Match whole word, and Regex match, and any of them
   reads the whole box as one pattern. The search rides in the address
   as q, with case, word, and re for the three switches. Each card
   highlights what matched in its alias and charge, counts the matches
   on its poster, and quotes the poster when the card itself has none.
   An open poster highlights its matches under a strip that jumps to each. */



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
    posterHits.clear();

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

function matchRanges(text){
    const rx     = searchHighlighter;
    const ranges = [];
    let match;

    rx.lastIndex = 0;
    while((match = rx.exec(text))){
        if(!match[0]){ rx.lastIndex++; continue; }
        const start = match.index;
        const end   = start+match[0].length;
        const prev  = ranges[ranges.length-1];
        if(prev && /^\s*$/.test(text.slice(prev[1],start))) prev[1] = end;
        else ranges.push([start,end]);
    }
    return ranges;
}

function markText(node){
    const text   = node.nodeValue;
    const ranges = matchRanges(text);
    if(!ranges.length) return;

    const frag = document.createDocumentFragment();
    let last   = 0;
    ranges.forEach(([start,end])=>{
        const mark = document.createElement("mark");
        mark.className   = "search-hit";
        mark.textContent = text.slice(start,end);
        frag.append(text.slice(last,start), mark);
        last = end;
    });
    frag.append(text.slice(last));
    node.replaceWith(frag);
}

function highlightIn(root, skip){
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode: node=>skip && node.parentElement.closest(skip) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
    });
    const nodes  = [];
    while(walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(markText);
    return [...root.querySelectorAll("mark.search-hit")];
}

function highlightMatches(root){
    if(!searchHighlighter) return;
    root.querySelectorAll(".card").forEach(card=>{
        const c      = CASES.find(x=>x.id===card.dataset.id);
        const onCard = [...card.querySelectorAll(".card-alias, .card-charge")]
            .reduce((n,el)=>n+highlightIn(el).length,0);
        const hits   = posterMatches(c);
        if(!hits.count) return;

        markPosterButton(card.querySelector("[data-open]"), c, hits.count);
        if(!onCard) card.querySelector(".card-charge").after(excerptNote(hits.excerpt));
    });
}


/* ================================================
     Poster Matches
   ================================================ */

const POSTER_SKIP   = ".poster-mug, svg, .poster-actions, .poster-message";
const EXCERPT_BLOCK = "li, .rap-val, .poster-alias, .poster-org, .poster-aka, .poster-footer span, .stamp, .class-badge";
const posterHits    = new Map();

function matchCountLabel(n){
    return `${n} match${n===1 ? "" : "es"}`;
}

function excerptAround(mark){
    const block = mark.closest(EXCERPT_BLOCK) || mark.parentElement;
    const range = document.createRange();
    range.setStart(block,0);
    range.setEndBefore(mark);

    const text  = block.textContent.replace(/\s+/g," ");
    const start = range.toString().replace(/\s+/g," ").length;
    const end   = start+mark.textContent.length;
    let before  = text.slice(Math.max(0,start-70),start);
    let after   = text.slice(end,end+90);

    const sentence = [...before.matchAll(/[.!?]\s/g)].pop();
    if(sentence) before = before.slice(sentence.index+2);
    else if(start>70) before = "\u2026"+before.replace(/^\S*\s/,"");
    if(end+90<text.length) after = after.replace(/\s\S*$/,"")+"\u2026";
    return (before+text.slice(start,end)+after).trim();
}

function posterMatches(c){
    if(!posterHits.has(c.id)){
        const box     = document.createElement("div");
        box.innerHTML = posterHtml(c);

        const marks = highlightIn(box, POSTER_SKIP);
        posterHits.set(c.id, {count:marks.length, excerpt:marks.length ? excerptAround(marks[0]) : ""});
    }
    return posterHits.get(c.id);
}

function markPosterButton(btn, c, count){
    const label = `${matchCountLabel(count)} on the wanted poster`;
    const badge = document.createElement("span");
    badge.className   = "hit-count";
    badge.textContent = count;
    badge.setAttribute("aria-hidden","true");

    btn.classList.add("has-hits");
    btn.dataset.tip = label;
    btn.setAttribute("aria-label", `Open the wanted poster for ${c.alias}, ${label}`);
    btn.appendChild(badge);
}

function excerptNote(text){
    const note  = document.createElement("p");
    const label = document.createElement("span");
    const quote = document.createElement("span");
    note.className    = "card-excerpt";
    label.className   = "card-excerpt-label";
    label.textContent = "On the poster";
    quote.textContent = text;
    note.append(label, quote);
    highlightIn(quote);
    return note;
}

function markPoster(content){
    if(!searchHighlighter) return;
    const marks = highlightIn(content, POSTER_SKIP);
    if(!marks.length) return;

    const strip = document.createElement("div");
    const count = document.createElement("span");
    const jump  = document.createElement("button");
    strip.className   = "poster-matches";
    count.className   = "poster-matches-count";
    count.textContent = `${matchCountLabel(marks.length)} for "${searchQuery}"`;
    jump.type         = "button";
    jump.className    = "poster-jump";
    strip.append(count, jump);
    content.prepend(strip);
    content.classList.add("has-matches");

    let next       = 0;
    const setLabel = ()=>{ jump.textContent = marks.length===1 ? "Jump to it" : `Jump to ${next+1} of ${marks.length}`; };
    setLabel();
    jump.addEventListener("click", ()=>{
        marks.forEach(m=>m.classList.remove("is-current"));
        const mark = marks[next];
        mark.classList.add("is-current");
        mark.scrollIntoView({block:"center", behavior:matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth"});
        next = (next+1)%marks.length;
        setLabel();
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