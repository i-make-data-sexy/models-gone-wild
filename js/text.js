/* ================================================
     Glossary
   ================================================ */

const GLOSS_KEYS = Object.keys(GLOSSARY).sort((a,b)=>b.length-a.length);

const escDate = c => c.date + (c.estimated ? ' (est.)' : '');

const UNDATED = "Date not disclosed";

function noticeTag(c){
    const n = c.notice;
    if(!n) return '';
    const who  = n.plural ? 'Victims' : 'Victim';
    const text = n.kind==='told'  ? `${who} told ${n.gap}`
               : n.kind==='found' ? `${who} found it first`
               : n.kind==='untold'? `${who} not told before it went public`
               : '';
    return text ? `<div class="lag-tag">${text}</div>` : '';
}

function noticeLine(c){
    const n = c.notice;
    if(n.kind==='told')
        return `${n.who} · ${n.told} · ${n.gap}${n.how ? ` · ${n.how}` : ''}`;
    if(n.kind==='found')
        return `${n.who} found it on its own and disclosed it ${n.victimDisclosed}, before ${c.lab} linked it on ${n.knew}`;
    if(n.kind==='untold')
        return `${n.who} was not told by ${c.lab} before the case went public${n.how ? `, ${n.how}` : ''}`;
    return '';
}
const escAttr = s => s.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');

function gloss(html){
    if(!html) return html;
    const used = new Set();
    return html.split(/(<[^>]*>)/).map(chunk=>{
        if(chunk.startsWith('<')) return chunk;
        GLOSS_KEYS.forEach(k=>{
            if(used.has(k)) return;

            const re = new RegExp('(^|[^\\w-])('+k.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')(?![\\w-])','i');
            if(re.test(chunk)){
                used.add(k);
                chunk = chunk.replace(re, (m,pre,hit) =>
                    `${pre}<span class="term" tabindex="0" role="note" data-def="${escAttr(GLOSSARY[k])}">${hit}</span>`);
            }
        });
        return chunk;
    }).join('');
}