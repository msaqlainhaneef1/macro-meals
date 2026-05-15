/**
 * Macro & Meals - Centralized Site Configuration
 * ================================================
 * Change branding, domain, schema, and all site-wide settings here.
 * Every page loads this file first. All branding is driven from this single source.
 */
const SITE_CONFIG = {
  // ── Brand ──────────────────────────────────────────────
  name: "Macro & Meals",
  nameShort: "Macro And Meals",
  nameAbbr: "MM",
  tagline: "Your trusted source for nutrition calculators and health tools. Free, accurate, and easy to use.",
  domain: "macroandmeals.com",
  url: "https://macroandmeals.com",
  email: "contact@macroandmeals.com",
  year: new Date().getFullYear(),

  // ── Schema.org defaults ────────────────────────────────
  schema: {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "Macro & Meals",
    url: "https://macroandmeals.com",
    description: "Free nutrition calculators, restaurant menu analyzers, and health tools.",
    publisher: {
      "@type": "Organization",
      name: "Macro & Meals",
      url: "https://macroandmeals.com"
    }
  },

  // ── Social / OG defaults ───────────────────────────────
  og: {
    site_name: "Macro & Meals",
    type: "website",
    locale: "en_US"
  },

  // ── Footer quick links ─────────────────────────────────
  quickLinks: [
    { text: "Home", href: "/" },
    { text: "About", href: "/about/" },
    { text: "Contact", href: "/contact/" },
    { text: "Privacy Policy", href: "/privacy-policy/" },
    { text: "Terms & Conditions", href: "/terms-conditions/" },
    { text: "Disclaimer", href: "/disclaimer/" }
  ],

  // ── Footer popular calculators ─────────────────────────
  popularCalcs: [
    { text: "BMI Calculator", href: "/bmi-calculator/" },
    { text: "BMR Calculator", href: "/bmr-calculator/" },
    { text: "TDEE Calculator", href: "/tdee-calculator/" },
    { text: "Protein Calculator", href: "/protein-calculator/" },
    { text: "Calorie Deficit Calculator", href: "/calorie-deficit-calculator/" },
    { text: "Keto Macro Calculator", href: "/keto-macro-calculator/" }
  ],

  // ── Footer restaurant calculators ──────────────────────
  restaurantCalcs: [
    { text: "Starbucks", href: "/starbucks-nutrition-calculator/" },
    { text: "Chipotle", href: "/chipotle-nutrition-calculator/" },
    { text: "McDonald's", href: "/mcdonalds-calories-calculator/" },
    { text: "Subway", href: "/subway-nutrition-calculator/" },
    { text: "Five Guys", href: "/five-guys-nutrition-calculator/" },
    { text: "Panda Express", href: "/panda-express-nutrition-calculator/" }
  ]
};

if (typeof module !== 'undefined') module.exports = SITE_CONFIG;
