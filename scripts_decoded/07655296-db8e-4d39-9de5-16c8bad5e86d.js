/* @ds-bundle: {"format":3,"namespace":"AstraDesignSystem_bf0882","components":[{"name":"Button","sourcePath":"components/actions/Button.jsx"},{"name":"Badge","sourcePath":"components/display/Badge.jsx"},{"name":"GlassCard","sourcePath":"components/display/GlassCard.jsx"},{"name":"StatCard","sourcePath":"components/display/StatCard.jsx"},{"name":"Tag","sourcePath":"components/display/Tag.jsx"},{"name":"Icon","sourcePath":"components/foundation/Icon.jsx"},{"name":"BlurText","sourcePath":"components/motion/BlurText.jsx"},{"name":"FadingVideo","sourcePath":"components/motion/FadingVideo.jsx"},{"name":"NavBar","sourcePath":"components/navigation/NavBar.jsx"}],"sourceHashes":{"components/actions/Button.jsx":"44d5a204ba0a","components/display/Badge.jsx":"583f98cd8c36","components/display/GlassCard.jsx":"1d79c56a51f1","components/display/StatCard.jsx":"908d323c65d4","components/display/Tag.jsx":"4bf54944e32b","components/foundation/Icon.jsx":"df6fde250fad","components/motion/BlurText.jsx":"f38ecb27cd54","components/motion/FadingVideo.jsx":"5043990ce330","components/navigation/NavBar.jsx":"23c910b6acd0","ui_kits/landing/Capabilities.jsx":"0360e0301938","ui_kits/landing/Hero.jsx":"605fa9f2970d"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.AstraDesignSystem_bf0882 = window.AstraDesignSystem_bf0882 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/display/Badge.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Announcement badge — a liquid-glass pill that leads with a solid white
 * chip ("New") followed by a short message. The hero's "Maiden Crewed
 * Voyage to Mars Arrives 2026" pill.
 */
function Badge({
  chip = "New",
  children,
  className = "",
  style = {},
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    className: `liquid-glass ${className}`.trim(),
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: "0.5rem",
      borderRadius: "var(--radius-pill)",
      paddingRight: "0.75rem",
      fontFamily: "var(--font-body)",
      ...style
    }
  }, rest), chip ? /*#__PURE__*/React.createElement("span", {
    style: {
      background: "var(--color-inverse-surface)",
      color: "var(--color-inverse-text)",
      borderRadius: "var(--radius-pill)",
      padding: "0.25rem 0.75rem",
      fontSize: "var(--text-xs)",
      fontWeight: "var(--weight-semibold)"
    }
  }, chip) : null, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: "var(--text-sm)",
      color: "var(--text-body)"
    }
  }, children));
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Badge.jsx", error: String((e && e.message) || e) }); }

// components/display/GlassCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Generic liquid-glass card container — 1.25rem radius, padded.
 * The base surface for capability cards and any glass panel.
 */
