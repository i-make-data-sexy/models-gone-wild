/* ========================================================================
     About This File
   ======================================================================== */

/* The site header's mobile menu, loaded by both pages. The MENU label
   toggles a hidden checkbox, and one change listener shows or hides the
   menu and keeps aria-expanded in step. A click handler on .menu-toggle
   breaks the menu on iPhone, so the checkbox is the whole mechanism. */



/* ========================================================================
     Site Header Mobile Menu
   ======================================================================== */

(function(){
    const checkbox = document.getElementById('menu-toggle-checkbox');
    const menu     = document.querySelector('.nav-primary .menu');
    const toggle   = document.querySelector('.menu-toggle');
    if(!checkbox || !menu) return;
    checkbox.addEventListener('change', function(){
        if(this.checked) menu.classList.add('visible');
        else menu.classList.remove('visible');
        if(toggle) toggle.setAttribute('aria-expanded', this.checked ? 'true' : 'false');
    });
})();