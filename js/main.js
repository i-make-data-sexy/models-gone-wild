/* ================================================
     Init
   ================================================ */

applyFilters();

const startCase=caseBySlug(posterFromUrl());
showView(viewFromUrl(), !startCase);
if(startCase) openCase(startCase.id,{push:false});

if(document.fonts && document.fonts.ready){ document.fonts.ready.then(()=>{ renderScatter(filtered()); renderLabChart(filtered()); }); }