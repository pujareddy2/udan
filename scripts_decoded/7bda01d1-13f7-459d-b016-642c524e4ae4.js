/* global React */
// Local line-icon set for the UDAAN dashboards (Lucide-style, inherits currentColor).
// Kept separate from the DS Icon (which only ships a handful of glyphs).
const UDAAN_ICON_PATHS = {
  award: '<circle cx="12" cy="8" r="5"/><path d="M8.5 12.5 7 21l5-2.6L17 21l-1.5-8.5"/>',
  briefcase: '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M3 12h18"/>',
  star: '<path d="m12 3 2.6 5.6L21 9.4l-4.5 4.2L17.7 21 12 17.4 6.3 21l1.2-7.4L3 9.4l6.4-.8z"/>',
  flask: '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/><path d="M7.5 15h9"/>',
  code: '<path d="m8 9-4 3 4 3M16 9l4 3-4 3M13 6l-2 12"/>',
  sprout: '<path d="M12 21v-8M12 13c0-3 2-5.5 6.5-5.5 0 3.2-2.2 5.5-6.5 5.5zM12 13c0-2.6-1.8-4.8-5.5-4.8 0 2.8 2 4.8 5.5 4.8z"/>',
  shield: '<path d="m12 3 7 3v5c0 4.2-3 7.3-7 9-4-1.7-7-4.8-7-9V6z"/><path d="m9 12 2 2 4-4"/>',
  coin: '<circle cx="12" cy="12" r="8.5"/><path d="M9.5 8.5h5M9.5 11.5h5M10 8.5c2.4 0 2.4 3.4 0 3.4l3.6 3.6"/>',
  bank: '<path d="m3 9 9-5 9 5M5 9.5v8M9.5 9.5v8M14.5 9.5v8M19 9.5v8M3.5 20.5h17"/>',
  chart: '<path d="M4 20.5h17M6 20v-7M11 20V7M16 20v-9M20.5 20v-5"/>',
  building: '<path d="M5 21V5a1 1 0 0 1 1-1h7a1 1 0 0 1 1 1v16M14 21V9.5h4a1 1 0 0 1 1 1V21M3.5 21h17M8 8h2M8 12h2M8 16h2"/>',
  tools: '<path d="M14.5 6.5a4 4 0 0 0-5.3 5.1l-5.6 5.6 2.2 2.2 5.6-5.6a4 4 0 0 0 5.1-5.3l-2.4 2.4-2-2z"/>',
  spark: '<path d="m12 3 1.9 5.6L19.5 10l-5.6 1.4L12 17l-1.9-5.6L4.5 10l5.6-1.4z"/>',
  book: '<path d="M5 4a2 2 0 0 1 2-2h12v16H7a2 2 0 0 0-2 2zM5 4v16M9 6h6"/>',
  bell: '<path d="M6 9a6 6 0 0 1 12 0c0 4.5 1.8 5.5 1.8 5.5H4.2S6 13.5 6 9M10 19.5a2 2 0 0 0 4 0"/>',
  settings: '<path d="M4 7h9M17 7h3M4 12h3M11 12h9M4 17h11M19 17h1"/><circle cx="15" cy="7" r="2.2"/><circle cx="9" cy="12" r="2.2"/><circle cx="17" cy="17" r="2.2"/>',
  message: '<path d="M21 12a8 7 0 0 1-8 7 9 9 0 0 1-3-.5L4.5 20l1.4-3.8A7 7 0 0 1 5 12a8 7 0 0 1 16 0z"/>',
  mic: '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M6 11a6 6 0 0 0 12 0M12 17v3.5M9 20.5h6"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
  arrow: '<path d="M7 17 17 7M9 7h8v8"/>',
  chev: '<path d="m9 6 6 6-6 6"/>',
  check: '<path d="m5 12 4 4 10-10"/>',
  alert: '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>',
};
function UdaanIcon({ name, size = 22, stroke = 1.8, style }) {
  return React.createElement("svg", {
    width: size, height: size, viewBox: "0 0 24 24", fill: "none",
    stroke: "currentColor", strokeWidth: stroke, strokeLinecap: "round",
    strokeLinejoin: "round", style,
    dangerouslySetInnerHTML: { __html: UDAAN_ICON_PATHS[name] || "" },
  });
}
window.UdaanIcon = UdaanIcon;
