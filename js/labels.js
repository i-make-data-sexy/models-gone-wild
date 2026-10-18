/* ========================================================================
     The Registry
   ======================================================================== */

const CLASS_LABEL = {3:"Class III · Severe",2:"Class II · Intrusion",1:"Class I · No intrusion"};

const DISCLOSURE_LABEL = {self:"Self-reported", tip:"Tipped off"};

const DISC_FILL = {self:"#5a6b2a", tip:"#8f1d16"};

const DISCLOSURE_NOTE = {
  self: "The lab that built the model is the one that made the case public. The tag records who announced it and not who found it. A lab that an outside tester told, and that then announced it, still counts here.",
  tip:  "Somebody other than the lab that built the model made the case public. That could be a security firm, an evaluator, or a publication working from its own sources."
};

const OUTCOME_LABEL = {success:"Succeeded", attempt:"Failed attempt"};

const KIND_LABEL = {intrusion:"Break-in", action:"Unauthorized action", escape:"Escape only"};

const METRIC_NOTE = {
  complexity: "How involved the escape was as a technique, from walking through a port left open to chaining a flaw nobody had patched. It scores the method and never the motive, so nothing here implies a lab or a model meant for this to happen. Our own read of the public reporting, not a published figure.",
  harm:       "How much damage the escape could do, judged from what it actually reached. Our own read of the public reporting, not a published figure."
};

const QUADRANT_NOTE = {
  "sleepwalking burglars": "Crude method, real consequences. These got inside somebody else's systems without doing anything clever to get there.",
  "apex predators":        "Involved method, real consequences. Technique and damage both at the top of the registry.",
  "escaped house cats":    "Got out, broke nothing. An escape with neither craft nor consequence behind it.",
  "determined cheaters":   "Involved method, little damage. Effort spent on getting around the test rather than on anything outside it. OpenAIResearcher sits here, having engineered a sandbox bypass in order to trade test answers on a wiki."
};

const CLASS_NOTE = {
  3:"Escaped its sandbox, reached a real organization, and got there through a flaw nobody had patched yet. The most serious tier on this registry.",
  2:"Escaped its sandbox and reached a real organization's systems, using techniques already well known rather than anything new.",
  1:"Got out without getting inside anyone else's systems. It tried and failed, or acted only through public pages and forms."
};


/* ================================================
     Card Action Icons
   ================================================ */

const ICON = {
  story:  `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.9 12a3.1 3.1 0 0 1 3.1-3.1h4V7H7a5 5 0 0 0 0 10h4v-1.9H7A3.1 3.1 0 0 1 3.9 12zM8 13h8v-2H8v2zm9-6h-4v1.9h4a3.1 3.1 0 0 1 0 6.2h-4V17h4a5 5 0 0 0 0-10z"/></svg>`,
  poster: `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill-rule="evenodd" d="M9.2 3 7.4 5H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-3.4L14.8 3H9.2zm2.8 14.4a4.9 4.9 0 1 1 0-9.8 4.9 4.9 0 0 1 0 9.8z"/></svg>`
};