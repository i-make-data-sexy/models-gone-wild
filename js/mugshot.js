/* ================================================
     Mugshot Generator
   ================================================ */

const M_INK = '#1c1a15', M_PAPER='#efe7d2', M_WHITE='#fbf7ec', M_BACK='#cfc4a6';
const M_LW  = 2.6;


/* ===============================
     Shared Furniture
   =============================== */

function heightChart(){
  let t       = '';
  const marks = [[26,""],[52,"6'0\""],[78,""],[104,"5'0\""],[130,""],[156,"4'0\""],[182,""]];
  marks.forEach(([y,label])=>{
    t+=`<line x1="0" y1="${y}" x2="190" y2="${y}" stroke="${M_INK}" stroke-width="1" opacity="${label?0.28:0.16}"/>`;
    if(label){
      t+=`<text x="4" y="${y-3}" fill="${M_INK}" opacity=".5" font-family="'Courier Prime',monospace" font-size="8">${label}</text>`;
    }
  });
  return `<rect width="190" height="230" fill="${M_BACK}"/>`+t;
}

function torso(uid){
  const torso = "M16 270 L52 182 H138 L174 270 Z";
  return `<defs><clipPath id="sh${uid}"><path d="${torso}"/></clipPath></defs>`
    + `<path d="M78 146 H112 V192 H78 Z" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="${M_LW}"/>`
    + `<path d="${torso}" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="${M_LW}"/>`
    + `<g clip-path="url(#sh${uid})">`
    + [192,204,216,228,240,252,264].map(y=>`<line x1="10" y1="${y}" x2="180" y2="${y}" stroke="${M_INK}" stroke-width="7"/>`).join('')
    + `</g>`;
}
function bookingPlate(n){
  return `<rect x="26" y="200" width="138" height="20" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="2"/>`
    + `<text x="95" y="215" text-anchor="middle" fill="${M_INK}" font-family="'Courier Prime',monospace" font-size="12" letter-spacing="1.5">BMC-${n}</text>`;
}
const brow  = d => `<path d="${d}" fill="none" stroke="${M_INK}" stroke-width="5" stroke-linecap="round"/>`;
const mLine = (d,w=M_LW) => `<path d="${d}" fill="none" stroke="${M_INK}" stroke-width="${w}" stroke-linecap="round"/>`;


/* ===============================
     Skulls
   =============================== */

const HEADS = {
  square: { earX:46, d:'<rect x="46" y="44" width="98" height="112" rx="30"/>' },
  round:  { earX:46, d:'<ellipse cx="95" cy="100" rx="50" ry="54"/>' },
  long:   { earX:53, d:'<ellipse cx="95" cy="98" rx="42" ry="60"/>' },
  taper:  { earX:49, d:'<path d="M95 42 C128 42 141 64 141 90 C141 118 120 154 95 154 C70 154 49 118 49 90 C49 64 62 42 95 42 Z"/>' }
};


/* ===============================
     Noses
   =============================== */

const NOSES = {
  hook:     mLine("M96 100 Q102 114 93 115", 2.4),
  button:   `<ellipse cx="95" cy="112" rx="6" ry="4.5" fill="none" stroke="${M_INK}" stroke-width="2.4"/>`,
  straight: mLine("M95 100 V113 Q95 116 91 116", 2.4),
  wide:     mLine("M86 110 Q95 118 104 110", 2.6)
};


/* ===============================
     Hair
   =============================== */

const HAIR = {
  part: `<path d="M45 80 C43 48 68 34 96 34 C126 34 146 50 147 78
                   C140 62 124 56 104 58 C88 60 70 66 60 84 Z" fill="${M_INK}"/>
         <path d="M104 58 C118 56 132 60 141 70 C132 54 118 46 104 46 Z" fill="${M_INK}"/>`,
  tousle: `<path d="M44 84 C42 48 70 32 96 32 C124 32 148 48 146 84
                     C140 70 138 62 130 68 C124 58 116 66 110 58
                     C102 68 96 58 88 66 C80 56 72 68 64 62
                     C56 68 52 72 44 84 Z" fill="${M_INK}"/>`,
  coil: (()=>{
    let c     = '';
    const pts = [[54,74],[62,58],[76,46],[95,41],[114,46],[128,58],[136,74]];
    pts.forEach(([x,y])=>{ c+=`<circle cx="${x}" cy="${y}" r="15" fill="${M_INK}"/>`; });
    return `<path d="M46 86 C46 50 70 36 95 36 C120 36 144 50 144 86 Z" fill="${M_INK}"/>`+c;
  })(),
  fringe: `<path d="M46 92 C46 46 70 31 95 31 C120 31 144 46 144 92
                     L144 70 C120 83 70 83 46 70 Z" fill="${M_INK}"/>`,
  crop: `<path d="M47 80 C47 48 70 36 95 36 C120 36 143 48 143 80
                   C138 62 120 54 95 54 C70 54 52 62 47 80 Z" fill="${M_INK}"/>`
};


