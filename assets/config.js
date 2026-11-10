/* The Southern Wire — site configuration.
   Fill in real IDs here once you have them; everything below is safely
   inert (no scripts load, no errors) until you do.

   GA_MEASUREMENT_ID   — Google Analytics 4. Get one free at analytics.google.com
                          (Admin -> Data Streams -> Web -> copy the "G-XXXXXXX" ID).
   ADSENSE_CLIENT_ID    — Google AdSense. Get one at adsense.google.com by adding
                          this site; Google reviews it before ads actually serve
                          (usually wants real traffic + the legal pages already
                          on this site: Privacy, Terms, About, Contact).
   ADSENSE_SLOT_TOP     — Ad unit "slot" ID for the top banner placement.
   ADSENSE_SLOT_INARTICLE — Ad unit "slot" ID for the in-article placement.
   NEWSLETTER_FORM_NAME — Netlify Forms form name used for the newsletter
                          signup box (works out of the box on Netlify, no
                          account needed — submissions show up in your
                          Netlify dashboard under Forms).
*/
window.SW_CONFIG = {
  GA_MEASUREMENT_ID: "",            // e.g. "G-ABC1234567"
  ADSENSE_CLIENT_ID: "",            // e.g. "ca-pub-1234567890123456"
  ADSENSE_SLOT_TOP: "",             // e.g. "1234567890"
  ADSENSE_SLOT_INARTICLE: "",       // e.g. "0987654321"
  NEWSLETTER_FORM_NAME: "newsletter"
};
