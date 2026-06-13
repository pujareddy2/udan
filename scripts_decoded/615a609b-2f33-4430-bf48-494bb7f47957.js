/* global React */
// UDAAN AI — the profile sheet. Two modes:
//   • view  — read-only cards; empty fields read "Not added yet"
//   • edit  — the Profile Builder: every field is an empty input the user fills
// Both render from window.UDAAN_PROFILE_SCHEMA. No demo data anywhere.

const { useState, useMemo } = React;

const MUTED = "rgba(255,255,255,0.55)";
const LABEL = "rgba(255,255,255,0.6)";

function initials(name) {
  if (!name) return "U";
  const parts = name.trim().split(/\s+/).slice(0, 2);
  return parts.map((p) => p[0]).join("").toUpperCase() || "U";
}

const inputStyle = {
  width: "100%", boxSizing: "border-box", background: "rgba(255,255,255,0.07)",
  border: "1px solid rgba(255,255,255,0.2)", borderRadius: "12px", padding: "0.55rem 0.75rem",
  color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.92rem", outline: "none",
  colorScheme: "dark",
};
const fieldLabelStyle = {
  fontFamily: "var(--font-body)", fontSize: "0.7rem", letterSpacing: "0.4px",
  textTransform: "uppercase", color: LABEL, marginBottom: "0.3rem", display: "block",
};

/* ---------- view primitives ---------- */
function Field({ label, value }) {
  const empty = value === undefined || value === null || value === "";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.2rem", minWidth: 0 }}>
      <span style={{ fontFamily: "var(--font-body)", fontSize: "0.7rem", letterSpacing: "0.4px",
        textTransform: "uppercase", color: LABEL }}>{label}</span>
      {empty ? (
        <span style={{ fontFamily: "var(--font-body)", fontSize: "0.82rem", color: MUTED, fontStyle: "italic" }}>Not added yet</span>
      ) : (
        <span style={{ fontFamily: "var(--font-body)", fontSize: "0.95rem", fontWeight: 500, color: "#fff",
          lineHeight: 1.25, overflowWrap: "anywhere" }}>{value}</span>
      )}
    </div>
  );
}

function StatusChip({ label, on, Icon }) {
  return (
    <span className="liquid-glass" style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem",
      borderRadius: "9999px", padding: "0.35rem 0.7rem 0.35rem 0.55rem", fontFamily: "var(--font-body)",
      fontSize: "0.8rem", fontWeight: 500, color: on ? "#fff" : MUTED }}>
      <Icon name={on ? "check" : "alert"} size={14} style={{ color: on ? "#7fe0a0" : "rgba(255,255,255,0.4)" }} />
      {label}
    </span>
  );
}

function PillChip({ label, on }) {
  return (
    <span className={on ? "liquid-glass-strong" : ""} style={{ borderRadius: "9999px",
      padding: "0.35rem 0.85rem", fontFamily: "var(--font-body)", fontSize: "0.8rem",
      fontWeight: on ? 600 : 400, color: on ? "#fff" : "rgba(255,255,255,0.55)",
      border: on ? "none" : "1px solid rgba(255,255,255,0.18)", background: on ? undefined : "transparent" }}>
      {label}
    </span>
  );
}

/* ---------- edit primitives ---------- */
function EditField({ field, value, onChange }) {
  const common = { style: inputStyle, value: value || "", placeholder: "Enter " + field.label.toLowerCase(),
    onChange: (e) => onChange(field.key, e.target.value) };
  return (
    <label style={{ display: "block", minWidth: 0 }}>
      <span style={fieldLabelStyle}>{field.label}</span>
      {field.type === "select" ? (
        <select style={inputStyle} value={value || ""} onChange={(e) => onChange(field.key, e.target.value)}>
          <option value="" style={{ color: "#111" }}>Select</option>
          {field.options.map((o) => <option key={o} value={o} style={{ color: "#111" }}>{o}</option>)}
        </select>
      ) : (
        <input type={field.type === "number" ? "number" : field.type === "date" ? "date" : "text"} {...common} />
      )}
    </label>
  );
}

