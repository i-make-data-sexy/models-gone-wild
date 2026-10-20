/* ========================================================================
     About This File
   ======================================================================== */

/* Starts the page once every other script has loaded. It applies the
   filters, opens the view the address names and any poster it links to,
   or the "no file" notice when the poster link names no case, and redraws
   both charts once the fonts load so their labels measure correctly. */



/* ========================================================================
     Init
   ======================================================================== */

function init(){
    applyFilters();

    const startSlug=posterFromUrl();
    const startCase=caseBySlug(startSlug);
    showView(viewFromUrl(), !startSlug);
    if(startCase) openCase(startCase.id,{push:false});
    else if(startSlug) openMissing();

    if(document.fonts && document.fonts.ready){ document.fonts.ready.then(()=>{ renderScatter(filtered()); renderLabChart(filtered()); }); }
}

init();