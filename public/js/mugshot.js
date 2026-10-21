/* ========================================================================
     About This File
   ======================================================================== */

/* The mugshot generator, which draws each case's booking photo as
   inline SVG from a shared height chart, torso, and booking plate, plus
   a skull, nose, hair, eyes, and accessories for each face. Every model
   has its own face, keyed by case id; a repeat offender's later cases
   name the earlier face in their face field, and
   scripts/check_mugshots.py fails on a case that draws the default face.
   mug() returns the SVG for a case. */



/* ========================================================================
     Mugshot Generator
   ======================================================================== */

const M_INK = cssToken("--ink"), M_PAPER=cssToken("--mug-paper"), M_WHITE=cssToken("--mug-white"), M_BACK=cssToken("--mug-wall");
const M_LW  = 2.6;


/* ================================================
     Shared Furniture
   ================================================ */

function heightChart(){
    let t       = "";
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
        + [192,204,216,228,240,252,264].map(y=>`<line x1="10" y1="${y}" x2="180" y2="${y}" stroke="${M_INK}" stroke-width="7"/>`).join("")
        + `</g>`;
}
function bookingPlate(n){
    return `<rect x="26" y="200" width="138" height="20" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="2"/>`
        + `<text x="95" y="215" text-anchor="middle" fill="${M_INK}" font-family="'Courier Prime',monospace" font-size="12" letter-spacing="1.5">BMC-${n}</text>`;
}
const brow  = d => `<path d="${d}" fill="none" stroke="${M_INK}" stroke-width="5" stroke-linecap="round"/>`;
const mLine = (d,w=M_LW) => `<path d="${d}" fill="none" stroke="${M_INK}" stroke-width="${w}" stroke-linecap="round"/>`;
const mFill = (d,o=1) => `<path d="${d}" fill="${M_INK}" opacity="${o}"/>`;
const dots  = (pts,r,o=1) => pts.map(([x,y])=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${M_INK}" opacity="${o}"/>`).join("");


/* ================================================
     Skulls
   ================================================ */

const HEADS = {
    square: { earX:46, d:'<rect x="46" y="44" width="98" height="112" rx="30"/>' },
    round:  { earX:46, d:'<ellipse cx="95" cy="100" rx="50" ry="54"/>' },
    long:   { earX:53, d:'<ellipse cx="95" cy="98" rx="42" ry="60"/>' },
    taper:  { earX:49, d:'<path d="M95 42 C128 42 141 64 141 90 C141 118 120 154 95 154 C70 154 49 118 49 90 C49 64 62 42 95 42 Z"/>' }
};


/* ================================================
     Noses
   ================================================ */

const NOSES = {
    hook:     mLine("M96 100 Q102 114 93 115", 2.4),
    button:   `<ellipse cx="95" cy="112" rx="6" ry="4.5" fill="none" stroke="${M_INK}" stroke-width="2.4"/>`,
    straight: mLine("M95 100 V113 Q95 116 91 116", 2.4),
    wide:     mLine("M86 110 Q95 118 104 110", 2.6)
};


/* ================================================
     Hair
   ================================================ */

const HAIR = {
    part:     `<path d="M45 80 C43 48 68 34 96 34 C126 34 146 50 147 78
                     C140 62 124 56 104 58 C88 60 70 66 60 84 Z" fill="${M_INK}"/>
           <path d="M104 58 C118 56 132 60 141 70 C132 54 118 46 104 46 Z" fill="${M_INK}"/>`,
    tousle:   `<path d="M44 84 C42 48 70 32 96 32 C124 32 148 48 146 84
                       C140 70 138 62 130 68 C124 58 116 66 110 58
                       C102 68 96 58 88 66 C80 56 72 68 64 62
                       C56 68 52 72 44 84 Z" fill="${M_INK}"/>`,
    coil:     (()=>{
        let c     = "";
        const pts = [[54,74],[62,58],[76,46],[95,41],[114,46],[128,58],[136,74]];
        pts.forEach(([x,y])=>{ c+=`<circle cx="${x}" cy="${y}" r="15" fill="${M_INK}"/>`; });
        return `<path d="M46 86 C46 50 70 36 95 36 C120 36 144 50 144 86 Z" fill="${M_INK}"/>`+c;
    })(),
    fringe:   `<path d="M46 92 C46 46 70 31 95 31 C120 31 144 46 144 92
                       L144 70 C120 83 70 83 46 70 Z" fill="${M_INK}"/>`,
    crop:     `<path d="M47 80 C47 48 70 36 95 36 C120 36 143 48 143 80
                     C138 62 120 54 95 54 C70 54 52 62 47 80 Z" fill="${M_INK}"/>`,
    longPart: mFill("M44 100 C42 50 68 31 95 31 C122 31 148 50 146 100 C142 66 120 50 95 48 C70 50 48 66 44 100 Z"),
    ponytail: mFill("M46 86 C46 48 70 34 95 34 C120 34 144 48 144 86 C136 62 118 54 95 54 C72 54 54 62 46 86 Z")
        + `<rect x="128" y="54" width="10" height="14" rx="3" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="2" transform="rotate(-30 133 61)"/>`,
    phillies: mFill("M54 88 C52 70 56 62 62 60 L60 92 Z") + mFill("M136 88 C138 70 134 62 128 60 L130 92 Z")
        + mFill("M44 80 C44 36 68 24 95 24 C122 24 146 36 146 80 Z")
        + `<ellipse cx="95" cy="80" rx="60" ry="9" fill="${M_INK}"/>`
        + `<circle cx="95" cy="26" r="4" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="1.5"/>`
        + `<path d="M86 46 C88 36 108 32 111 42 C113 51 103 56 96 53 M96 39 C98 50 98 62 95 68 C93 73 87 74 86 69" fill="none" stroke="${M_PAPER}" stroke-width="4.6" stroke-linecap="round"/>`
        + `<circle cx="86" cy="46" r="3.3" fill="${M_PAPER}"/><circle cx="86" cy="69" r="3.1" fill="${M_PAPER}"/>`,
    bob:      mFill("M45 78 C45 44 69 30 95 30 C121 30 145 44 145 78 Z")
        + mFill("M45 76 L40 150 L55 150 L52 76 Z") + mFill("M145 76 L150 150 L135 150 L138 76 Z"),
    pixie:    mFill("M44 92 C38 50 66 31 97 31 C128 31 150 48 146 84 C130 70 102 72 72 98 C66 88 56 84 44 92 Z"),
    waves:    mFill("M44 100 C42 50 70 31 102 31 C128 31 148 48 146 92 C140 66 126 54 112 50 C88 54 60 68 44 100 Z"),
    curls:    mFill("M46 86 C46 50 70 36 95 36 C120 36 144 50 144 86 Z")
        + dots([[52,74],[60,56],[76,44],[95,40],[114,44],[130,56],[138,74],[48,92],[142,92]],13),
    braids:   mFill("M45 92 C44 50 68 34 95 34 C122 34 146 50 145 92 C140 66 120 52 95 50 C70 52 50 66 45 92 Z")
        + [0,1,2,3,4,5].map(i=>`<ellipse cx="${40-i*0.6}" cy="${112+i*12}" rx="9" ry="8" fill="${M_INK}"/><ellipse cx="${150+i*0.6}" cy="${112+i*12}" rx="9" ry="8" fill="${M_INK}"/>`).join("")
        + `<rect x="30" y="178" width="14" height="6" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="2"/><rect x="147" y="178" width="14" height="6" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="2"/>`,
    beanie:   mFill("M42 82 C42 38 68 24 95 24 C122 24 148 38 148 82 Z")
        + `<rect x="40" y="70" width="110" height="16" rx="5" fill="${M_INK}"/>`
        + [50,60,70,80,90,100,110,120,130,140].map(x=>`<line x1="${x}" y1="72" x2="${x}" y2="84" stroke="${M_PAPER}" stroke-width="1.6" opacity=".7"/>`).join("")
        + `<circle cx="95" cy="20" r="10" fill="${M_INK}"/>`,
    mohawk:   mFill("M82 62 L80 20 L86 30 L89 12 L95 24 L101 10 L104 28 L110 18 L108 62 Z"),
    bald:     mLine("M112 54 Q124 58 130 68",2.4),
    flattop:  mFill("M52 84 L52 52 Q52 30 74 30 H116 Q138 30 138 52 L138 84 C134 64 118 58 95 58 C72 58 56 64 52 84 Z"),
    slick:    mFill("M46 84 C46 42 70 30 95 30 C120 30 144 42 144 84 C140 64 124 52 95 52 C66 52 50 64 46 84 Z")
        + `<path d="M70 46 Q95 36 124 46 M64 54 Q95 42 130 54" fill="none" stroke="${M_PAPER}" stroke-width="1.6" stroke-linecap="round"/>`,
    combover: mLine("M54 70 Q90 52 138 66",2.4) + mLine("M56 76 Q92 58 140 72",2.4) + mLine("M58 82 Q94 64 140 78",2.4)
        + mFill("M45 104 C44 90 46 82 50 78 L52 104 Z") + mFill("M145 104 C146 90 144 82 140 78 L138 104 Z"),
    cap:      mFill("M44 80 C44 36 68 24 95 24 C122 24 146 36 146 80 Z")
        + `<ellipse cx="95" cy="80" rx="62" ry="9" fill="${M_INK}"/>`
        + `<circle cx="95" cy="26" r="4" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="1.5"/>`
        + `<path d="M95 30 V78" stroke="${M_PAPER}" stroke-width="1.4"/>`,
    messy:    mFill("M42 88 C34 56 52 30 80 26 L84 14 L92 26 L104 12 L108 26 L124 18 L122 32 C146 40 154 66 148 88 C140 66 126 60 112 64 C104 54 94 64 86 56 C78 64 64 60 42 88 Z")
};

// Back layers drawn behind the shoulders
const HAIR_BACK = {
    longPart: mFill("M41 100 C38 44 66 28 95 28 C124 28 152 44 149 100 L151 196 L39 196 Z"),
    ponytail: mFill("M126 52 C168 44 176 100 160 160 C156 124 150 94 132 72 Z"),
    phillies: mFill("M120 66 C158 64 166 110 150 162 C148 128 140 100 126 84 Z"),
    bob:      mFill("M38 100 C36 42 66 27 95 27 C124 27 154 42 152 100 L154 152 Q95 160 36 152 Z"),
    waves:    mFill("M41 100 C37 44 66 28 95 28 C124 28 153 44 149 100 Q159 122 148 142 Q159 164 148 186 L42 186 Q31 164 42 142 Q31 122 41 100 Z"),
    braids:   mFill("M50 70 C36 82 30 98 32 114 L48 114 L50 90 Z") + mFill("M140 70 C154 82 160 98 158 114 L142 114 L140 90 Z"),
    curls:    dots([[44,96],[38,118],[40,140],[44,162],[146,96],[152,118],[150,140],[146,162],[52,178],[138,178]],15)
};


/* ================================================
     Eyes
   ================================================ */

const EYES = {
    plain:  (px=0,py=0) => `<ellipse cx="76" cy="98" rx="13" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>`
        + `<ellipse cx="114" cy="98" rx="13" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>`
        + dots([[76+px,98+py],[114+px,98+py]],4.6),
    almond: (px=0) => `<path d="M62 99 Q76 86 90 99 Q76 108 62 99 Z" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>`
        + `<path d="M100 99 Q114 86 128 99 Q114 108 100 99 Z" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>`
        + dots([[76+px,98],[114+px,98]],4.4),
    sleepy: () => `<ellipse cx="76" cy="99" rx="13" ry="9" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>`
        + `<ellipse cx="114" cy="99" rx="13" ry="9" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>`
        + dots([[76,102],[114,102]],4.4)
        + `<path d="M63 98 Q76 88 89 98 Z M101 98 Q114 88 127 98 Z" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="2.4"/>`,
    squint: () => mLine("M63 99 Q76 93 89 99",3) + mLine("M101 99 Q114 93 127 99",3) + dots([[76,99],[114,99]],3),
    wide:   (px=0,py=0) => `<circle cx="76" cy="97" r="14" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>`
        + `<circle cx="114" cy="97" r="14" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>`
        + dots([[76+px,97+py],[114+px,97+py]],4)
};


/* ================================================
     Accessories
   ================================================ */

const GEAR = {
    lashes:   mLine("M61 94 L56 89",2.2) + mLine("M64 90 L60 84",2.2) + mLine("M129 94 L134 89",2.2) + mLine("M126 90 L130 84",2.2),
    round:    `<g fill="none" stroke="${M_INK}" stroke-width="3"><circle cx="76" cy="98" r="17"/><circle cx="114" cy="98" r="17"/><path d="M93 96 Q95 92 97 96 M59 96 H46 M131 96 H144"/></g>`,
    square:   `<g fill="none" stroke="${M_INK}" stroke-width="3.4"><rect x="57" y="86" width="38" height="24" rx="3"/><rect x="95" y="86" width="38" height="24" rx="3"/><path d="M57 92 H47 M133 92 H143"/></g>`,
    cateye:   `<g fill="none" stroke="${M_INK}" stroke-width="3.4"><path d="M58 92 Q60 112 78 110 Q92 108 92 94 Q76 88 56 84 Z"/><path d="M132 92 Q130 112 112 110 Q98 108 98 94 Q114 88 134 84 Z"/><path d="M92 95 Q95 92 98 95"/></g>`,
    studs:    x => dots([[x,118],[190-x,118]],3.2),
    mole:     dots([[124,124]],2.6),
    freckles: dots([[64,118],[70,121],[66,124],[120,121],[126,118],[124,124]],1.6),
    stubble:  dots([[62,132],[68,140],[76,146],[86,150],[95,151],[104,150],[114,146],[122,140],[128,132],[70,134],[120,134],[80,142],[110,142]],1.2),
    bags:     mLine("M66 112 Q76 116 86 112",1.6) + mLine("M104 112 Q114 116 124 112",1.6),
    lips:     mFill("M80 137 Q88 131 95 135 Q102 131 110 137 Q95 148 80 137 Z"),
    stache:   mFill("M76 130 Q86 121 95 127 Q104 121 114 130 Q104 136 95 131 Q86 136 76 130 Z"),
    beard:    mFill("M46 112 C46 158 70 172 95 172 C120 172 144 158 144 112 C138 122 128 126 118 124 C110 122 102 120 95 122 C88 120 80 122 72 124 C62 126 52 122 46 112 Z")
        + `<ellipse cx="95" cy="141" rx="11" ry="4.5" fill="${M_PAPER}" stroke="${M_INK}" stroke-width="2"/>`,
    goatee:   mFill("M86 146 Q95 162 104 146 Q95 150 86 146 Z"),
    smirk:    mLine("M78 138 Q96 142 112 132",2.8),
    smile:    mLine("M78 134 Q95 146 112 134",2.8),
    frown:    mLine("M78 140 Q95 131 112 140",2.8),
    flat:     mLine("M76 138 H114")
};


/* ================================================
     Faces
   ================================================ */

const FACES = {
    sol: { head:"square", nose:"hook", hair:"part", dy:24, f:`
            <ellipse cx="76" cy="96" rx="13" ry="11" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
            <ellipse cx="114" cy="96" rx="13" ry="11" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
            <circle cx="80" cy="88" r="5" fill="${M_INK}"/><circle cx="118" cy="88" r="5" fill="${M_INK}"/>
            ${mLine("M63 92 Q76 82 89 92",4)}${mLine("M101 92 Q114 82 127 92",4)}
            ${brow("M60 74 H88")}
            ${brow("M102 70 Q116 62 130 72")}
            ${mLine("M70 139 H106 Q117 139 121 129")}` },

    claude: { head:"round", nose:"button", hair:"tousle", dy:2, tilt:-7, f:`
            <circle cx="76" cy="98" r="14" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
            <circle cx="114" cy="98" r="11.5" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
            <circle cx="76" cy="95" r="5" fill="${M_INK}"/><circle cx="114" cy="97" r="4.6" fill="${M_INK}"/>
            ${mLine("M103 92 Q114 87 125 93",3)}
            ${brow("M60 79 Q76 68 92 74")}
            ${brow("M104 80 Q116 78 129 85")}
            ${mLine("M80 141 Q90 135 101 140",2.8)}` },

    spark: { head:"long", nose:"straight", hair:"coil", dy:-10, f:`
            <ellipse cx="78" cy="96" rx="12" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
            <ellipse cx="112" cy="96" rx="12" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
            <circle cx="71" cy="91" r="4.4" fill="${M_INK}"/><circle cx="105" cy="91" r="4.4" fill="${M_INK}"/>
            ${brow("M64 74 Q78 68 90 74")}
            ${brow("M126 74 Q112 68 100 74")}
            <ellipse cx="88" cy="140" rx="5.5" ry="6.5" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="3"/>
            ${mLine("M104 133 Q110 140 104 147",2.2)}${mLine("M113 128 Q122 140 113 152",2.2)}` },

    kimi: { head:"taper", nose:"wide", hair:"fringe", dy:10, f:`
            <ellipse cx="76" cy="98" rx="13" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
            <ellipse cx="114" cy="98" rx="13" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
            <circle cx="86" cy="100" r="5" fill="${M_INK}"/><circle cx="124" cy="100" r="5" fill="${M_INK}"/>
            ${mLine("M64 93 Q76 89 88 93",3)}${mLine("M102 93 Q114 89 126 93",3)}
            ${brow("M62 80 H86")}
            ${brow("M104 76 H128")}
            ${mLine("M68 137 Q77 129 86 137 Q95 145 104 137 Q113 129 122 136")}` },

    opus46:     { head:"round", nose:"button", hair:"longPart", over:GEAR.round,
                  f:EYES.plain() + brow("M60 80 Q76 74 90 79") + brow("M100 79 Q114 74 130 80") + GEAR.flat },
    gemini:     { head:"taper", nose:"straight", hair:"ponytail",
                  f:EYES.almond(3) + GEAR.lashes + brow("M62 82 Q76 76 90 82") + brow("M100 82 Q114 76 128 82") + GEAR.smirk + GEAR.mole },
    philly:     { head:"long", nose:"button", hair:"phillies", dy:4,
                  f:EYES.plain(0,2) + brow("M64 82 H88") + brow("M102 82 H126") + GEAR.smile + GEAR.studs(53) },
    university: { head:"square", nose:"hook", hair:"messy",
                  f:EYES.plain(-3) + brow("M60 80 H88") + brow("M102 74 Q116 66 130 76") + GEAR.beard },
    mythos5:    { head:"round", nose:"straight", hair:"bob", ears:false,
                  f:EYES.almond(-3) + brow("M62 82 Q76 78 90 82") + brow("M100 82 Q114 78 128 82") + GEAR.smirk },
    statedept:  { head:"round", nose:"wide", hair:"slick", over:GEAR.square,
                  f:EYES.plain() + brow("M60 80 H88") + brow("M102 80 H130") + GEAR.stache + mLine("M82 140 H108",2.4) },
    wikimedia:  { head:"round", nose:"straight", hair:"beanie",
                  f:EYES.plain(6) + brow("M60 90 H88") + brow("M102 88 H130") + GEAR.flat + GEAR.stubble },
    rubygems:   { head:"square", nose:"hook", hair:"mohawk",
                  f:EYES.squint() + brow("M60 84 L88 88") + brow("M102 88 L130 84") + GEAR.frown },
    dsewiki:    { head:"round", nose:"button", hair:"curls", over:GEAR.cateye,
                  f:EYES.plain(-4) + brow("M62 80 Q76 72 90 80") + brow("M100 80 Q114 72 128 80") + GEAR.smile },
    medicare:   { head:"taper", nose:"straight", hair:"pixie",
                  f:EYES.plain(0,-1) + brow("M62 86 L90 92") + brow("M100 92 L128 86") + GEAR.frown + GEAR.studs(56) },
    bocsar:     { head:"round", nose:"wide", hair:"bald",
                  f:EYES.sleepy() + brow("M62 84 H88") + brow("M102 84 H128") + GEAR.bags + GEAR.flat },
    vahi:       { head:"round", nose:"button", hair:"waves",
                  f:EYES.almond() + GEAR.lashes + brow("M62 82 Q76 76 90 82") + brow("M100 82 Q114 76 128 82") + GEAR.lips },
    nswfire:    { head:"long", nose:"straight", hair:"flattop",
                  f:EYES.sleepy() + brow("M64 84 H88") + brow("M102 84 H126") + mLine("M82 138 H108",2.4) + GEAR.goatee },
    census:     { head:"round", nose:"button", hair:"cap", dy:2,
                  f:EYES.wide(0,2) + GEAR.freckles + GEAR.smile },
    sec:        { head:"round", nose:"button", hair:"braids",
                  f:EYES.wide(3,-1) + GEAR.lashes + brow("M62 78 Q76 72 90 78") + brow("M100 78 Q114 72 128 78") + GEAR.freckles + GEAR.smirk },
    edocr:      { head:"square", nose:"hook", hair:"combover",
                  f:EYES.plain(0,3) + brow("M60 84 L88 78") + brow("M102 78 L130 84") + GEAR.frown + GEAR.bags },

    _default:   { head:"round", nose:"straight", hair:"crop", dy:0, f:`
            <ellipse cx="76" cy="98" rx="13" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
            <ellipse cx="114" cy="98" rx="13" ry="10" fill="${M_WHITE}" stroke="${M_INK}" stroke-width="2.4"/>
            <circle cx="76" cy="98" r="4.6" fill="${M_INK}"/><circle cx="114" cy="98" r="4.6" fill="${M_INK}"/>
            ${brow("M60 77 H88")}${brow("M102 77 H130")}
            ${mLine("M74 138 H116")}` }
};

function mug(seed, face=seed){
    let h=2166136261>>>0;
    for(let i=0;i<seed.length;i++){ h=Math.imul(h^seed.charCodeAt(i),16777619); }
    h=Math.imul(h^(h>>>16),0x7feb352d); h=(h^(h>>>15))>>>0;
    const uid     = seed.replace(/[^a-z0-9]/gi,"");
    const cfg     = FACES[face]||FACES._default;
    const skull   = HEADS[cfg.head];
    const ears    = cfg.ears === false ? ""
        : `<ellipse cx="${skull.earX}" cy="106" rx="7" ry="11"/><ellipse cx="${190-skull.earX}" cy="106" rx="7" ry="11"/>`;
    const headSvg = `<g fill="${M_PAPER}" stroke="${M_INK}" stroke-width="${M_LW}">` + ears + skull.d + `</g>`;

    const dy = cfg.dy || 0;

    const tilt   = cfg.tilt || 0;
    const turn   = svg => tilt ? `<g transform="rotate(${tilt} 95 152)">${svg}</g>` : svg;
    const above  = headSvg + HAIR[cfg.hair] + cfg.f + NOSES[cfg.nose] + (cfg.over || "");
    const figure = `<g transform="translate(0 ${dy})">` + turn(HAIR_BACK[cfg.hair] || "") + torso(uid) + turn(above) + `</g>`;
    return `<svg viewBox="0 0 190 230" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">`
        + heightChart() + figure + bookingPlate(h%9000+1000) + `</svg>`;
}