function GlassCard({
  children,
  padding = "1.5rem",
  className = "",
  style = {},
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    className: `liquid-glass ${className}`.trim(),
    style: {
      borderRadius: "var(--radius-card)",
      padding,
      color: "var(--text-body)",
      fontFamily: "var(--font-body)",
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { GlassCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/GlassCard.jsx", error: String((e && e.message) || e) }); }

// components/display/Tag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Small liquid-glass pill tag. Used in clusters on capability cards
 * (e.g. "Photo Realism", "Eco-Vibe"). 11px, white/90, never wraps.
 */
function Tag({
  children,
  className = "",
  style = {},
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    className: `liquid-glass ${className}`.trim(),
    style: {
      display: "inline-flex",
      alignItems: "center",
      borderRadius: "var(--radius-pill)",
      padding: "0.25rem 0.75rem",
      fontFamily: "var(--font-body)",
      fontSize: "var(--text-2xs)",
      fontWeight: "var(--weight-regular)",
      color: "var(--text-body)",
      whiteSpace: "nowrap",
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Tag.jsx", error: String((e && e.message) || e) }); }

// components/foundation/Icon.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Astra icon set. Lucide-style line icons (arrow-up-right, play, clock, globe)
 * and Material-style glyphs (image, movie, lightbulb) used inside capability cards.
 * All icons inherit `currentColor`; line icons stroke, glyph icons fill.
 */

const LINE = new Set(["arrow-up-right", "clock", "globe"]);
const FILL = new Set(["play", "image", "movie", "lightbulb"]);
const PATHS = {
  "arrow-up-right": /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("path", {
    d: "M7 17L17 7"
  }), /*#__PURE__*/React.createElement("path", {
    d: "M7 7h10v10"
  })),
  clock: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("circle", {
    cx: "12",
    cy: "12",
    r: "10"
  }), /*#__PURE__*/React.createElement("path", {
    d: "M12 6v6l4 2"
  })),
  globe: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("circle", {
    cx: "12",
    cy: "12",
    r: "10"
  }), /*#__PURE__*/React.createElement("path", {
    d: "M2 12h20"
  }), /*#__PURE__*/React.createElement("path", {
    d: "M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"
  })),
  play: /*#__PURE__*/React.createElement("polygon", {
    points: "6 4 20 12 6 20 6 4"
  }),
  image: /*#__PURE__*/React.createElement("path", {
    d: "M5 21q-.825 0-1.412-.587T3 19V5q0-.825.588-1.412T5 3h14q.825 0 1.413.588T21 5v14q0 .825-.587 1.413T19 21H5Zm1-4h12l-3.75-5-3 4L9 13l-3 4Z"
  }),
  movie: /*#__PURE__*/React.createElement("path", {
    d: "M4 6.47 5.76 10H20v8H4V6.47M22 4h-4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.89-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4Z"
  }),
  lightbulb: /*#__PURE__*/React.createElement("path", {
    d: "M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1Zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7Z"
  })
};
function Icon({
  name,
  size = 24,
  strokeWidth = 2,
  className = "",
  style = {},
  ...rest
}) {
  const path = PATHS[name];
  if (!path) return null;
  const isLine = LINE.has(name);
  const shared = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    className,
    style,
    "aria-hidden": "true",
    ...rest
  };
  if (isLine) {
    return /*#__PURE__*/React.createElement("svg", _extends({}, shared, {
      fill: "none",
      stroke: "currentColor",
      strokeWidth: strokeWidth,
      strokeLinecap: "round",
      strokeLinejoin: "round"
    }), path);
  }
  return /*#__PURE__*/React.createElement("svg", _extends({}, shared, {
    fill: "currentColor",
    stroke: "none"
  }), path);
}
Object.assign(__ds_scope, { Icon });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/foundation/Icon.jsx", error: String((e && e.message) || e) }); }

// components/actions/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Astra button. Three treatments seen across the brand:
 *  - "white"  solid white pill, black text (top-right nav CTA, "Claim a Spot")
 *  - "glass"  heavy liquid-glass pill, white text (primary hero CTA, "Start Your Voyage")
 *  - "ghost"  bare text link, white text (secondary, "View Liftoff")
 * Everything is a pill. Icons inherit text color.
 */
function Button({
  children,
  variant = "glass",
  icon,
  iconPosition = "right",
  size = "md",
  href,
  disabled = false,
  className = "",
  style = {},
  ...rest
}) {
  const pad = size === "sm" ? {
    padding: "0.5rem 0.75rem",
    fontSize: "var(--text-sm)"
  } : size === "lg" ? {
    padding: "0.75rem 1.5rem",
    fontSize: "var(--text-base)"
  } : {
    padding: "0.625rem 1.25rem",
    fontSize: "var(--text-sm)"
  };
  const base = {
    display: "inline-flex",
    alignItems: "center",
    gap: "0.5rem",
    borderRadius: "var(--radius-pill)",
    fontFamily: "var(--font-body)",
    fontWeight: "var(--weight-medium)",
    lineHeight: 1,
    whiteSpace: "nowrap",
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.5 : 1,
    border: "none",
    textDecoration: "none",
    transition: "opacity 150ms ease, transform 150ms ease",
    ...pad
  };
  let variantStyle = {};
  let glassClass = "";
  if (variant === "white") {
    variantStyle = {
      background: "var(--color-inverse-surface)",
      color: "var(--color-inverse-text)"
    };
  } else if (variant === "glass") {
    glassClass = "liquid-glass-strong";
    variantStyle = {
      color: "var(--text-strong)"
    };
  } else {
    // ghost
    variantStyle = {
      background: "transparent",
      color: "var(--text-strong)",
      padding: size === "sm" ? "0.25rem 0" : "0.375rem 0"
    };
  }
  const iconSize = size === "sm" ? 16 : 20;
  const iconEl = icon ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: iconSize
  }) : null;
  const content = /*#__PURE__*/React.createElement(React.Fragment, null, icon && iconPosition === "left" ? iconEl : null, /*#__PURE__*/React.createElement("span", null, children), icon && iconPosition === "right" ? iconEl : null);
  const Tag = href ? "a" : "button";
  return /*#__PURE__*/React.createElement(Tag, _extends({
    className: `${glassClass} ${className}`.trim(),
    style: {
      ...base,
      ...variantStyle,
      ...style
    },
    href: href,
    disabled: !href ? disabled : undefined,
    onMouseEnter: e => !disabled && (e.currentTarget.style.opacity = 0.85),
    onMouseLeave: e => !disabled && (e.currentTarget.style.opacity = 1)
  }, rest), content);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/actions/Button.jsx", error: String((e && e.message) || e) }); }

// components/display/StatCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Stat card — a fixed-width liquid-glass card with an outline icon on top
 * and a big italic-serif figure with a light label below. Hero stats row.
 */
function StatCard({
  icon,
  value,
  label,
  className = "",
  style = {},
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    className: `liquid-glass ${className}`.trim(),
    style: {
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      width: "220px",
      padding: "1.25rem",
      borderRadius: "var(--radius-card)",
      ...style
    }
  }, rest), icon ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: 28,
    style: {
      color: "var(--text-strong)"
    }
  }) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: "2rem"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: "var(--font-heading)",
      fontStyle: "italic",
      fontSize: "var(--text-stat)",
      lineHeight: "var(--leading-none)",
      letterSpacing: "var(--tracking-tight-1)",
      color: "var(--text-strong)"
    }
  }, value), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: "0.5rem",
      fontFamily: "var(--font-body)",
      fontWeight: "var(--weight-light)",
      fontSize: "var(--text-xs)",
      color: "var(--text-strong)"
    }
  }, label)));
}
Object.assign(__ds_scope, { StatCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/StatCard.jsx", error: String((e && e.message) || e) }); }

// components/motion/BlurText.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Word-by-word blur-in headline. Triggers on 10% visibility via
 * IntersectionObserver, staggers each word by 100ms. Requires Framer Motion
 * on window.Motion; degrades to plain (already-visible) text without it.
 */
function BlurText({
  text = "",
  className = "",
  style = {},
  as = "p",
  ...rest
}) {
  const ref = React.useRef(null);
  const [inView, setInView] = React.useState(false);
  const Motion = typeof window !== "undefined" && window.Motion || null;
  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const reveal = () => setInView(true);

    // If the headline is already within (or above) the viewport at mount,
    // reveal on the next frame — don't wait on the observer.
    requestAnimationFrame(() => {
      const r = el.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > 0) reveal();
    });
    const io = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        reveal();
        io.disconnect();
      }
    }, {
      threshold: 0.1
    });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  const words = text.split(" ");
  const Parent = as;
  const parentStyle = {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "center",
    rowGap: "0.1em",
    margin: 0,
    ...style
  };
  if (!Motion) {
    return /*#__PURE__*/React.createElement(Parent, _extends({
      ref: ref,
      className: className,
      style: parentStyle
    }, rest), words.map((w, i) => /*#__PURE__*/React.createElement("span", {
      key: i,
      style: {
        display: "inline-block",
        marginRight: "0.28em"
      }
    }, w)));
  }
  const M = Motion.motion;
  return /*#__PURE__*/React.createElement(Parent, _extends({
    ref: ref,
    className: className,
    style: parentStyle
  }, rest), words.map((w, i) => /*#__PURE__*/React.createElement(M.span, {
    key: i,
    initial: {
      filter: "blur(10px)",
      opacity: 0,
      y: 50
    },
    animate: inView ? {
      filter: ["blur(10px)", "blur(5px)", "blur(0px)"],
      opacity: [0, 0.5, 1],
      y: [50, -5, 0]
    } : {},
    transition: {
      duration: 0.7,
      times: [0, 0.5, 1],
      ease: "easeOut",
      delay: i * 100 / 1000
    },
    style: {
      display: "inline-block",
      marginRight: "0.28em"
    }
  }, w)));
}
Object.assign(__ds_scope, { BlurText });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/motion/BlurText.jsx", error: String((e && e.message) || e) }); }

