/* ========================================================================
     About This File
   ======================================================================== */

/* Starts the page once every other script has loaded. It applies the
   filters, opens the view the address names and any poster it links to,
   and redraws both charts once the fonts load so their labels measure
   correctly. */



/* ========================================================================
     Init
   ======================================================================== */

applyFilters();

const startCase=caseBySlug(posterFromUrl());
showView(viewFromUrl(), !startCase);
if(startCase) openCase(startCase.id,{push:false});

if(document.fonts && document.fonts.ready){ document.fonts.ready.then(()=>{ renderScatter(filtered()); renderLabChart(filtered()); }); }