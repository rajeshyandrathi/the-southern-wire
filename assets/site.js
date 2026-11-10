/* The Southern Wire — shared site behavior.
   Loaded on every page. Every feature degrades gracefully: if config IDs
   are blank, or an expected element isn't on the page, that feature just
   does nothing — nothing here can break a page that doesn't use it. */
(function(){
  "use strict";
  var CFG = window.SW_CONFIG || {};

  // ---- figure out how deep we are, so relative asset/page links work ----
  var path = window.location.pathname;
  var inSubdir = /\/(posts|archive)\//.test(path);
  var base = inSubdir ? "../" : "";

  function qs(sel, root){ return (root||document).querySelector(sel); }
  function qsa(sel, root){ return Array.prototype.slice.call((root||document).querySelectorAll(sel)); }
  function el(tag, attrs, html){
    var e = document.createElement(tag);
    for (var k in (attrs||{})) e.setAttribute(k, attrs[k]);
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  // ================= COOKIE CONSENT =================
  var CONSENT_KEY = "sw_consent";
  function getConsent(){ try { return localStorage.getItem(CONSENT_KEY); } catch(e){ return null; } }
  function setConsent(v){ try { localStorage.setItem(CONSENT_KEY, v); } catch(e){} }

  function loadAnalyticsAndAds(){
    if (CFG.GA_MEASUREMENT_ID){
      var s1 = el("script", {async:"", src:"https://www.googletagmanager.com/gtag/js?id=" + CFG.GA_MEASUREMENT_ID});
      document.head.appendChild(s1);
      window.dataLayer = window.dataLayer || [];
      function gtag(){ window.dataLayer.push(arguments); }
      gtag("js", new Date());
      gtag("config", CFG.GA_MEASUREMENT_ID);
    }
    if (CFG.ADSENSE_CLIENT_ID){
      var s2 = el("script", {
        async:"",
        src:"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + CFG.ADSENSE_CLIENT_ID,
        crossorigin:"anonymous"
      });
      document.head.appendChild(s2);
      renderAdSlots();
    }
  }

  function renderAdSlots(){
    if (!CFG.ADSENSE_CLIENT_ID) return;
    qsa(".sw-adslot[data-slot]").forEach(function(slot){
      if (slot.getAttribute("data-live") === "1") return;
      slot.setAttribute("data-live", "1");
      slot.innerHTML = "";
      var ins = el("ins", {
        "class":"adsbygoogle",
        style:"display:block",
        "data-ad-client": CFG.ADSENSE_CLIENT_ID,
        "data-ad-slot": slot.getAttribute("data-slot"),
        "data-ad-format":"auto",
        "data-full-width-responsive":"true"
      });
      slot.appendChild(ins);
      try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch(e){}
    });
  }

  function initCookieBanner(){
    var consent = getConsent();
    if (consent === "accepted"){ loadAnalyticsAndAds(); return; }
    if (consent === "declined") return;

    var bar = el("div", {"class":"sw-cookie", role:"dialog", "aria-label":"Cookie notice"},
      '<p>We use cookies for basic analytics and, once ads are enabled, to show relevant ads. See our ' +
      '<a href="' + base + 'privacy.html">Privacy Policy</a>.</p>' +
      '<div class="sw-cookie-actions">' +
        '<button type="button" class="sw-cookie-decline">Decline</button>' +
        '<button type="button" class="sw-cookie-accept">Accept</button>' +
      '</div>');
    document.body.appendChild(bar);
    qs(".sw-cookie-accept", bar).addEventListener("click", function(){
      setConsent("accepted"); bar.remove(); loadAnalyticsAndAds();
    });
    qs(".sw-cookie-decline", bar).addEventListener("click", function(){
      setConsent("declined"); bar.remove();
    });
  }

  // ================= AD SLOT PLACEMENT =================
  function insertAdSlots(){
    // Top banner: right after the desk nav, on index/category/archive pages.
    var nav = qs("nav.deskrow");
    if (nav && !qs(".sw-adslot-top")){
      var top = el("div", {"class":"sw-adslot sw-adslot-top", "data-slot": CFG.ADSENSE_SLOT_TOP || ""},
        '<span class="sw-ad-label">Advertisement</span>');
      // On category pages the nav sits inside <header>; on the homepage it's
      // a standalone sibling. Either way, anchor off whichever is bigger.
      var anchor = nav.closest("header") || nav;
      anchor.insertAdjacentElement("afterend", top);
    }
    // In-article: after the 2nd paragraph of the main article on post pages.
    var article = qs("article");
    if (article && !qs(".sw-adslot-inarticle")){
      var paras = qsa("p", article);
      if (paras.length >= 2){
        var mid = el("div", {"class":"sw-adslot sw-adslot-inarticle", "data-slot": CFG.ADSENSE_SLOT_INARTICLE || ""},
          '<span class="sw-ad-label">Advertisement</span>');
        paras[1].insertAdjacentElement("afterend", mid);
      }
    }
  }

  // ================= LEGAL LINKS IN FOOTER =================
  function insertLegalLinks(){
    var footer = qs("footer");
    if (!footer || qs(".sw-legal-links", footer)) return;
    var links = el("p", {"class":"sw-legal-links"},
      '<a href="' + base + 'about.html">About</a>' +
      '<a href="' + base + 'privacy.html">Privacy</a>' +
      '<a href="' + base + 'terms.html">Terms</a>' +
      '<a href="' + base + 'contact.html">Contact</a>');
    footer.appendChild(links);
  }

  // ================= SHARE BAR =================
  function insertShareBar(){
    var article = qs("main article");
    if (!article || qs(".sw-share")) return;
    var h1 = qs("h1");
    var title = h1 ? h1.textContent.trim() : document.title;
    var url = window.location.href;
    var bar = el("div", {"class":"sw-share"},
      '<span class="sw-share-label">Share</span>' +
      '<a target="_blank" rel="noopener" href="https://twitter.com/intent/tweet?text=' + encodeURIComponent(title) + '&url=' + encodeURIComponent(url) + '">X / Twitter</a>' +
      '<a target="_blank" rel="noopener" href="https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url) + '">Facebook</a>' +
      '<a target="_blank" rel="noopener" href="https://wa.me/?text=' + encodeURIComponent(title + " " + url) + '">WhatsApp</a>' +
      '<a target="_blank" rel="noopener" href="https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(url) + '">LinkedIn</a>' +
      '<button type="button" class="sw-copy-link">Copy link</button>');
    article.insertAdjacentElement("afterend", bar);
    qs(".sw-copy-link", bar).addEventListener("click", function(btn){
      navigator.clipboard && navigator.clipboard.writeText(url).then(function(){
        var b = qs(".sw-copy-link", bar);
        var old = b.textContent; b.textContent = "Copied!";
        setTimeout(function(){ b.textContent = old; }, 1800);
      });
    });
  }

  // ================= RELATED POSTS =================
  function insertRelatedPosts(){
    var article = qs("main article");
    if (!article || qs(".sw-related")) return;
    var tagEl = qs(".tag");
    var category = tagEl ? tagEl.textContent.trim() : null;
    if (!category) return;
    fetch(base + "search-index.json").then(function(r){ return r.json(); }).then(function(items){
      var here = window.location.pathname.split("/").pop();
      var matches = items.filter(function(it){
        return it.category === category && it.url.indexOf(here) === -1;
      });
      // shuffle, take 3
      for (var i = matches.length - 1; i > 0; i--){
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = matches[i]; matches[i] = matches[j]; matches[j] = tmp;
      }
      matches = matches.slice(0, 3);
      if (!matches.length) return;
      var list = matches.map(function(it){
        return '<li><a href="' + base + it.url + '">' + it.title + '</a></li>';
      }).join("");
      var box = el("div", {"class":"sw-related"},
        '<h3>More from ' + category + '</h3><ul>' + list + "</ul>");
      var shareBar = qs(".sw-share");
      (shareBar || article).insertAdjacentElement("afterend", box);
    }).catch(function(){ /* search index not reachable; skip silently */ });
  }

  // ================= SEARCH BOX =================
  function insertSearch(){
    var nav = qs("nav.deskrow");
    if (!nav || qs(".sw-search")) return;
    var wrap = el("div", {"class":"wrap"});
    var box = el("div", {"class":"sw-search"},
      '<input type="search" placeholder="Search The Southern Wire…" aria-label="Search">' +
      '<div class="sw-search-results"></div>');
    wrap.appendChild(box);
    var anchor = nav.closest("header") || nav;
    anchor.insertAdjacentElement("afterend", wrap);

    var input = qs("input", box);
    var results = qs(".sw-search-results", box);
    var indexPromise = fetch(base + "search-index.json").then(function(r){ return r.json(); }).catch(function(){ return []; });

    input.addEventListener("input", function(){
      var q = input.value.trim().toLowerCase();
      if (!q){ results.classList.remove("sw-open"); results.innerHTML = ""; return; }
      indexPromise.then(function(items){
        var matches = items.filter(function(it){
          return it.title.toLowerCase().indexOf(q) !== -1;
        }).slice(0, 10);
        if (!matches.length){
          results.innerHTML = '<div class="sw-search-empty">No stories match &ldquo;' + q + '&rdquo;.</div>';
        } else {
          results.innerHTML = matches.map(function(it){
            return '<a href="' + base + it.url + '"><span class="sw-sr-cat">' + it.category + ' &middot; ' + it.date + '</span>' + it.title + '</a>';
          }).join("");
        }
        results.classList.add("sw-open");
      });
    });
    document.addEventListener("click", function(ev){
      if (!box.contains(ev.target)) results.classList.remove("sw-open");
    });
  }

  // ================= NEWSLETTER (dynamic copy for pages with no static form) =================
  function insertNewsletterIfMissing(){
    if (qs(".sw-newsletter")) return; // already injected (or a hand-placed one exists)
    var footer = qs("footer");
    if (!footer) return;
    var formName = CFG.NEWSLETTER_FORM_NAME || "newsletter";
    var box = el("div", {"class":"sw-newsletter"},
      '<h3>Get tomorrow’s edition in your inbox</h3>' +
      '<p>One email a day, every morning. No spam, unsubscribe any time.</p>' +
      '<form>' +
        '<input type="email" name="email" placeholder="you@example.com" required aria-label="Email address">' +
        '<button type="submit">Subscribe</button>' +
      '</form>' +
      '<p class="sw-nl-msg"></p>');
    footer.insertAdjacentElement("beforebegin", box);
    qs("form", box).addEventListener("submit", function(ev){
      ev.preventDefault();
      var email = qs("input[type=email]", box).value;
      var msg = qs(".sw-nl-msg", box);
      fetch("/", {
        method: "POST",
        headers: {"Content-Type":"application/x-www-form-urlencoded"},
        body: encodeURIComponent("form-name") + "=" + encodeURIComponent(formName) + "&" + encodeURIComponent("email") + "=" + encodeURIComponent(email)
      }).then(function(){
        msg.textContent = "Thanks — you’re subscribed.";
        msg.classList.add("sw-show");
        qs("form", box).reset();
      }).catch(function(){
        msg.textContent = "Something went wrong — please try again later.";
        msg.classList.add("sw-show");
      });
    });
  }

  // ================= RUN =================
  function safe(fn){
    try { fn(); } catch(e){ console.error("[site.js] " + fn.name + " failed:", e); }
  }

  document.addEventListener("DOMContentLoaded", function(){
    safe(insertAdSlots);
    safe(insertLegalLinks);
    safe(insertSearch);
    safe(insertShareBar);
    safe(insertRelatedPosts);
    safe(insertNewsletterIfMissing);
    safe(initCookieBanner);
    if (getConsent() === "accepted") safe(renderAdSlots);
  });
})();
