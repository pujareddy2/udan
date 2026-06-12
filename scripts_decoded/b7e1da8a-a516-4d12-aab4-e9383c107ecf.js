/* global React */
// UDAAN AI — persona dashboards rendered in the Astra visual language.

const { useState, useRef, useEffect } = React;

function Dashboard() {
  const DS = window.AstraDesignSystem_bf0882;
  const { Badge, Button, BlurText, StatCard, Tag } = DS;
  const Icon = window.UdaanIcon;
  const M = window.Motion.motion;
  const AnimatePresence = window.Motion.AnimatePresence;
  const personas = window.UDAAN_PERSONAS;

  const [profileOpen, setProfileOpen] = useState(() => !(window.UDAAN_PROFILE_BUILT && window.UDAAN_PROFILE_BUILT()));
  const [profileEdit, setProfileEdit] = useState(() => !(window.UDAAN_PROFILE_BUILT && window.UDAAN_PROFILE_BUILT()));
  const openProfile = (editMode) => { setProfileEdit(!!editMode); setProfileOpen(true); };

  const navInitials = (() => {
    try {
      const s = JSON.parse(localStorage.getItem("udaan_profile") || "null");
      const n = s && s.full_name;
      if (!n) return "AK";
      return n.trim().split(/\s+/).slice(0, 2).map((x) => x[0]).join("").toUpperCase() || "AK";
    } catch (e) { return "AK"; }
  })();

  const startKey = window.__startPersona || new URLSearchParams(location.search).get("persona");
  const startIdx = personas.findIndex((p) => p.key === startKey);
  const [idx, setIdx] = useState(startIdx === -1 ? 0 : startIdx);
  const p = personas[idx];
  const userId = localStorage.getItem("user_id") || "1";

  const [apiData, setApiData] = useState(null);
  const [loadingApi, setLoadingApi] = useState(false);

  useEffect(() => {
    if (p.key === "farmers" && userId) {
      setLoadingApi(true);
      Promise.all([
        fetch(`http://localhost:8000/api/v1/dashboard/farmer/${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/wallet/opportunities?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/farmer/recommendations?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/farmer/documents/summary?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/readiness?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/value?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/approval/farmer/${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/deadlines/upcoming?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/timeline?user_id=${userId}`).then(r=>r.ok?r.json():null),
      ]).then(res => {
        setApiData({
          summary: res[0], wallet: res[1], ai: res[2], docs: res[3],
          readiness: res[4], value: res[5], approval: res[6],
          deadlines: res[7], timeline: res[8]
        });
        setLoadingApi(false);
      }).catch(e => {
        console.error(e); setLoadingApi(false);
      });
    }
  }, [p.key, userId]);

  const rise = (delay) => ({
    initial: { filter: "blur(10px)", opacity: 0, y: 20 },
    animate: { filter: "blur(0px)", opacity: 1, y: 0 },
    transition: { duration: 0.7, ease: "easeOut", delay },
  });

  const scrollTop = () => document.getElementById("udaan-scroll")?.scrollTo({ top: 0, behavior: "smooth" });
  const selectPersona = (i) => { setIdx(i); scrollTop(); };

  return (
    <div style={{ position: "relative", minHeight: "100vh", background: "#000" }}>
      <div style={{ position: "fixed", inset: 0, zIndex: 0, overflow: "hidden", background: "#000" }}>
        <video key={p.key} className="udaan-bgvideo" src={p.video} autoPlay muted loop playsInline preload="auto"
          onCanPlay={(e) => e.currentTarget.play().catch(() => {})}
          style={{ position: "absolute", left: "50%", top: "50%", transform: "translate(-50%, -50%)",
            minWidth: "100%", minHeight: "100%", width: "auto", height: "auto",
            objectFit: "cover", objectPosition: p.objectPosition,
          }}
        />
        <div style={{ position: "absolute", inset: 0, pointerEvents: "none",
          background: "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.15) 16%, rgba(0,0,0,0.15) 55%, rgba(0,0,0,0.6) 100%)",
        }} />
      </div>

      <UdaanNav personas={personas} idx={idx} onSelect={selectPersona} onProfile={() => openProfile(false)} initials={navInitials} Icon={Icon} />

      <div id="udaan-scroll" style={{ position: "relative", zIndex: 10, height: "100vh", overflowY: "auto" }}>
        <div key={p.key}>
          {/* HERO */}
          <section data-screen-label={p.label + " dashboard"} style={{
              minHeight: "100vh", display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center", textAlign: "center",
              padding: "7rem 1.5rem 3rem",
            }}>
            <M.div {...rise(0.35)}><Badge chip={p.chip}>{p.tagline}</Badge></M.div>
            <div style={{ marginTop: "1.75rem" }}>
              <BlurText key={p.key} text={p.heading} style={{
                  fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#fff",
                  fontSize: "clamp(2.5rem, 6vw, 5rem)", lineHeight: 0.92, letterSpacing: "-1px", maxWidth: "min(92vw, 900px)",
                }} />
            </div>
            <M.p {...rise(0.75)} style={{
              marginTop: "1.25rem", maxWidth: "44rem", fontSize: "clamp(0.95rem, 1.4vw, 1.1rem)",
              fontWeight: 300, lineHeight: 1.4, color: "rgba(255,255,255,0.92)", fontFamily: "var(--font-body)",
            }}>{p.sub}</M.p>

            {p.languages && (
              <M.div {...rise(0.85)} style={{ marginTop: "1.1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Icon name="globe" size={16} style={{ color: "rgba(255,255,255,0.8)" }} />
                {p.languages.map((l, i) => (
                  <span key={l} className="liquid-glass" style={{
                    borderRadius: "9999px", padding: "0.3rem 0.8rem", fontSize: "0.8rem",
                    fontFamily: "var(--font-body)", fontWeight: i === 0 ? 600 : 400, color: "#fff",
                  }}>{l}</span>
                ))}
              </M.div>
            )}

            <M.div {...rise(1.0)} style={{ marginTop: "1.75rem", display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "center", gap: "1.25rem" }}>
              <Button variant="glass" icon="arrow-up-right">{p.cta}</Button>
              <Button variant="ghost" icon="play" iconPosition="left">{p.secondaryCta}</Button>
            </M.div>
          </section>

          {/* DYNAMIC FARMER DASHBOARD VS STATIC DASHBOARDS */}
          {p.key === "farmers" ? (
             <FarmerSections data={apiData} loading={loadingApi} Icon={Icon} Button={Button} Tag={Tag} />
          ) : (
             <>
                {/* STATIC CATEGORIES */}
                <section style={{ padding: "2rem clamp(1.5rem, 5vw, 5rem) 1rem", maxWidth: "1240px", margin: "0 auto" }}>
                  <SectionLabel>{p.categoriesTitle}</SectionLabel>
                  <div style={{ marginTop: "1.5rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.25rem" }}>
                    {p.categories.map((c) => <CategoryCard key={c.name} c={c} Icon={Icon} />)}
                  </div>
                </section>

                {/* STATIC FEED */}
                <section style={{ padding: "2.5rem clamp(1.5rem, 5vw, 5rem) 2rem", maxWidth: "1240px", margin: "0 auto" }}>
                  <SectionLabel>{p.feedTitle}</SectionLabel>
                  <div style={{ marginTop: "1.5rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.25rem" }}>
                    {p.feed.map((f) => <FeedCard key={f.name} f={f} Tag={Tag} Button={Button} Icon={Icon} />)}
                  </div>
                </section>
             </>
          )}

          {/* AI CTA (All Personas) */}
          <section style={{ padding: "1rem clamp(1.5rem, 5vw, 5rem) 6rem", maxWidth: "1240px", margin: "0 auto" }}>
            <div className="liquid-glass-strong" style={{
              borderRadius: "var(--radius-card)", padding: "clamp(2rem, 4vw, 3rem)",
              display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "1.5rem",
            }}>
              <div style={{ maxWidth: "40ch" }}>
                <h3 style={{
                  margin: 0, fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#fff",
                  fontSize: "clamp(1.75rem, 3.5vw, 2.5rem)", lineHeight: 1, letterSpacing: "-1px",
                }}>Chat with UDAAN AI</h3>
                <p style={{
                  margin: "0.75rem 0 0", fontFamily: "var(--font-body)", fontWeight: 300,
                  fontSize: "0.95rem", lineHeight: 1.4, color: "rgba(255,255,255,0.9)",
                }}>Ask about any scheme, check your eligibility in seconds and get step-by-step help applying — anytime.</p>
              </div>
              <Button variant="white" icon="arrow-up-right">Start chatting</Button>
            </div>
          </section>
        </div>
      </div>

      {/* Floating AI chat button - Upgraded for Farmers */}
      {p.key === "farmers" ? (
          <div style={{ position: "fixed", bottom: "1.5rem", right: "1.5rem", zIndex: 100, display: "flex", flexDirection: "column", gap: "0.5rem", alignItems: "flex-end" }}>
             <button className="liquid-glass" style={{ border: "none", padding: "0.6rem 1.2rem", borderRadius: "999px", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.9rem", cursor: "pointer", whiteSpace: "nowrap" }}>🎤 Speak in Telugu</button>
             <button className="liquid-glass" style={{ border: "none", padding: "0.6rem 1.2rem", borderRadius: "999px", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.9rem", cursor: "pointer", whiteSpace: "nowrap" }}>🎤 Speak in Hindi</button>
             <button className="liquid-glass" style={{ border: "none", padding: "0.6rem 1.2rem", borderRadius: "999px", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.9rem", cursor: "pointer", whiteSpace: "nowrap" }}>🎤 Speak in English</button>
             <button aria-label="Chat with UDAAN AI" className="udaan-fab liquid-glass-strong" style={{ marginTop: "0.5rem" }}>
                <Icon name="message" size={26} style={{ color: "#fff" }} />
             </button>
          </div>
      ) : (
          <button aria-label="Chat with UDAAN AI" className="udaan-fab liquid-glass-strong">
            <Icon name="message" size={26} style={{ color: "#fff" }} />
          </button>
      )}

      {profileOpen && <window.UdaanProfile key={p.key} persona={p.key} initialEdit={profileEdit} onClose={() => setProfileOpen(false)} />}
    </div>
  );
}

// -----------------------------------------------------
// FARMER DYNAMIC SECTIONS
// -----------------------------------------------------
function FarmerSections({ data, loading, Icon, Button, Tag }) {
   if (loading || !data) return <div style={{ padding: "3rem", textAlign: "center", color: "#fff", fontFamily: "var(--font-body)", fontSize: "1.2rem" }}>Loading UDAAN Engines...</div>;

   const sum = data.summary || {};
   const wallet = data.wallet || { eligible_opportunities: [], status_counts: {} };
   const ai = data.ai || {};
   const docs = data.docs || {};
   const readi = data.readiness || {};
   const val = data.value || {};
   const app = data.approval || {};
   const time = data.timeline || [];
   const dead = data.deadlines?.deadlines || [];

   return (
      <div style={{ maxWidth: "1240px", margin: "0 auto", padding: "1rem clamp(1.5rem, 5vw, 5rem)", display: "flex", flexDirection: "column", gap: "2.5rem" }}>
         
         {/* 1. Farmer Summary Card */}
         <section>
            <SectionLabel>Farmer Summary</SectionLabel>
            <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", marginTop: "1rem", color: "#fff", display: "flex", flexDirection: "column", gap: "1rem" }}>
               <h3 style={{ margin: "0", fontSize: "1.8rem", fontFamily: "var(--font-heading)", fontStyle: "italic" }}>Welcome {sum.farmer_name || "Farmer"}</h3>
               <div style={{ display: "flex", flexWrap: "wrap", gap: "1.5rem", fontFamily: "var(--font-body)", fontSize: "1rem" }}>
                  <div><strong style={{ opacity: 0.8 }}>Profile:</strong> {sum.profile_completion || 0}% Complete</div>
                  <div><strong style={{ opacity: 0.8 }}>Eligible:</strong> {sum.eligible_opportunities || 0} Schemes</div>
                  <div><strong style={{ opacity: 0.8 }}>Potential Value:</strong> ₹{sum.potential_value || 0}</div>
                  <div><strong style={{ opacity: 0.8 }}>Missing Docs:</strong> {sum.documents_missing || 0}</div>
                  <div><strong style={{ opacity: 0.8 }}>Approval Score:</strong> {sum.approval_score || 0}%</div>
               </div>
            </div>
         </section>

         {/* 2. Quick Access Cards (Static - Market Prices Removed) */}
         <section>
            <SectionLabel>Quick Access</SectionLabel>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.25rem", marginTop: "1rem" }}>
               {[
                 { icon: "sprout", name: "PM Kisan", stat: "₹6,000 / yr", note: "Direct income support" },
                 { icon: "shield", name: "Crop Insurance", stat: "2% premium", note: "PM Fasal Bima Yojana" },
                 { icon: "coin", name: "Subsidies", stat: "120+ schemes", note: "Seed · solar · drip" },
                 { icon: "bank", name: "Agriculture Loans", stat: "@ 4% interest", note: "Kisan Credit Card" }
               ].map(c => <CategoryCard key={c.name} c={c} Icon={Icon} />)}
            </div>
         </section>

         {/* 3. Opportunity Wallet */}
         <section>
            <SectionLabel>Opportunity Wallet</SectionLabel>
            <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", marginTop: "1rem", color: "#fff", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "2rem" }}>
               <div><div style={{ opacity: 0.8, fontFamily: "var(--font-body)" }}>Ready To Apply</div><div style={{ fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)" }}>{wallet.status_counts?.["Ready"] || 4}</div></div>
               <div><div style={{ opacity: 0.8, fontFamily: "var(--font-body)" }}>Blocked</div><div style={{ fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ff6b6b" }}>{wallet.status_counts?.["Blocked"] || 2}</div></div>
               <div><div style={{ opacity: 0.8, fontFamily: "var(--font-body)" }}>Need Clarification</div><div style={{ fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ffd27a" }}>{wallet.status_counts?.["Clarification"] || 1}</div></div>
               <div><div style={{ opacity: 0.8, fontFamily: "var(--font-body)" }}>Applied</div><div style={{ fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7fe0a0" }}>{wallet.status_counts?.["Applied"] || 0}</div></div>
            </div>
         </section>

         {/* 4. AI Recommendations */}
         <section>
            <SectionLabel>AI Recommended For You</SectionLabel>
            <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", color: "#fff", background: "linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%)" }}>
               <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "2.2rem", fontFamily: "var(--font-heading)", fontStyle: "italic" }}>{ai.scheme_name || "Rythu Bandhu"}</h3>
               <p style={{ margin: 0, opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.1rem" }}>Based on: {ai.reasoning || "2 Acres Land, Paddy Crop, Telangana"}</p>
               <div style={{ marginTop: "1.5rem", fontSize: "1.5rem", fontFamily: "var(--font-body)" }}>Potential Benefit: <strong style={{ color: "#7fe0a0" }}>{ai.benefit || "₹20,000"}</strong></div>
            </div>
         </section>

         {/* 5. Eligible Schemes Feed */}
         <section>
            <SectionLabel>Eligible Schemes</SectionLabel>
            <div style={{ marginTop: "1.5rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.25rem" }}>
               {(wallet.eligible_opportunities?.length ? wallet.eligible_opportunities : [
                 { name: "PM-KISAN Samman Nidhi", amount: "₹6,000 / year", deadline: "Always open", status: "Eligible", ok: true, tag: "Income" },
                 { name: "Kisan Credit Card", amount: "up to ₹3,00,000", deadline: "Open", status: "Eligible", ok: true, tag: "Loan" },
                 { name: "Pradhan Mantri Fasal Bima", amount: "2% premium", deadline: "Season-based", status: "Eligible", ok: true, tag: "Insurance" }
               ]).map((f, i) => <FeedCard key={i} f={f} Tag={Tag} Button={Button} Icon={Icon} />)}
            </div>
         </section>

         {/* 6. Missing Documents */}
         <section>
            <SectionLabel>Missing Documents</SectionLabel>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem" }}>
               {(docs.missing?.length ? docs.missing : ["Land Passbook Missing", "Income Certificate Missing"]).map((doc, i) => (
                  <div key={i} className="liquid-glass" style={{ padding: "1.25rem 1.5rem", borderRadius: "var(--radius-card)", color: "#fff", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
                     <div style={{ color: "#ffd27a", fontWeight: "bold", fontFamily: "var(--font-body)", fontSize: "1.1rem" }}>{doc}</div>
                     <div style={{ display: "flex", gap: "0.5rem" }}>
                        <Button variant="ghost" size="sm">View Sample</Button>
                        <Button variant="white" size="sm">How To Get</Button>
                     </div>
                  </div>
               ))}
            </div>
         </section>

         {/* 7. Readiness Score */}
         <section>
            <SectionLabel>Readiness Score</SectionLabel>
            <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", color: "#fff", display: "flex", gap: "3rem", alignItems: "center", flexWrap: "wrap" }}>
               <div style={{ fontSize: "4rem", fontWeight: "bold", fontFamily: "var(--font-heading)", fontStyle: "italic", lineHeight: 1 }}>{readi.overall_score || 82}%</div>
               <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", opacity: 0.9, fontFamily: "var(--font-body)", fontSize: "1.2rem" }}>
                  <div>Profile: <strong>{readi.breakdown?.profile || 90}%</strong></div>
                  <div>Documents: <strong>{readi.breakdown?.documents || 70}%</strong></div>
                  <div>Eligibility: <strong>{readi.breakdown?.eligibility || 85}%</strong></div>
               </div>
            </div>
         </section>

         {/* 8. Value Wallet */}
         <section>
            <SectionLabel>Value Wallet</SectionLabel>
            <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", color: "#fff", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "2rem" }}>
               <div><div style={{ opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.1rem" }}>Eligible Value</div><div style={{ fontSize: "2.5rem", fontWeight: "bold", fontFamily: "var(--font-heading)" }}>₹{val.eligible_value || "56,000"}</div></div>
               <div><div style={{ opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.1rem" }}>Potential Value</div><div style={{ fontSize: "2.5rem", fontWeight: "bold", fontFamily: "var(--font-heading)" }}>₹{val.potential_value || "1,20,000"}</div></div>
               <div><div style={{ opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.1rem" }}>Recovery Value</div><div style={{ fontSize: "2.5rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7fe0a0" }}>₹{val.recovery_value || "64,000"}</div></div>
            </div>
         </section>

         {/* 9. Approval Probability */}
         <section>
            <SectionLabel>Approval Probability</SectionLabel>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1.25rem", marginTop: "1rem" }}>
               {(app.opportunities?.length ? app.opportunities : [
                 { name: "PM Kisan", score: 92 }, { name: "Crop Insurance", score: 86 }, { name: "KCC Loan", score: 71 }
               ]).map((op, i) => (
                  <div key={i} className="liquid-glass" style={{ padding: "1.5rem", borderRadius: "var(--radius-card)", color: "#fff", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                     <span style={{ fontFamily: "var(--font-body)", fontSize: "1.1rem", fontWeight: 600 }}>{op.name}</span>
                     <span style={{ fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "1.8rem", fontWeight: "bold", color: op.score > 80 ? "#7fe0a0" : "#ffd27a" }}>{op.score}%</span>
                  </div>
               ))}
            </div>
         </section>

         {/* 10. Urgent Deadlines */}
         <section>
            <SectionLabel>Urgent Deadlines</SectionLabel>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem" }}>
               {(dead.length ? dead : [
                 { name: "Solar Subsidy", days: "3 Days Remaining" },
                 { name: "Insurance Enrollment", days: "7 Days Remaining" }
               ]).map((d, i) => (
                  <div key={i} className="liquid-glass" style={{ padding: "1.5rem", borderRadius: "var(--radius-card)", color: "#fff", borderLeft: "6px solid #ff6b6b", background: "linear-gradient(90deg, rgba(255,107,107,0.1) 0%, rgba(0,0,0,0) 100%)" }}>
                     <div style={{ color: "#ff6b6b", fontWeight: "bold", fontSize: "1rem", fontFamily: "var(--font-body)", textTransform: "uppercase" }}>{d.days || `${d.days_remaining} Days Remaining`}</div>
                     <div style={{ fontSize: "1.4rem", marginTop: "0.25rem", fontFamily: "var(--font-body)", fontWeight: 600 }}>{d.name || d.scheme}</div>
                  </div>
               ))}
            </div>
         </section>

         {/* 11. Timeline */}
         <section>
            <SectionLabel>Farmer Journey Timeline</SectionLabel>
            <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "2.5rem 2rem", marginTop: "1rem", color: "#fff", display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
               {(time.length ? time : ["PM Kisan Discovered", "Income Certificate Missing", "Document Uploaded", "Application Submitted", "Approved"]).map((t, i, arr) => (
                  <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
                     <div style={{ padding: "0.75rem 1.5rem", background: "rgba(255,255,255,0.15)", borderRadius: "99px", fontFamily: "var(--font-body)", fontWeight: 500, display: "flex", alignItems: "center", gap: "1rem" }}>
                         <div style={{ width: "24px", height: "24px", borderRadius: "50%", background: "#fff", color: "#000", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.8rem", fontWeight: "bold" }}>{i+1}</div>
                         {typeof t === 'string' ? t : (t.title || t.event)}
                     </div>
                     {i < arr.length - 1 && <div style={{ height: "40px", width: "2px", background: "rgba(255,255,255,0.3)", margin: "0 0 0 23px" }} />}
                  </div>
               ))}
            </div>
         </section>
      </div>
   );
}


/* ---------- Subcomponents ---------- */
function SectionLabel({ children }) {
  return <div style={{ fontSize: "0.875rem", color: "rgba(255,255,255,0.8)", fontFamily: "var(--font-body)", textTransform: "uppercase", letterSpacing: "1px" }}>{children}</div>;
}

function CategoryCard({ c, Icon }) {
  return (
    <div className="liquid-glass udaan-lift" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", cursor: "pointer", display: "flex", flexDirection: "column", gap: "0.9rem", minHeight: "168px" }}>
      <div className="liquid-glass" style={{ width: 46, height: 46, borderRadius: "var(--radius-tile)", display: "flex", alignItems: "center", justifyContent: "center", flex: "0 0 auto" }}>
        <Icon name={c.icon} size={24} style={{ color: "#fff" }} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "1.05rem", color: "#fff", letterSpacing: "-0.2px" }}>{c.name}</div>
        <div style={{ fontFamily: "var(--font-body)", fontWeight: 300, fontSize: "0.82rem", color: "rgba(255,255,255,0.75)", marginTop: "0.2rem" }}>{c.note}</div>
      </div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "0.85rem", color: "#fff" }}>{c.stat}</span>
        <span style={{ display: "flex", alignItems: "center", gap: "0.15rem", fontFamily: "var(--font-body)", fontWeight: 500, fontSize: "0.8rem", color: "rgba(255,255,255,0.85)" }}>View <Icon name="chev" size={15} /></span>
      </div>
    </div>
  );
}

function FeedCard({ f, Tag, Button, Icon }) {
  return (
    <div className="liquid-glass udaan-lift" style={{ borderRadius: "var(--radius-card)", padding: "1.4rem", display: "flex", flexDirection: "column", gap: "1rem", minHeight: "210px" }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "0.75rem" }}>
        <Tag>{f.tag}</Tag>
        <span className="liquid-glass" style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem", borderRadius: "9999px", padding: "0.25rem 0.6rem", fontFamily: "var(--font-body)", fontSize: "var(--text-2xs)", fontWeight: 600, color: "#fff" }}>
          <Icon name={f.ok ? "check" : "alert"} size={13} style={{ color: f.ok ? "#7fe0a0" : "#ffd27a" }} />
          {f.status}
        </span>
      </div>
      <div style={{ flex: 1 }}>
        <h4 style={{ margin: 0, fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#fff", fontSize: "1.45rem", lineHeight: 1.05, letterSpacing: "-0.5px" }}>{f.name}</h4>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: "1rem" }}>
        <div>
          <div style={{ fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "1rem", color: "#fff" }}>{f.amount}</div>
          <div style={{ fontFamily: "var(--font-body)", fontWeight: 300, fontSize: "0.8rem", color: "rgba(255,255,255,0.75)", marginTop: "0.15rem" }}>Deadline · {f.deadline}</div>
        </div>
        <Button variant="white" size="sm" icon="arrow-up-right">Apply</Button>
      </div>
    </div>
  );
}

function UdaanNav({ personas, idx, onSelect, onProfile, initials, Icon }) {
  return (
    <nav style={{ position: "fixed", top: "1rem", left: 0, right: 0, zIndex: 50, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 1.5rem", fontFamily: "var(--font-body)", gap: "1rem" }}>
      <div className="liquid-glass" style={{ display: "flex", alignItems: "center", gap: "0.6rem", borderRadius: "9999px", padding: "0.4rem 0.9rem 0.4rem 0.4rem", flex: "0 0 auto" }}>
        <span className="liquid-glass-strong" style={{ width: 40, height: 40, borderRadius: "9999px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "1.5rem", color: "#fff", lineHeight: 1 }}>u</span>
        <span style={{ fontWeight: 600, fontSize: "0.95rem", color: "#fff", letterSpacing: "0.3px", whiteSpace: "nowrap" }}>UDAAN AI</span>
      </div>
      <div className="liquid-glass" style={{ display: "flex", alignItems: "center", gap: "0.25rem", padding: "0.375rem", borderRadius: "9999px" }}>
        {personas.map((p, i) => (
          <button key={p.key} onClick={() => onSelect(i)} className={i === idx ? "liquid-glass-strong" : ""} style={{ border: "none", cursor: "pointer", borderRadius: "9999px", padding: "0.5rem 0.95rem", fontFamily: "var(--font-body)", fontWeight: 500, fontSize: "var(--text-sm)", whiteSpace: "nowrap", background: i === idx ? "#fff" : "transparent", color: i === idx ? "#000" : "rgba(255,255,255,0.9)", transition: "color 150ms ease" }}>{p.label}</button>
        ))}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flex: "0 0 auto" }}>
        <button className="liquid-glass udaan-icon-btn" aria-label="Notifications"><Icon name="bell" size={18} style={{ color: "#fff" }} /><span className="udaan-dot" /></button>
        <button className="liquid-glass udaan-icon-btn" aria-label="Settings"><Icon name="settings" size={18} style={{ color: "#fff" }} /></button>
        <button onClick={onProfile} className="liquid-glass udaan-lift" aria-label="Open profile" style={{ display: "flex", alignItems: "center", gap: "0.5rem", borderRadius: "9999px", border: "none", cursor: "pointer", padding: "0.3rem 0.85rem 0.3rem 0.3rem" }}>
          <span className="liquid-glass-strong" style={{ width: 30, height: 30, borderRadius: "9999px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "0.75rem", color: "#fff" }}>{initials || "AK"}</span>
          <span style={{ fontWeight: 500, fontSize: "0.85rem", color: "#fff" }}>Profile</span>
        </button>
      </div>
    </nav>
  );
}

window.UdaanDashboard = Dashboard;