function MultiEditor({ section, selected, onToggle }) {
  const sel = selected || [];
  const [customVal, setCustomVal] = useState("");
  const addCustom = () => {
    const v = customVal.trim();
    if (v && sel.indexOf(v) === -1) { onToggle(section.id, v); }
    setCustomVal("");
  };
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.7rem" }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
        {section.options.map((o) => {
          const on = sel.indexOf(o) !== -1;
          return (
            <button key={o} type="button" onClick={() => onToggle(section.id, o)}
              className={on ? "liquid-glass-strong" : ""} style={{ cursor: "pointer", borderRadius: "9999px",
                padding: "0.4rem 0.9rem", fontFamily: "var(--font-body)", fontSize: "0.8rem",
                fontWeight: on ? 600 : 400, color: on ? "#fff" : "rgba(255,255,255,0.7)",
                border: on ? "none" : "1px solid rgba(255,255,255,0.22)", background: on ? undefined : "transparent" }}>
              {o}
            </button>
          );
        })}
        {/* show custom chips that aren't in the predefined options */}
        {sel.filter((s) => section.options.indexOf(s) === -1).map((c) => (
          <button key={c} type="button" onClick={() => onToggle(section.id, c)}
            className="liquid-glass-strong" style={{ cursor: "pointer", borderRadius: "9999px",
              padding: "0.4rem 0.9rem", fontFamily: "var(--font-body)", fontSize: "0.8rem",
              fontWeight: 600, color: "#fff", border: "none" }}>
            {c} ×
          </button>
        ))}
      </div>
      {section.customInput && (
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <input type="text" value={customVal} placeholder="+ Add your own"
            onChange={(e) => setCustomVal(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addCustom(); } }}
            style={Object.assign({}, inputStyle, { flex: 1, maxWidth: "240px", borderRadius: "9999px",
              padding: "0.4rem 0.85rem", fontSize: "0.82rem" })} />
          {customVal.trim() && (
            <button type="button" onClick={addCustom}
              className="liquid-glass-strong udaan-lift" style={{ cursor: "pointer", border: "none",
                borderRadius: "9999px", padding: "0.4rem 0.85rem", color: "#fff",
                fontFamily: "var(--font-body)", fontSize: "0.8rem", fontWeight: 600 }}>
              + Add
            </button>
          )}
        </div>
      )}
    </div>
  );
}