// components/motion/FadingVideo.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const FADE_MS = 500;
const FADE_OUT_LEAD = 0.55; // seconds before `ended` to begin fade-out

/**
 * Looping background video with a JS-driven (rAF) crossfade — no CSS
 * transitions. Starts at opacity 0, fades in on loadeddata, fades out in
 * the last 0.55s, then resets and fades back in. Looping is manual.
 */
function FadingVideo({
  src,
  className = "",
  style = {},
  ...rest
}) {
  const videoRef = React.useRef(null);
  const rafRef = React.useRef(null);
  const fadingOutRef = React.useRef(false);
  React.useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    const fadeTo = (target, duration = FADE_MS) => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      const start = parseFloat(video.style.opacity || "0");
      const delta = target - start;
      const t0 = performance.now();
      const step = now => {
        const p = Math.min((now - t0) / duration, 1);
        video.style.opacity = String(start + delta * p);
        if (p < 1) rafRef.current = requestAnimationFrame(step);
      };
      rafRef.current = requestAnimationFrame(step);
    };
    const onLoadedData = () => {
      video.style.opacity = "0";
      video.play().catch(() => {});
      fadeTo(1);
    };
    const onTimeUpdate = () => {
      const remaining = video.duration - video.currentTime;
      if (!fadingOutRef.current && remaining <= FADE_OUT_LEAD && remaining > 0) {
        fadingOutRef.current = true;
        fadeTo(0);
      }
    };
    const onEnded = () => {
      video.style.opacity = "0";
      setTimeout(() => {
        video.currentTime = 0;
        video.play().catch(() => {});
        fadingOutRef.current = false;
        fadeTo(1);
      }, 100);
    };
    video.addEventListener("loadeddata", onLoadedData);
    video.addEventListener("timeupdate", onTimeUpdate);
    video.addEventListener("ended", onEnded);
    if (video.readyState >= 2) onLoadedData();
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      video.removeEventListener("loadeddata", onLoadedData);
      video.removeEventListener("timeupdate", onTimeUpdate);
      video.removeEventListener("ended", onEnded);
    };
  }, [src]);
  return /*#__PURE__*/React.createElement("video", _extends({
    ref: videoRef,
    src: src,
    autoPlay: true,
    muted: true,
    playsInline: true,
    preload: "auto",
    className: className,
    style: {
      opacity: 0,
      ...style
    }
  }, rest));
}
Object.assign(__ds_scope, { FadingVideo });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/motion/FadingVideo.jsx", error: String((e && e.message) || e) }); }

