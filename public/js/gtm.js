/* ========================================================================
     About This File
   ======================================================================== */

/* The Google Tag Manager (GTM) loader, loaded as the first script in the
   head of both pages. It is Google's own snippet with two changes. It
   reads the container ID from the script tag's data-gtm-id attribute, so
   the ID stays in the page beside the noscript fallback that also needs
   it, and it appends the GTM script to the head since no earlier script
   exists to insert it before. Keep it an external file since the Content
   Security Policy forbids inline scripts. */



/* ========================================================================
     Tag Manager Loader
   ======================================================================== */

(function (w, d, containerId) {
    if (!containerId) return;

    w.dataLayer = w.dataLayer || [];
    w.dataLayer.push({ "gtm.start": new Date().getTime(), event: "gtm.js" });

    const tag = d.createElement("script");
    tag.async = true;
    tag.src = "https://www.googletagmanager.com/gtm.js?id=" + containerId;
    d.head.appendChild(tag);
})(window, document, document.currentScript.dataset.gtmId);