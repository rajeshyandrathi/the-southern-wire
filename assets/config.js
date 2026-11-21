/* The Southern Wire — site configuration.
   Fill in real IDs here once you have them; everything below is safely
   inert (no scripts load, no errors) until you do.

   GA_MEASUREMENT_ID   — Google Analytics 4. Get one free at analytics.google.com
                          (Admin -> Data Streams -> Web -> copy the "G-XXXXXXX" ID).
   ADSENSE_CLIENT_ID    — Google AdSense. Auto ads: once this is set, the
                          adsbygoogle script loads (after cookie consent) and
                          Google places ads on the page itself — no manual
                          ad-unit slot IDs needed.
   NEWSLETTER_FORM_NAME — Netlify Forms form name used for the newsletter
                          signup box (works out of the box on Netlify, no
                          account needed — submissions show up in your
                          Netlify dashboard under Forms).
*/
window.SW_CONFIG = {
  GTM_CONTAINER_ID: "GTM-N4N2HFHM", // Google Tag Manager container
  GA_MEASUREMENT_ID: "",            // e.g. "G-ABC1234567"
  ADSENSE_CLIENT_ID: "ca-pub-8802336141966708",
  NEWSLETTER_FORM_NAME: "newsletter"
};