// components/navigation/NavBar.jsx
try { (() => {
const DEFAULT_LINKS = ["Home", "Voyages", "Worlds", "Innovation", "Plan Launch"];

/**
 * Astra top navigation. A 48px glass logo circle (lowercase italic serif "a"),
 * a centered glass pill of links + a white CTA button (desktop), and a
 * balancing spacer on the right. Fixed near the top of the viewport.
 */
function NavBar({
  links = DEFAULT_LINKS,
  ctaLabel = "Claim a Spot",
  logo = "a",
  onCta,
  fixed = true,
  className = "",
  style = {}
}) {
  return /*#__PURE__*/React.createElement("nav", {
    className: className,
    style: {
      position: fixed ? "fixed" : "relative",
      top: fixed ? "1rem" : undefined,
      left: 0,
      right: 0,
      zIndex: 50,
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 2rem",
      fontFamily: "var(--font-body)",
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "liquid-glass",
    style: {
      width: 48,
      height: 48,
      borderRadius: "var(--radius-pill)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      flex: "0 0 auto"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-heading)",
      fontStyle: "italic",
      fontSize: "1.75rem",
      color: "var(--text-strong)",
      lineHeight: 1
    }
  }, logo)), /*#__PURE__*/React.createElement("div", {
    className: "liquid-glass",
    style: {
      display: "flex",
      alignItems: "center",
      gap: "0.25rem",
      padding: "0.375rem",
      borderRadius: "var(--radius-pill)"
    }
  }, links.map(l => /*#__PURE__*/React.createElement("a", {
    key: l,
    href: "#",
    style: {
      padding: "0.5rem 0.75rem",
      fontSize: "var(--text-sm)",
      fontWeight: "var(--weight-medium)",
      color: "var(--text-body)",
      textDecoration: "none",
      whiteSpace: "nowrap"
    }
  }, l)), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "white",
    size: "sm",
    icon: "arrow-up-right",
    onClick: onCta
  }, ctaLabel)), /*#__PURE__*/React.createElement("div", {
    style: {
      width: 48,
      height: 48,
      flex: "0 0 auto"
    },
    "aria-hidden": "true"
  }));
}
Object.assign(__ds_scope, { NavBar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/NavBar.jsx", error: String((e && e.message) || e) }); }

// ui_kits/landing/Capabilities.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
// Astra landing — Capabilities section. Three liquid-glass cards over a
// full-bleed crossfading video. Inline-styled layout (no Tailwind dependency).

const CAPABILITIES = [{
  icon: "image",
  title: "AI Scenery",
  tags: ["Natural Context", "Photo Realism", "Infinite Settings", "Eco-Vibe"],
  body: "AI analyzes your product to create indistinguishable natural environments — from Icelandic cliffs to misty forests."
}, {
  icon: "movie",
  title: "Batch Production",
  tags: ["Scale Fast", "Visual Consistency", "Time Saver", "Ready to Post"],
  body: "Style your entire product line in minutes. Create a unified visual identity for catalogues and social media without weeks of retouching."
}, {
  icon: "lightbulb",
  title: "Smart Lighting",
  tags: ["Ray Tracing", "Physical Shadows", "Studio Quality", "Sunlight Sync"],
  body: "Automatic lighting and material adjustment. Achieve flawless integration with realistic shadows and sunlight."
}];
function CapabilityCard({
  icon,
  title,
  tags,
  body
}) {
  const {
    Tag: CapTag,
    Icon: CapIcon
  } = window.AstraDesignSystem_bf0882;
  return /*#__PURE__*/React.createElement("div", {
    className: "liquid-glass",
    style: {
      display: "flex",
      flexDirection: "column",
      padding: "1.5rem",
      borderRadius: "1.25rem",
      minHeight: "360px"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "space-between",
      gap: "1rem"
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "liquid-glass",
    style: {
      width: 44,
      height: 44,
      borderRadius: "0.75rem",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      flex: "0 0 auto"
    }
  }, /*#__PURE__*/React.createElement(CapIcon, {
    name: icon,
    size: 24,
    style: {
      color: "#fff"
    }
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "flex-end",
      gap: "0.375rem",
      maxWidth: "70%"
    }
  }, tags.map(t => /*#__PURE__*/React.createElement(CapTag, {
    key: t
  }, t)))), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: "1.5rem"
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      fontFamily: "var(--font-heading)",
      fontStyle: "italic",
      color: "#fff",
      fontSize: "clamp(1.875rem, 3vw, 2.25rem)",
      lineHeight: 1,
      letterSpacing: "-1px"
    }
  }, title), /*#__PURE__*/React.createElement("p", {
    style: {
      marginTop: "0.75rem",
      fontSize: "0.875rem",
      fontWeight: 300,
      lineHeight: 1.375,
      color: "rgba(255,255,255,0.9)",
      fontFamily: "var(--font-body)",
      maxWidth: "32ch"
    }
  }, body)));
}
function CapabilitiesSection() {
  const {
    FadingVideo: CapVideo
  } = window.AstraDesignSystem_bf0882;
  return /*#__PURE__*/React.createElement("section", {
    style: {
      position: "relative",
      display: "flex",
      flexDirection: "column",
      minHeight: "100vh",
      background: "#000"
    }
  }, /*#__PURE__*/React.createElement(CapVideo, {
    src: "../../uploads/People_working_together_at_table_202606112330.mp4",
    style: {
      position: "absolute",
      inset: 0,
      width: "100%",
      height: "100%",
      objectFit: "cover",
      zIndex: 0
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "relative",
      zIndex: 10,
      display: "flex",
      flexDirection: "column",
      minHeight: "100vh",
      padding: "6rem clamp(2rem, 5vw, 5rem) 2.5rem"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: "auto"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: "1.5rem",
      fontSize: "0.875rem",
      color: "rgba(255,255,255,0.8)",
      fontFamily: "var(--font-body)"
    }
  }, "// Capabilities"), /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      fontFamily: "var(--font-heading)",
      fontStyle: "italic",
      color: "#fff",
      fontSize: "clamp(3rem, 7vw, 6rem)",
      lineHeight: 0.9,
      letterSpacing: "-3px"
    }
  }, "Production", /*#__PURE__*/React.createElement("br", null), "evolved")), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: "4rem",
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
      gap: "1.5rem"
    }
  }, CAPABILITIES.map(c => /*#__PURE__*/React.createElement(CapabilityCard, _extends({
    key: c.title
  }, c))))));
}
window.CapabilitiesSection = CapabilitiesSection;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/landing/Capabilities.jsx", error: String((e && e.message) || e) }); }

