/* ========================================================================
     About This File
   ======================================================================== */

/* Applies the filters to every view, runs the options menu, and
   switches between the timeline, Threat Matrix, and Cases by Lab tabs,
   keeping each view's permalink in the address bar. It also works out
   APP_BASE, the app's own path, which the other scripts build their
   links from. */



/* ========================================================================
     Views
   ======================================================================== */

/* ================================================
     Apply Filters
   ================================================ */

const filterCount=document.getElementById('filterCount');
function applyFilters(){
    const list=filtered();
    renderTimeline(list);
    renderScatter(list);
    renderLabChart(list);
    [classSelect,outcomeSelect,kindSelect].forEach(s=>s.classList.toggle('is-active', !!s.value));
    const labs = selectedLabs();
    updateLabSummary(labs);
    const narrowed = !!(classSelect.value || labs.length || outcomeSelect.value || kindSelect.value);
    filterCount.hidden = !narrowed;
    filterCount.textContent = `Showing ${list.length} of ${CASES.length} files on record.`;

    optionsDot.hidden = !narrowed;
    optionsClear.hidden = !narrowed;
}

[classSelect,labList,outcomeSelect,kindSelect].forEach(s=>s.addEventListener('change',applyFilters));


/* ================================================
     Options Menu
   ================================================ */

const optionsMenu  = document.getElementById('optionsMenu');
const optionsDot   = document.getElementById('optionsDot');
const optionsClear = document.getElementById('optionsClear');

function closeOptions(returnFocus){
    optionsMenu.open = false;
    if(returnFocus) optionsMenu.querySelector('summary').focus();
}

document.addEventListener('click', e=>{
    if(optionsMenu.open && !optionsMenu.contains(e.target)) closeOptions(false);
});

document.addEventListener('keydown', e=>{
    if(e.key!=='Escape' || !optionsMenu.open || overlay.classList.contains('open')) return;

    if(labPicker.open){ labPicker.open=false; labSummary.focus(); return; }
    closeOptions(true);
});

document.getElementById('optionsClear').addEventListener('click', ()=>{
    [classSelect,outcomeSelect,kindSelect].forEach(s=>{ s.value=''; });
    labList.querySelectorAll('input').forEach(b=>{ b.checked=false; });
    labPicker.open = false;
    applyFilters();

    classSelect.focus();
});

document.getElementById('optionsClose').addEventListener('click', ()=>closeOptions(true));


/* ================================================
     View Tabs
   ================================================ */

const tabs       = document.querySelectorAll('.tab');
const VIEWS      = ['timeline','matrix','labs'];
const VIEW_SLUGS = {matrix:'threat-matrix', labs:'lab-counts'};

const APP_BASE=(function(){
    let p=window.location.pathname
        .replace(/index\.html$/,'')
        .replace(/(?:threat-matrix|lab-counts|poster\/[\w-]+)\/?$/,'');
    return p.endsWith('/') ? p : p+'/';
})();

const methodologyLink=document.getElementById('methodologyLink');
if(methodologyLink) methodologyLink.href=APP_BASE+'methodology/';

function viewFromUrl(){
    const seg=window.location.pathname.slice(APP_BASE.length).replace(/\/$/,'');
    for(const name in VIEW_SLUGS){ if(VIEW_SLUGS[name]===seg) return name; }
    return new URLSearchParams(window.location.search).get('view');
}

function posterFromUrl(){
    const m=window.location.pathname.slice(APP_BASE.length).match(/^poster\/([\w-]+)\/?$/);
    return m ? m[1] : null;
}

function syncViewUrl(){
    if(!window.history || !history.replaceState) return;
    const url=new URL(window.location.href);
    url.pathname=APP_BASE+(VIEW_SLUGS[currentView] ? VIEW_SLUGS[currentView]+'/' : '');
    url.searchParams.delete('view');
    if(url.href!==window.location.href) history.replaceState(null,'',url);
}

let currentView='timeline';

function showView(name, syncUrl){
    if(VIEWS.indexOf(name)===-1) name='timeline';
    currentView=name;
    tabs.forEach(t=>t.setAttribute('aria-selected', t.id==='tab-'+name ? 'true':'false'));
    document.querySelectorAll('.view').forEach(v=>{
        const on = v.id==='view-'+name;
        v.classList.toggle('active', on);
        v.hidden = !on;
    });

    if(name==='matrix') renderScatter(filtered());
    if(syncUrl) syncViewUrl();
}

tabs.forEach(tab=>{
    tab.addEventListener('click',()=>showView(tab.id.replace('tab-',''), true));
});