function BoolEditor({ section, draft, onSet }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.7rem" }}>
      {section.fields.map((f) => {
        const v = draft[f.key];
        return (
          <div key={f.key} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem" }}>
            <span style={{ fontFamily: "var(--font-body)", fontSize: "0.9rem", color: "#fff" }}>{f.label}</span>
            <div style={{ display: "flex", gap: "0.4rem" }}>
              {[["Yes", true], ["No", false]].map(([txt, val]) => {
                const on = v === val;
                return (
                  <button key={txt} type="button" onClick={() => onSet(f.key, val)}
                    className={on ? "liquid-glass-strong" : ""} style={{ cursor: "pointer", borderRadius: "9999px",
                      padding: "0.32rem 0.85rem", fontFamily: "var(--font-body)", fontSize: "0.8rem",
                      fontWeight: on ? 600 : 400, color: on ? "#fff" : "rgba(255,255,255,0.6)",
                      border: on ? "none" : "1px solid rgba(255,255,255,0.22)", background: on ? undefined : "transparent" }}>
                    {txt}
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ---------- section card ---------- */
function SectionCard({ section, schema, edit, draft, handlers, Icon }) {
  return (
    <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "1.4rem 1.5rem",
      display: "flex", flexDirection: "column", gap: "1.1rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.7rem" }}>
        <div className="liquid-glass" style={{ width: 38, height: 38, borderRadius: "var(--radius-tile)",
          flex: "0 0 auto", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Icon name={schema.icon} size={20} style={{ color: "#fff" }} />
        </div>
        <h3 style={{ margin: 0, fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "1.02rem",
          color: "#fff", letterSpacing: "-0.2px" }}>{schema.title}</h3>
      </div>

      {edit && schema.hint && (
        <p style={{ margin: "-0.4rem 0 0", fontFamily: "var(--font-body)", fontWeight: 300,
          fontSize: "0.8rem", color: "rgba(255,255,255,0.65)" }}>{schema.hint}</p>
      )}

      {/* ---- fields ---- */}
      {schema.type !== "multi" && schema.type !== "bool" && (
        edit ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.9rem 1.2rem" }}>
            {schema.fields.map((f) => <EditField key={f.key} field={f} value={draft[f.key]} onChange={handlers.setField} />)}
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1rem 1.5rem" }}>
            {section.fields.map((f) => <Field key={f.label} label={f.label} value={f.value} />)}
          </div>
        )
      )}

      {/* ---- multi ---- */}
      {schema.type === "multi" && (
        edit ? <MultiEditor section={schema} selected={draft[schema.id]} onToggle={handlers.toggleMulti} />
             : <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                 {section.items.map((it) => <PillChip key={it.label} label={it.label} on={it.on} />)}
               </div>
      )}

      {/* ---- bool ---- */}
      {schema.type === "bool" && (
        edit ? <BoolEditor section={schema} draft={draft} onSet={handlers.setField} />
             : <div style={{ display: "flex", flexWrap: "wrap", gap: "0.55rem" }}>
                 {section.items.map((it) => <StatusChip key={it.label} label={it.label} on={it.on} Icon={Icon} />)}
               </div>
      )}
    </div>
  );
}

/* ---------- completion ring ---------- */
function Ring({ value, size = 96, stroke = 7 }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const off = c * (1 - value / 100);
  return (
    <div style={{ position: "relative", width: size, height: size, flex: "0 0 auto" }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth={stroke} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#fff" strokeWidth={stroke}
          strokeLinecap="round" strokeDasharray={c} strokeDashoffset={off} />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center" }}>
        <span style={{ fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "1.5rem", color: "#fff", lineHeight: 1 }}>{value}%</span>
        <span style={{ fontFamily: "var(--font-body)", fontSize: "0.6rem", letterSpacing: "0.4px",
          textTransform: "uppercase", color: LABEL, marginTop: "0.15rem" }}>Complete</span>
      </div>
    </div>
  );
}

function MetricChip({ label, value }) {
  return (
    <div className="liquid-glass" style={{ borderRadius: "var(--radius-tile)", padding: "0.7rem 1rem",
      display: "flex", flexDirection: "column", gap: "0.1rem", minWidth: 0 }}>
      <span style={{ fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "1.4rem", color: "#fff", lineHeight: 1 }}>{value}</span>
      <span style={{ fontFamily: "var(--font-body)", fontSize: "0.68rem", letterSpacing: "0.3px",
        textTransform: "uppercase", color: LABEL }}>{label}</span>
    </div>
  );
}

/* ---------- the sheet ---------- */
function Profile({ persona, onClose, initialEdit }) {
  const Icon = window.UdaanIcon;
  const schema = window.UDAAN_PROFILE_SCHEMA;
  const sectionsSchema = useMemo(
    () => schema.common.concat(schema.personas[persona] || schema.personas.students),
    [persona]
  );

  const [values, setValues] = useState(() => window.UDAAN_LOAD_PROFILE(persona));
  const [built, setBuilt] = useState(() => window.UDAAN_PROFILE_BUILT());
  const [edit, setEdit] = useState(!!initialEdit);
  const [draft, setDraft] = useState(() => window.UDAAN_LOAD_PROFILE(persona));

  const data = useMemo(() => window.UDAAN_BUILD_FROM_VALUES(persona, values), [persona, values]);

  const handlers = {
    setField: (key, val) => setDraft((d) => Object.assign({}, d, { [key]: val })),
    toggleMulti: (id, opt) => setDraft((d) => {
      const arr = new Set(d[id] || []);
      if (arr.has(opt)) arr.delete(opt); else arr.add(opt);
      return Object.assign({}, d, { [id]: Array.from(arr) });
    }),
  };

  const startEdit = () => { setDraft(Object.assign({}, values)); setEdit(true); };
  const save = () => {
    window.UDAAN_SAVE_PROFILE(draft);
    setValues(draft); setBuilt(true); setEdit(false);
    document.querySelector('[data-profile-scroll]')?.scrollTo({ top: 0, behavior: "smooth" });
  };
  const cancel = () => { if (built) setEdit(false); else onClose(); };

  const headerName = (edit ? draft.full_name : data.identity.full_name) || "";

  return (
    <div className="udaan-profile-overlay" data-profile-scroll
      style={{ position: "fixed", inset: 0, zIndex: 100, overflowY: "auto", background: "rgba(0,0,0,0.62)",
        backdropFilter: "blur(14px)", WebkitBackdropFilter: "blur(14px)" }}
      onClick={onClose}>

      {/* sticky top bar */}
      <div style={{ position: "sticky", top: 0, zIndex: 2, display: "flex", alignItems: "center",
        justifyContent: "space-between", gap: "1rem", padding: "1rem clamp(1.25rem, 4vw, 3rem)",
        background: "linear-gradient(180deg, rgba(0,0,0,0.55), rgba(0,0,0,0))" }}
        onClick={(e) => e.stopPropagation()}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", color: "#fff" }}>
          <Icon name="settings" size={18} style={{ color: "rgba(255,255,255,0.8)" }} />
          <span style={{ fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "0.95rem", letterSpacing: "0.3px" }}>
            {edit ? "Build Your Profile" : "My Profile"}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          {edit ? (
            <>
              <button onClick={cancel} className="liquid-glass udaan-lift" style={pillBtn}>Cancel</button>
              <button onClick={save} className="liquid-glass-strong udaan-lift" style={Object.assign({}, pillBtn, { fontWeight: 600 })}>Save profile</button>
            </>
          ) : (
            <>
              <button onClick={startEdit} className="liquid-glass-strong udaan-lift" style={Object.assign({}, pillBtn, { fontWeight: 600 })}>Edit profile</button>
              <button onClick={onClose} aria-label="Close profile" className="liquid-glass udaan-lift" style={pillBtn}>
                Close
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M6 6l12 12M18 6 6 18" /></svg>
              </button>
            </>
          )}
        </div>
      </div>

      <div className="udaan-profile-sheet"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: "1100px", margin: "0 auto", padding: "0.5rem clamp(1.25rem, 4vw, 3rem) 5rem" }}>

        {/* identity hero */}
        <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)",
          padding: "clamp(1.5rem, 3vw, 2.25rem)", display: "flex", flexWrap: "wrap", alignItems: "center", gap: "1.75rem" }}>
          <span className="liquid-glass" style={{ width: 84, height: 84, borderRadius: "9999px", flex: "0 0 auto",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "2rem", color: "#fff" }}>
            {initials(headerName)}
          </span>
          <div style={{ flex: "1 1 220px", minWidth: 0 }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
              <h1 style={{ margin: 0, fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#fff",
                fontSize: "clamp(1.8rem, 4vw, 2.6rem)", lineHeight: 1, letterSpacing: "-1px" }}>
                {headerName || "Your name"}
              </h1>
              <span className="liquid-glass" style={{ borderRadius: "9999px", padding: "0.3rem 0.8rem",
                fontFamily: "var(--font-body)", fontSize: "0.78rem", fontWeight: 600, color: "#fff" }}>{data.personaLabel}</span>
            </div>
            <p style={{ margin: "0.6rem 0 0", fontFamily: "var(--font-body)", fontWeight: 300, fontSize: "0.92rem",
              color: "rgba(255,255,255,0.85)" }}>
              {edit ? "Fill in your details below — only what you enter is saved. You can update this anytime."
                    : (data.identity.email || "Add your details to improve your matches")}
            </p>
          </div>
          <Ring value={edit ? window.UDAAN_BUILD_FROM_VALUES(persona, draft).completion : data.completion} />
        </div>

        {/* metrics */}
        <div style={{ marginTop: "1rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.85rem" }}>
          {(edit ? window.UDAAN_BUILD_FROM_VALUES(persona, draft) : data).metrics.map((m) => <MetricChip key={m.label} label={m.label} value={m.value} />)}
        </div>

        {/* sections */}
        <div style={{ marginTop: "1.4rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "1rem", alignItems: "start" }}>
          {sectionsSchema.map((s, i) => (
            <SectionCard key={s.id} schema={s} section={data.sections[i]} edit={edit} draft={draft} handlers={handlers} Icon={Icon} />
          ))}
        </div>

        {/* footer */}
        {edit ? (
          <div className="liquid-glass" style={{ marginTop: "1.4rem", borderRadius: "var(--radius-card)",
            padding: "1.25rem 1.5rem", display: "flex", flexWrap: "wrap", alignItems: "center",
            justifyContent: "space-between", gap: "1rem" }}>
            <span style={{ fontFamily: "var(--font-body)", fontWeight: 300, fontSize: "0.9rem", color: "rgba(255,255,255,0.88)" }}>
              Save what you have now — you can complete the rest later.
            </span>
            <div style={{ display: "flex", gap: "0.6rem" }}>
              <button onClick={cancel} className="liquid-glass udaan-lift" style={pillBtn}>Cancel</button>
              <button onClick={save} className="liquid-glass-strong udaan-lift" style={Object.assign({}, pillBtn, { fontWeight: 600 })}>Save profile</button>
            </div>
          </div>
        ) : (
          <div className="liquid-glass" style={{ marginTop: "1.4rem", borderRadius: "var(--radius-card)",
            padding: "1.25rem 1.5rem", display: "flex", flexWrap: "wrap", alignItems: "center",
            justifyContent: "space-between", gap: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.7rem", minWidth: 0 }}>
              <Icon name="alert" size={20} style={{ color: "#ffd27a", flex: "0 0 auto" }} />
              <span style={{ fontFamily: "var(--font-body)", fontWeight: 300, fontSize: "0.9rem", color: "rgba(255,255,255,0.88)", lineHeight: 1.4 }}>
                Your profile is <b style={{ fontWeight: 600 }}>{data.completion}% complete</b> ({data.fieldsFilled} of {data.fieldsTotal} fields). Finish the rest to improve your matches.
              </span>
            </div>
            <button onClick={startEdit} className="liquid-glass-strong udaan-lift" style={Object.assign({}, pillBtn, { fontWeight: 600 })}>
              {built ? "Edit profile" : "Build profile"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

const pillBtn = {
  display: "inline-flex", alignItems: "center", gap: "0.4rem", border: "none", cursor: "pointer",
  borderRadius: "9999px", padding: "0.5rem 1.05rem", color: "#fff",
  fontFamily: "var(--font-body)", fontWeight: 500, fontSize: "0.85rem", whiteSpace: "nowrap",
};

window.UdaanProfile = Profile;