// ui_kits/landing/Hero.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
// Astra landing — Hero section. Composes design-system components over a
// full-bleed crossfading video. Framer Motion entrance animations.
// Layout is inline-styled (no Tailwind dependency) so it renders anywhere.

function HeroSection() {
  const {
    Badge,
    StatCard,
    Button,
    BlurText,
    FadingVideo,
    NavBar
  } = window.AstraDesignSystem_bf0882;
  const M = window.Motion.motion;
  const rise = delay => ({
    initial: {
      filter: "blur(10px)",
      opacity: 0,
      y: 20
    },
    animate: {
      filter: "blur(0px)",
      opacity: 1,
      y: 0
    },
    transition: {
      duration: 0.8,
      ease: "easeOut",
      delay
    }
  });
  return /*#__PURE__*/React.createElement("section", {
    style: {
      position: "relative",
      height: "100vh",
      width: "100%",
      overflow: "hidden",
      background: "#000"
    }
  }, /*#__PURE__*/React.createElement(FadingVideo, {
    src: "../../uploads/Students_walking_on_campus_path_202606112311.mp4",
    style: {
      position: "absolute",
      left: "50%",
      top: 0,
      transform: "translateX(-50%)",
      width: "120%",
      height: "120%",
      objectFit: "cover",
      objectPosition: "top",
      zIndex: 0
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "relative",
      zIndex: 10,
      display: "flex",
      flexDirection: "column",
      height: "100%"
    }
  }, /*#__PURE__*/React.createElement(NavBar, null), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "6rem 1rem 0",
      textAlign: "center",
      minHeight: 0
    }
  }, /*#__PURE__*/React.createElement(M.div, rise(0.4), /*#__PURE__*/React.createElement(Badge, {
    chip: "New"
  }, "Maiden Crewed Voyage to Mars Arrives 2026")), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: "1.5rem"
    }
  }, /*#__PURE__*/React.createElement(BlurText, {
    text: "Venture Past Our Sky Across the Universe",
    style: {
      fontFamily: "var(--font-heading)",
      fontStyle: "italic",
      color: "#fff",
      fontSize: "clamp(3rem, 7vw, 5.5rem)",
      lineHeight: 0.8,
      letterSpacing: "-4px",
      maxWidth: "42rem"
    }
  })), /*#__PURE__*/React.createElement(M.p, _extends({}, rise(0.8), {
    style: {
      marginTop: "1rem",
      maxWidth: "42rem",
      fontSize: "clamp(0.875rem, 1.4vw, 1rem)",
      fontWeight: 300,
      lineHeight: 1.25,
      color: "#fff",
      fontFamily: "var(--font-body)"
    }
  }), "Discover the universe in ways once unimaginable. Our pioneering vessels and breakthrough engineering bring deep-space exploration within reach\u2014secure and extraordinary."), /*#__PURE__*/React.createElement(M.div, _extends({}, rise(1.1), {
    style: {
      marginTop: "1.5rem",
      display: "flex",
      alignItems: "center",
      gap: "1.5rem"
    }
  }), /*#__PURE__*/React.createElement(Button, {
    variant: "glass",
    icon: "arrow-up-right"
  }, "Start Your Voyage"), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    icon: "play",
    iconPosition: "left"
  }, "View Liftoff")), /*#__PURE__*/React.createElement(M.div, _extends({}, rise(1.3), {
    style: {
      marginTop: "2rem",
      display: "flex",
      alignItems: "stretch",
      gap: "1rem"
    }
  }), /*#__PURE__*/React.createElement(StatCard, {
    icon: "clock",
    value: "34.5 Min",
    label: "Average Videos Watch Time"
  }), /*#__PURE__*/React.createElement(StatCard, {
    icon: "globe",
    value: "2.8B+",
    label: "Users Across the Globe"
  }))), /*#__PURE__*/React.createElement(M.div, _extends({}, rise(1.4), {
    style: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: "1rem",
      paddingBottom: "2rem"
    }
  }), /*#__PURE__*/React.createElement("span", {
    className: "liquid-glass",
    style: {
      borderRadius: "9999px",
      padding: "0.25rem 0.875rem",
      fontSize: "0.75rem",
      fontWeight: 500,
      color: "#fff",
      fontFamily: "var(--font-body)"
    }
  }, "Collaborating with top aerospace pioneers globally"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: "clamp(2rem, 5vw, 4rem)",
      fontFamily: "var(--font-heading)",
      fontStyle: "italic",
      letterSpacing: "-0.5px"
    }
  }, ["Aeon", "Vela", "Apex", "Orbit", "Zeno"].map(p => /*#__PURE__*/React.createElement("span", {
    key: p,
    style: {
      fontSize: "clamp(1.5rem, 3vw, 1.875rem)",
      color: "#fff"
    }
  }, p))))));
}
window.HeroSection = HeroSection;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/landing/Hero.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.GlassCard = __ds_scope.GlassCard;

__ds_ns.StatCard = __ds_scope.StatCard;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.Icon = __ds_scope.Icon;

__ds_ns.BlurText = __ds_scope.BlurText;

__ds_ns.FadingVideo = __ds_scope.FadingVideo;

__ds_ns.NavBar = __ds_scope.NavBar;

})();
