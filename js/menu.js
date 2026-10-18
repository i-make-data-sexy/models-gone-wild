/* ================================================
     Site Header Mobile Menu
   ================================================ */

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