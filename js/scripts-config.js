/**
 * Macro & Meals - External Scripts Configuration
 * ================================================
 * Paste your analytics, AdSense, and any other third-party script
 * snippets here. They will be injected into every page automatically.
 *
 * HOW TO USE:
 *   1. Add your script snippet as a string to the EXTERNAL_SCRIPTS array.
 *   2. Each entry will be injected into the <head> of every page.
 *   3. For body-level scripts, add them to EXTERNAL_BODY_SCRIPTS.
 */

const EXTERNAL_SCRIPTS = [
  // ── Google Analytics (GA4) ─────────────────────────────
  // Uncomment and replace G-XXXXXXXXXX with your Measurement ID
  // `<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
  //  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-XXXXXXXXXX');</script>`,

  // ── Google AdSense ─────────────────────────────────────
  // Uncomment and replace ca-pub-XXXXXXXXXXXXXXXX with your publisher ID
  // `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>`,

  // ── Google Tag Manager ─────────────────────────────────
  // Uncomment and replace GTM-XXXXXX with your container ID
  // `<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-XXXXXX');</script>`,

  // ── Microsoft Clarity ──────────────────────────────────
  // Uncomment and replace YOUR_CLARITY_ID
  // `<script type="text/javascript">(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script","YOUR_CLARITY_ID");</script>`,

  // ── Facebook Pixel ─────────────────────────────────────
  // Uncomment and replace YOUR_PIXEL_ID
  // `<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','YOUR_PIXEL_ID');fbq('track','PageView');</script>`,
];

const EXTERNAL_BODY_SCRIPTS = [
  // ── Google Tag Manager (noscript) ──────────────────────
  // Uncomment and replace GTM-XXXXXX with your container ID
  // `<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXX" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>`,
];

(function injectExternalScripts() {
  EXTERNAL_SCRIPTS.forEach(function(snippet) {
    if (!snippet || snippet.trim().startsWith('//')) return;
    var temp = document.createElement('div');
    temp.innerHTML = snippet;
    Array.from(temp.children).forEach(function(el) {
      document.head.appendChild(el.cloneNode(true));
    });
  });
  EXTERNAL_BODY_SCRIPTS.forEach(function(snippet) {
    if (!snippet || snippet.trim().startsWith('//')) return;
    var temp = document.createElement('div');
    temp.innerHTML = snippet;
    Array.from(temp.children).forEach(function(el) {
      document.body.insertBefore(el.cloneNode(true), document.body.firstChild);
    });
  });
})();
