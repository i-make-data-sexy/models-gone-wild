/* ================================================
     Tooltip
   ================================================ */

const tip     = document.getElementById('tip');
const TIP_GAP = 10;
let tipFor    = null;

function positionTip(el){
  const text = el.dataset.def || el.dataset.tip;
  if(!text) return;
  tipFor = el;

  tip.innerHTML = text;
  tip.className = 'tip ' + (el.dataset.def ? 'tip-def' : 'tip-label')
    + (text.indexOf('tip-lede') > -1 ? ' tip-scores' : '');

  tip.style.left = '0px';
  tip.style.top = '0px';
  tip.classList.add('show');

  const t      = (el.querySelector('circle.axis-icon') || el).getBoundingClientRect();
  const b      = tip.getBoundingClientRect();
  const column = el.closest('.poster') ? null : document.querySelector('.content');
  const c      = column ? column.getBoundingClientRect() : null;

  const minX = Math.max(TIP_GAP, c ? c.left + TIP_GAP : TIP_GAP);
  const maxX = Math.min(window.innerWidth - TIP_GAP, c ? c.right - TIP_GAP : window.innerWidth - TIP_GAP);

  let x = t.left + t.width/2 - b.width/2;
  if(x + b.width > maxX) x = maxX - b.width;
  if(x < minX) x = minX;

  const roomAbove = t.top - TIP_GAP;
  const roomBelow = window.innerHeight - t.bottom - TIP_GAP;
  let y, placement;
  if(b.height <= roomAbove){
    y = t.top - b.height - TIP_GAP; placement = 'above';
  } else if(b.height <= roomBelow){
    y = t.bottom + TIP_GAP; placement = 'below';
  } else if(roomAbove >= roomBelow){
    y = t.top - b.height - TIP_GAP; placement = 'above';
  } else {
    y = t.bottom + TIP_GAP; placement = 'below';
  }
  y = Math.max(TIP_GAP, Math.min(y, window.innerHeight - b.height - TIP_GAP));

  tip.style.left = Math.round(x) + 'px';
  tip.style.top  = Math.round(y) + 'px';
  tip.classList.add(placement);

  const arrow = Math.min(Math.max(t.left + t.width/2 - x, 12), b.width - 12);
  tip.style.setProperty('--arrow', Math.round(arrow) + 'px');
}

function hideTip(){
  tip.classList.remove('show','above','below');
  tipFor = null;
}

['mouseenter','focus'].forEach(ev=>{
  document.addEventListener(ev, e=>{
    const el = e.target.closest && e.target.closest('[data-def],[data-tip]');
    if(el) positionTip(el);
  }, true);
});
['mouseleave','blur'].forEach(ev=>{
  document.addEventListener(ev, e=>{
    const el = e.target.closest && e.target.closest('[data-def],[data-tip]');
    if(el && el === tipFor) hideTip();
  }, true);
});

window.addEventListener('scroll', hideTip, true);
window.addEventListener('resize', hideTip);

let scatterResize = null, scatterWidth = 0;
window.addEventListener('resize', ()=>{
  clearTimeout(scatterResize);
  scatterResize = setTimeout(()=>{
    const w = Math.floor(scatterHost.clientWidth);
    if(currentView==='matrix' && w !== scatterWidth){ scatterWidth = w; renderScatter(filtered()); }
  }, 150);
});
document.addEventListener('keydown', e=>{ if(e.key==='Escape') hideTip(); });