/* ===============================
     The Four Faces
   =============================== */

const FACES = {
  sol: { head:'square', nose:'hook', hair:'part', dy:24, f:`
      <ellipse cx="76" cy="96" rx="13" ry="11" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
      <ellipse cx="114" cy="96" rx="13" ry="11" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
      <circle cx="80" cy="88" r="5" fill="${M_INK}"/><circle cx="118" cy="88" r="5" fill="${M_INK}"/>
      ${mLine("M63 92 Q76 82 89 92",4)}${mLine("M101 92 Q114 82 127 92",4)}
      ${brow("M60 74 H88")}
      ${brow("M102 70 Q116 62 130 72")}
      ${mLine("M70 139 H106 Q117 139 121 129")}` },

  claude: { head:'round', nose:'button', hair:'tousle', dy:2, tilt:-7, f:`
      <circle cx="76" cy="98" r="14" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
      <circle cx="114" cy="98" r="11.5" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
      <circle cx="76" cy="95" r="5" fill="${M_INK}"/><circle cx="114" cy="97" r="4.6" fill="${M_INK}"/>
      ${mLine("M103 92 Q114 87 125 93",3)}
      ${brow("M60 79 Q76 68 92 74")}
      ${brow("M104 80 Q116 78 129 85")}
      ${mLine("M80 141 Q90 135 101 140",2.8)}` },

  spark: { head:'long', nose:'straight', hair:'coil', dy:-10, f:`
      <ellipse cx="78" cy="96" rx="12" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
      <ellipse cx="112" cy="96" rx="12" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
      <circle cx="71" cy="91" r="4.4" fill="${M_INK}"/><circle cx="105" cy="91" r="4.4" fill="${M_INK}"/>
      ${brow("M64 74 Q78 68 90 74")}
      ${brow("M126 74 Q112 68 100 74")}
      <ellipse cx="88" cy="140" rx="5.5" ry="6.5" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="3"/>
      ${mLine("M104 133 Q110 140 104 147",2.2)}${mLine("M113 128 Q122 140 113 152",2.2)}` },

  kimi: { head:'taper', nose:'wide', hair:'fringe', dy:10, f:`
      <ellipse cx="76" cy="98" rx="13" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
      <ellipse cx="114" cy="98" rx="13" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
      <circle cx="86" cy="100" r="5" fill="${M_INK}"/><circle cx="124" cy="100" r="5" fill="${M_INK}"/>
      ${mLine("M64 93 Q76 89 88 93",3)}${mLine("M102 93 Q114 89 126 93",3)}
      ${brow("M62 80 H86")}
      ${brow("M104 76 H128")}
      ${mLine("M68 137 Q77 129 86 137 Q95 145 104 137 Q113 129 122 136")}` },

  _default: { head:'round', nose:'straight', hair:'crop', dy:0, f:`
      <ellipse cx="76" cy="98" rx="13" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
      <ellipse cx="114" cy="98" rx="13" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
      <circle cx="76" cy="98" r="4.6" fill="${M_INK}"/><circle cx="114" cy="98" r="4.6" fill="${M_INK}"/>
      ${brow("M60 77 H88")}${brow("M102 77 H130")}
      ${mLine("M74 138 H116")}` }
};

function mug(seed){
  let h=2166136261>>>0;
  for(let i=0;i<seed.length;i++){ h=Math.imul(h^seed.charCodeAt(i),16777619); }
  h=Math.imul(h^(h>>>16),0x7feb352d); h=(h^(h>>>15))>>>0;
  const uid     = seed.replace(/[^a-z0-9]/gi,'');
  const cfg     = FACES[seed]||FACES._default;
  const skull   = HEADS[cfg.head];
  const headSvg = `<g fill="${M_PAPER}" stroke="${M_INK}" stroke-width="${M_LW}">`
    + `<ellipse cx="${skull.earX}" cy="106" rx="7" ry="11"/>`
    + `<ellipse cx="${190-skull.earX}" cy="106" rx="7" ry="11"/>`
    + skull.d + `</g>`;

  const dy = cfg.dy || 0;

  const tilt       = cfg.tilt || 0;
  const above      = headSvg + HAIR[cfg.hair] + cfg.f + NOSES[cfg.nose];
  const skullGroup = tilt ? `<g transform="rotate(${tilt} 95 152)">${above}</g>` : above;
  const figure     = `<g transform="translate(0 ${dy})">` + torso(uid) + skullGroup + `</g>`;
  return `<svg viewBox="0 0 190 230" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">`
    + heightChart() + figure + bookingPlate(h%9000+1000) + `</svg>`;
}