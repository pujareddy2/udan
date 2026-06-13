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
  const [alertsOpen, setAlertsOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);

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

      <UdaanNav personas={personas} idx={idx} onSelect={selectPersona} onProfile={() => openProfile(false)} initials={navInitials} Icon={Icon} onAlertOpen={() => setAlertsOpen(true)} />

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
          ) : p.key === "jobseekers" ? (
             <JobSeekerSections Icon={Icon} Button={Button} Tag={Tag} Badge={Badge} StatCard={StatCard} onAlertOpen={() => setAlertsOpen(true)} />
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

      {/* Floating AI chat button - Upgraded for Farmers / Job Seekers */}
      {p.key === "farmers" ? (
          <div style={{ position: "fixed", bottom: "1.5rem", right: "1.5rem", zIndex: 100, display: "flex", flexDirection: "column", gap: "0.5rem", alignItems: "flex-end" }}>
             <button className="liquid-glass" style={{ border: "none", padding: "0.6rem 1.2rem", borderRadius: "999px", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.9rem", cursor: "pointer", whiteSpace: "nowrap" }}>🎤 Speak in Telugu</button>
             <button className="liquid-glass" style={{ border: "none", padding: "0.6rem 1.2rem", borderRadius: "999px", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.9rem", cursor: "pointer", whiteSpace: "nowrap" }}>🎤 Speak in Hindi</button>
             <button className="liquid-glass" style={{ border: "none", padding: "0.6rem 1.2rem", borderRadius: "999px", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.9rem", cursor: "pointer", whiteSpace: "nowrap" }}>🎤 Speak in English</button>
             <button onClick={() => setChatOpen(true)} aria-label="Chat with UDAAN AI" className="udaan-fab liquid-glass-strong" style={{ marginTop: "0.5rem" }}>
                <Icon name="message" size={26} style={{ color: "#fff" }} />
             </button>
          </div>
      ) : (
          <button onClick={() => setChatOpen(true)} aria-label="Chat with UDAAN AI" className="udaan-fab liquid-glass-strong">
            <Icon name="message" size={26} style={{ color: "#fff" }} />
          </button>
      )}

      {alertsOpen && <AlertCenterDrawer onClose={() => setAlertsOpen(false)} Icon={Icon} Button={Button} />}
      {chatOpen && <VoiceChatDialog onClose={() => setChatOpen(false)} Icon={Icon} Button={Button} />}
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

function UdaanNav({ personas, idx, onSelect, onProfile, initials, Icon, onAlertOpen }) {
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
        <button onClick={onAlertOpen} className="liquid-glass udaan-icon-btn" aria-label="Notifications"><Icon name="bell" size={18} style={{ color: "#fff" }} /><span className="udaan-dot" /></button>
        <button className="liquid-glass udaan-icon-btn" aria-label="Settings"><Icon name="settings" size={18} style={{ color: "#fff" }} /></button>
        <button onClick={onProfile} className="liquid-glass udaan-lift" aria-label="Open profile" style={{ display: "flex", alignItems: "center", gap: "0.5rem", borderRadius: "9999px", border: "none", cursor: "pointer", padding: "0.3rem 0.85rem 0.3rem 0.3rem" }}>
          <span className="liquid-glass-strong" style={{ width: 30, height: 30, borderRadius: "9999px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "0.75rem", color: "#fff" }}>{initials || "AK"}</span>
          <span style={{ fontWeight: 500, fontSize: "0.85rem", color: "#fff" }}>Profile</span>
        </button>
      </div>
    </nav>
  );
}

// ============================================================================
// JOB SEEKER DASHBOARD SECTIONS
// ============================================================================
function JobSeekerSections({ Icon, Button, Tag, Badge, StatCard, onAlertOpen }) {
  const [profile, setProfile] = useState({
    name: "Aanya Kumar",
    qualification: "B.Tech in Computer Science",
    experience: "1 Year",
    role: "Junior Software Engineer",
    state: "Telangana",
    district: "Hyderabad",
    category: "OBC",
    age: 23,
    skills: ["Python", "SQL", "HTML", "CSS"],
    hasCasteCert: false
  });

  const [registeredCourse, setRegisteredCourse] = useState(false);
  const [uploadedCasteCert, setUploadedCasteCert] = useState(false);
  const [decoderOpp, setDecoderOpp] = useState(null);
  const [scamText, setScamText] = useState("");
  const [scamResult, setScamResult] = useState(null);
  const [sortBy, setSortBy] = useState("priority");

  const currentSkills = registeredCourse ? [...profile.skills, "Java Programming"] : profile.skills;
  const currentHasCasteCert = uploadedCasteCert;

  const profileCompletion = 85;
  const documentScore = currentHasCasteCert ? 100 : 70;
  const skillsScore = registeredCourse ? 100 : 80;
  const overallReadiness = Math.round((profileCompletion + documentScore + skillsScore) / 3);

  const opportunities = [
    {
      id: "SSC_CGL",
      name: "SSC CGL 2026 (Assistant Section Officer)",
      amount: "₹44,900 – ₹1,42,400 / mo",
      deadline: "20 Jul 2026",
      deadlineDays: 37,
      tag: "Govt Job",
      benefitVal: 44900,
      readiness: 100,
      source: "ssc.nic.in",
      isGovt: true,
      trustScore: 100,
      categoryAgeRelaxation: "3 years relaxation for OBC applied (Max Age: 33, Current Age: 23)",
      requiredDocs: ["Aadhaar", "Graduation Certificate"],
      missingDocs: [],
      missingSkills: [],
      reasoning: "You meet the graduation requirement. 3 years OBC age relaxation is applied."
    },
    {
      id: "NATS_APP",
      name: "NATS Technical Apprenticeship",
      amount: "₹12,000 / month",
      deadline: "31 Aug 2026",
      deadlineDays: 79,
      tag: "Apprenticeship",
      benefitVal: 12000,
      readiness: 95,
      source: "nats.education.gov.in",
      isGovt: true,
      trustScore: 95,
      requiredDocs: ["Aadhaar", "Graduation Certificate"],
      missingDocs: [],
      missingSkills: [],
      reasoning: "Qualified with B.Tech degree. Document verification matches."
    },
    {
      id: "PMKVY_JAVA",
      name: "PMKVY Java Developer Certification",
      amount: "Free Course + ₹8,000 Stipend",
      deadline: "15 Jul 2026",
      deadlineDays: 32,
      tag: "Skilling",
      benefitVal: 8000,
      readiness: registeredCourse ? 100 : 60,
      source: "pmkvyofficial.org",
      isGovt: true,
      trustScore: 90,
      requiredDocs: ["Aadhaar", "Tenth Class Certificate"],
      missingDocs: [],
      missingSkills: registeredCourse ? [] : ["Java Programming"],
      reasoning: registeredCourse ? "Registered in Java Upgrade Course." : "Requires Java Programming skill. Fix below to unlock.",
      upgradeAvailable: !registeredCourse
    },
    {
      id: "RRB_NTPC",
      name: "RRB NTPC — Railway Commercial Clerk",
      amount: "₹21,700 – ₹29,200 / mo",
      deadline: "05 Jul 2026",
      deadlineDays: 22,
      tag: "Govt Job",
      benefitVal: 21700,
      readiness: currentHasCasteCert ? 100 : 75,
      source: "rrbsecunderabad.nic.in",
      isGovt: true,
      trustScore: 100,
      categoryAgeRelaxation: "3 years relaxation for OBC applied (Max Age: 30, Current Age: 23)",
      requiredDocs: ["Aadhaar", "Caste Certificate", "Intermediate Certificate"],
      missingDocs: currentHasCasteCert ? [] : ["Caste Certificate"],
      missingSkills: [],
      reasoning: currentHasCasteCert ? "All documents verified." : "Requires Caste Certificate to verify OBC category status."
    }
  ];

  const getPriorityScore = (opp) => {
    const r = opp.readiness;
    const b = opp.benefitVal;
    const d = opp.deadlineDays;
    return (b / 1400) * 0.4 + r * 0.4 + (100 - d) * 0.2;
  };

  const sortedOpps = [...opportunities].sort((a, b) => {
    if (sortBy === "reward") return b.benefitVal - a.benefitVal;
    if (sortBy === "deadline") return a.deadlineDays - b.deadlineDays;
    if (sortBy === "readiness") return b.readiness - a.readiness;
    return getPriorityScore(b) - getPriorityScore(a);
  });

  const handleScamCheck = () => {
    if (!scamText.trim()) return;
    const desc = scamText.toLowerCase();
    const flags = [];
    if (desc.includes("registration fee") || desc.includes("refundable fee") || desc.includes("deposit")) {
      flags.push("Requests up-front cash deposit / registration fee (Common Scam Pattern)");
    }
    if (desc.includes("telegram") || desc.includes("whatsapp")) {
      flags.push("Requests joining a third-party chat channel (Telegram/WhatsApp group)");
    }
    if (desc.includes("no experience") && (desc.includes("huge payout") || desc.includes("earn 50000") || desc.includes("earn 100000"))) {
      flags.push("Unrealistic high weekly earnings with no qualification requirements");
    }
    if (desc.includes("processing charge") || desc.includes("visa charge")) {
      flags.push("Requests document processing / visa clearance charge");
    }

    if (flags.length > 0) {
      setScamResult({
        safe: false,
        level: "High Risk Alert 🚨",
        reasons: flags
      });
    } else {
      setScamResult({
        safe: true,
        level: "Safe Profile ✓",
        reasons: ["No obvious scam signatures detected. Always verify the physical address of the company."]
      });
    }
  };

  return (
    <div style={{ maxWidth: "1240px", margin: "0 auto", padding: "1rem clamp(1.5rem, 5vw, 5rem)", display: "flex", flexDirection: "column", gap: "2.5rem" }}>
      
      {/* 1. Profile Summary Strip */}
      <section>
        <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem 1.5rem", display: "flex", flexDirection: "column", gap: "1rem", color: "#fff" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <div style={{ fontSize: "0.8rem", color: "rgba(255,255,255,0.7)", textTransform: "uppercase", letterSpacing: "1px" }}>Logged In Job Seeker</div>
              <h3 style={{ margin: "0.2rem 0 0", fontSize: "1.8rem", fontFamily: "var(--font-heading)", fontStyle: "italic" }}>{profile.name}</h3>
            </div>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <span className="liquid-glass" style={{ padding: "0.4rem 0.8rem", borderRadius: "99px", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                <Icon name="check" size={14} style={{ color: "#7fe0a0" }} /> Verified Seeker
              </span>
              <span className="liquid-glass-strong" style={{ padding: "0.4rem 0.8rem", borderRadius: "99px", fontSize: "0.85rem", background: "rgba(255,255,255,0.15)" }}>
                {profile.category} Category
              </span>
            </div>
          </div>
          <div style={{ height: "1px", background: "rgba(255,255,255,0.1)" }} />
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", fontFamily: "var(--font-body)", fontSize: "0.95rem" }}>
            <div><strong style={{ opacity: 0.75 }}>Education:</strong> {profile.qualification}</div>
            <div><strong style={{ opacity: 0.75 }}>Experience:</strong> {profile.experience}</div>
            <div><strong style={{ opacity: 0.75 }}>Target Role:</strong> {profile.role}</div>
            <div><strong style={{ opacity: 0.75 }}>Location:</strong> {profile.district}, {profile.state}</div>
            <div><strong style={{ opacity: 0.75 }}>Skills:</strong> {currentSkills.join(", ")}</div>
          </div>
        </div>
      </section>

      {/* 2. Missed Opportunity Banner */}
      {!currentHasCasteCert && (
        <section>
          <div className="liquid-glass" style={{ borderLeft: "6px solid #ff6b6b", borderRadius: "var(--radius-card)", padding: "1.25rem 1.5rem", color: "#fff", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1.5rem", background: "linear-gradient(90deg, rgba(255,107,107,0.12) 0%, rgba(0,0,0,0) 100%)" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Icon name="alert" size={20} style={{ color: "#ff6b6b" }} />
                <strong style={{ fontSize: "1.1rem", fontFamily: "var(--font-heading)", fontStyle: "italic", letterSpacing: "0.5px" }}>Missed Opportunity Alert</strong>
              </div>
              <p style={{ margin: "0.5rem 0 0", fontSize: "0.92rem", lineHeight: 1.4, opacity: 0.9 }}>
                You permanently missed the <strong>National Merit Scholarship 2025 (₹12,000 value)</strong>. The deadline closed on 31 Jan 2026 because your <strong>Caste Certificate</strong> was not verified in time.
              </p>
            </div>
            <Button onClick={() => setUploadedCasteCert(true)} variant="white" size="sm">Fix Caste Certificate</Button>
          </div>
        </section>
      )}

      {/* 3. Grid for Readiness Ring & Document Readiness Panel & Roadmap */}
      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.5rem" }}>
        
        {/* Readiness Ring Card + Free Scheme Fix */}
        <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", color: "#fff", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div style={{ fontSize: "0.85rem", opacity: 0.8, textTransform: "uppercase", letterSpacing: "1px", fontWeight: 600 }}>Application Readiness Ring</div>
          <div style={{ display: "flex", alignItems: "center", gap: "2rem", flexWrap: "wrap" }}>
            <div style={{ position: "relative", width: "110px", height: "110px", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width="110" height="110" viewBox="0 0 110 110">
                <circle cx="55" cy="55" r="45" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
                <circle cx="55" cy="55" r="45" fill="none" stroke={overallReadiness > 85 ? "#7fe0a0" : "#ffd27a"} strokeWidth="8" 
                        strokeDasharray={2 * Math.PI * 45} 
                        strokeDashoffset={2 * Math.PI * 45 * (1 - overallReadiness / 100)} 
                        transform="rotate(-90 55 55)" style={{ transition: "stroke-dashoffset 0.5s ease" }} />
              </svg>
              <div style={{ position: "absolute", fontSize: "1.6rem", fontWeight: "bold", fontFamily: "var(--font-heading)", fontStyle: "italic" }}>{overallReadiness}%</div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", fontFamily: "var(--font-body)", fontSize: "0.95rem" }}>
              <div>Profile Data: <strong style={{ color: "#7fe0a0" }}>{profileCompletion}%</strong></div>
              <div>Required Documents: <strong style={{ color: currentHasCasteCert ? "#7fe0a0" : "#ffd27a" }}>{documentScore}%</strong></div>
              <div>Required Skills: <strong style={{ color: registeredCourse ? "#7fe0a0" : "#ffd27a" }}>{skillsScore}%</strong></div>
            </div>
          </div>

          {/* Free Scheme Fix */}
          <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-tile)", padding: "1rem", marginTop: "auto", display: "flex", flexDirection: "column", gap: "0.75rem", background: "rgba(255,255,255,0.04)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Icon name="spark" size={16} style={{ color: "#ffd27a" }} />
              <span style={{ fontSize: "0.9rem", fontWeight: 600 }}>AI Free Scheme Fix Upgrade</span>
            </div>
            {registeredCourse ? (
              <div style={{ fontSize: "0.85rem", color: "#7fe0a0", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <Icon name="check" size={14} /> Registered! Java Skill unlocked on profile.
              </div>
            ) : (
              <>
                <p style={{ margin: 0, fontSize: "0.82rem", opacity: 0.9, lineHeight: 1.35 }}>
                  You are missing the <strong>Java Programming</strong> skill required for the <strong>PMKVY Java Developer</strong> scheme. 
                </p>
                <Button onClick={() => setRegisteredCourse(true)} variant="white" size="sm" style={{ width: "fit-content" }}>⚡ Enroll Free Upgrade</Button>
              </>
            )}
          </div>
        </div>

        {/* Document Readiness Panel */}
        <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", color: "#fff", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ fontSize: "0.85rem", opacity: 0.8, textTransform: "uppercase", letterSpacing: "1px", fontWeight: 600 }}>Document Verification Wallet</div>
          
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", fontFamily: "var(--font-body)", fontSize: "0.95rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0.75rem", background: "rgba(127,224,160,0.1)", borderRadius: "var(--radius-tile)" }}>
              <span>Aadhaar Identity Card</span>
              <span style={{ color: "#7fe0a0", fontSize: "0.8rem", fontWeight: "bold" }}>✓ Verified</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0.75rem", background: "rgba(127,224,160,0.1)", borderRadius: "var(--radius-tile)" }}>
              <span>Graduation Certificate (B.Tech)</span>
              <span style={{ color: "#7fe0a0", fontSize: "0.8rem", fontWeight: "bold" }}>✓ Verified</span>
            </div>
            
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0.75rem", background: currentHasCasteCert ? "rgba(127,224,160,0.1)" : "rgba(255,210,122,0.1)", borderRadius: "var(--radius-tile)" }}>
              <span>Caste Certificate (OBC)</span>
              {currentHasCasteCert ? (
                <span style={{ color: "#7fe0a0", fontSize: "0.8rem", fontWeight: "bold" }}>✓ Verified</span>
              ) : (
                <div style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
                  <span style={{ color: "#ffd27a", fontSize: "0.8rem" }}>⚠ Missing</span>
                  <button onClick={() => setUploadedCasteCert(true)} style={{ border: "none", background: "rgba(255,255,255,0.2)", color: "#fff", borderRadius: "4px", padding: "2px 6px", fontSize: "0.75rem", cursor: "pointer" }}>Upload</button>
                </div>
              )}
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0.75rem", background: "rgba(255,255,255,0.06)", borderRadius: "var(--radius-tile)" }}>
              <span>Income Certificate</span>
              <div style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
                <span style={{ opacity: 0.6, fontSize: "0.8rem" }}>Optional</span>
              </div>
            </div>
          </div>
        </div>

        {/* Roadmap / Next Steps Card */}
        <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", color: "#fff", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ fontSize: "0.85rem", opacity: 0.8, textTransform: "uppercase", letterSpacing: "1px", fontWeight: 600 }}>Personalized Seeker Roadmap</div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem", fontFamily: "var(--font-body)", fontSize: "0.9rem" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "0.5rem", opacity: 0.6 }}>
              <Icon name="check" size={16} style={{ color: "#7fe0a0", marginTop: "2px" }} />
              <div>Complete profile registration (100%)</div>
            </div>
            
            <div style={{ display: "flex", alignItems: "flex-start", gap: "0.5rem", opacity: currentHasCasteCert ? 0.6 : 1 }}>
              <input type="checkbox" checked={currentHasCasteCert} readOnly style={{ marginTop: "3px" }} />
              <div>
                <strong>Obtain Caste Certificate</strong>
                <div style={{ fontSize: "0.75rem", opacity: 0.7 }}>Blocks RRB NTPC opportunity. Visit Tehsildar Office.</div>
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "flex-start", gap: "0.5rem", opacity: registeredCourse ? 0.6 : 1 }}>
              <input type="checkbox" checked={registeredCourse} readOnly style={{ marginTop: "3px" }} />
              <div>
                <strong>Complete Java Skill Fix Course</strong>
                <div style={{ fontSize: "0.75rem", opacity: 0.7 }}>Unlocks PMKVY Java Developer stipend value.</div>
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "flex-start", gap: "0.5rem" }}>
              <input type="checkbox" checked={false} disabled style={{ marginTop: "3px" }} />
              <div>
                <strong>Apply for SSC CGL 2026</strong>
                <div style={{ fontSize: "0.75rem", opacity: 0.7 }}>Registration closes 20 Jul 2026.</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Scam Shield and Verification Area */}
      <section>
        <SectionLabel>Scam Shield Guard</SectionLabel>
        <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", color: "#fff", marginTop: "1rem", display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: "2rem" }}>
          <div>
            <h4 style={{ margin: "0 0 0.5rem 0", fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "1.4rem" }}>Verify Job Post Authenticity</h4>
            <p style={{ margin: "0 0 1rem 0", fontSize: "0.85rem", opacity: 0.8, lineHeight: 1.4 }}>
              Paste a suspicious job description, contact message, or email below. The Scam Shield rule-engine will evaluate it for suspect signatures (such as mandatory refundable deposits or WhatsApp group recruitments).
            </p>
            <textarea value={scamText} onChange={(e) => setScamText(e.target.value)} placeholder="e.g. Earn Rs 5000 daily working from home! Join our Telegram group. Refundable security deposit of Rs 1500 mandatory for laptop dispatch." style={{ width: "100%", height: "90px", padding: "0.75rem", borderRadius: "8px", background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.2)", color: "#fff", outline: "none", fontFamily: "var(--font-body)", resize: "none" }} />
            <Button onClick={handleScamCheck} variant="white" size="sm" style={{ marginTop: "0.75rem" }}>Scan for Scams</Button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", borderLeft: "1px solid rgba(255,255,255,0.1)", paddingLeft: "1rem" }}>
            {scamResult ? (
              <div style={{ textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem" }}>
                <Icon name={scamResult.safe ? "check" : "alert"} size={42} style={{ color: scamResult.safe ? "#7fe0a0" : "#ff6b6b" }} />
                <h5 style={{ margin: 0, fontSize: "1.2rem", fontWeight: "bold", color: scamResult.safe ? "#7fe0a0" : "#ff6b6b" }}>{scamResult.level}</h5>
                <ul style={{ margin: 0, paddingLeft: "1rem", textAlign: "left", fontSize: "0.8rem", opacity: 0.9, display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                  {scamResult.reasons.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>
            ) : (
              <div style={{ textAlign: "center", opacity: 0.6 }}>
                <Icon name="shield" size={42} />
                <div style={{ fontSize: "0.85rem", marginTop: "0.5rem" }}>Shield Idle. Enter text to scan.</div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 5. Recommended & Match Feed Section */}
      <section>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
          <SectionLabel>Matched Opportunities & Priority Ranking</SectionLabel>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "0.85rem", color: "rgba(255,255,255,0.6)", fontFamily: "var(--font-body)" }}>Sort:</span>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} style={{ padding: "0.3rem 0.6rem", background: "rgba(255,255,255,0.1)", color: "#fff", border: "1px solid rgba(255,255,255,0.2)", borderRadius: "8px", fontFamily: "var(--font-body)", fontSize: "0.85rem" }}>
              <option value="priority" style={{ color: "#000" }}>Priority Index (Recommended)</option>
              <option value="reward" style={{ color: "#000" }}>Reward (Highest Benefit)</option>
              <option value="deadline" style={{ color: "#000" }}>Deadline (Soonest first)</option>
              <option value="readiness" style={{ color: "#000" }}>Readiness (Highest Match)</option>
            </select>
          </div>
        </div>

        <div style={{ marginTop: "1rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.25rem" }}>
          {sortedOpps.map((opp) => {
            const hasMissingSkills = opp.missingSkills && opp.missingSkills.length > 0;
            const hasMissingDocs = opp.missingDocs && opp.missingDocs.length > 0;
            const isReady = !hasMissingSkills && !hasMissingDocs;
            
            return (
              <div key={opp.id} className="liquid-glass udaan-lift" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", display: "flex", flexDirection: "column", gap: "0.9rem", minHeight: "220px", color: "#fff" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem" }}>
                  <Tag>{opp.tag}</Tag>
                  <div style={{ display: "flex", gap: "0.3rem", alignItems: "center" }}>
                    <span className="liquid-glass" style={{ padding: "0.2rem 0.5rem", borderRadius: "99px", fontSize: "0.75rem", color: isReady ? "#7fe0a0" : "#ffd27a", display: "inline-flex", alignItems: "center", gap: "0.2rem" }}>
                      <Icon name={isReady ? "check" : "alert"} size={12} style={{ color: isReady ? "#7fe0a0" : "#ffd27a" }} />
                      {opp.readiness}% Ready
                    </span>
                    {opp.isGovt && (
                      <span className="liquid-glass" style={{ padding: "0.2rem 0.5rem", borderRadius: "99px", fontSize: "0.75rem", color: "#8cc6ff", display: "inline-flex", alignItems: "center", gap: "0.2rem" }}>
                        Govt Official
                      </span>
                    )}
                  </div>
                </div>

                <div style={{ flex: 1 }}>
                  <h4 style={{ margin: 0, fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "1.35rem", lineHeight: 1.1 }}>{opp.name}</h4>
                  {/* Trust / Source Chips */}
                  <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", marginTop: "0.5rem", flexWrap: "wrap" }}>
                    {/* Source domain chip */}
                    <span style={{
                      display: "inline-flex", alignItems: "center", gap: "0.25rem",
                      padding: "0.15rem 0.55rem", borderRadius: "99px",
                      background: "rgba(255,255,255,0.08)",
                      border: "1px solid rgba(255,255,255,0.15)",
                      fontSize: "0.72rem", color: "rgba(255,255,255,0.75)"
                    }}>
                      <Icon name="globe" size={10} style={{ color: "rgba(255,255,255,0.55)" }} />
                      {opp.source}
                    </span>
                    {/* Trust score chip */}
                    <span style={{
                      display: "inline-flex", alignItems: "center", gap: "0.25rem",
                      padding: "0.15rem 0.55rem", borderRadius: "99px",
                      background: opp.trustScore >= 90 ? "rgba(127,224,160,0.15)" : opp.trustScore >= 70 ? "rgba(255,210,122,0.15)" : "rgba(255,107,107,0.15)",
                      border: `1px solid ${opp.trustScore >= 90 ? "rgba(127,224,160,0.4)" : opp.trustScore >= 70 ? "rgba(255,210,122,0.4)" : "rgba(255,107,107,0.4)"}`,
                      fontSize: "0.72rem",
                      color: opp.trustScore >= 90 ? "#7fe0a0" : opp.trustScore >= 70 ? "#ffd27a" : "#ff6b6b"
                    }}>
                      <Icon name="shield" size={10} style={{ color: opp.trustScore >= 90 ? "#7fe0a0" : opp.trustScore >= 70 ? "#ffd27a" : "#ff6b6b" }} />
                      Trust {opp.trustScore}%
                    </span>
                    {/* Official govt badge */}
                    {opp.isGovt && (
                      <span style={{
                        display: "inline-flex", alignItems: "center", gap: "0.2rem",
                        padding: "0.15rem 0.55rem", borderRadius: "99px",
                        background: "rgba(140,198,255,0.12)",
                        border: "1px solid rgba(140,198,255,0.35)",
                        fontSize: "0.72rem", color: "#8cc6ff"
                      }}>
                        🇮🇳 Official Govt
                      </span>
                    )}
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem", fontSize: "0.85rem" }}>
                  <div><strong style={{ opacity: 0.8 }}>Benefit:</strong> {opp.amount}</div>
                  <div><strong style={{ opacity: 0.8 }}>Deadline:</strong> {opp.deadline} ({opp.deadlineDays} days remaining)</div>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.5rem", marginTop: "0.5rem" }}>
                  <button onClick={() => setDecoderOpp(opp)} style={{ border: "none", background: "none", color: "#8cc6ff", cursor: "pointer", textDecoration: "underline", fontSize: "0.85rem", padding: 0 }}>Check Eligibility</button>
                  {isReady ? (
                    <Button variant="white" size="sm">Apply Now</Button>
                  ) : opp.upgradeAvailable ? (
                    <Button onClick={() => setRegisteredCourse(true)} variant="glass" size="sm">⚡ Enroll Free Fix</Button>
                  ) : (
                    <Button variant="ghost" size="sm" onClick={() => onAlertOpen()}>Resolve Blockers</Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 6. Eligibility Decoder Modal popup */}
      {decoderOpp && (
        <div style={{ position: "fixed", inset: 0, zIndex: 1000, background: "rgba(0,0,0,0.85)", display: "flex", alignItems: "center", justifyContent: "center", padding: "1.5rem" }}>
          <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "2rem", width: "100%", maxWidth: "550px", color: "#fff", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <Tag>{decoderOpp.tag}</Tag>
                <h3 style={{ margin: "0.5rem 0 0", fontSize: "1.8rem", fontFamily: "var(--font-heading)", fontStyle: "italic" }}>Eligibility Decoder</h3>
              </div>
              <button onClick={() => setDecoderOpp(null)} style={{ border: "none", background: "none", color: "#fff", fontSize: "1.5rem", cursor: "pointer" }}>×</button>
            </div>

            <div>
              <strong style={{ fontSize: "1.1rem" }}>{decoderOpp.name}</strong>
              <div style={{ fontSize: "0.85rem", opacity: 0.7, marginTop: "0.25rem" }}>Eligibility Match: {decoderOpp.readiness}%</div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "1rem", fontSize: "0.95rem" }}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: "0.6rem" }}>
                <Icon name="check" size={18} style={{ color: "#7fe0a0", marginTop: "2px" }} />
                <div>
                  <strong>Age & Category Rule</strong>
                  <div style={{ fontSize: "0.85rem", opacity: 0.85, marginTop: "0.15rem" }}>
                    Eligible. {decoderOpp.categoryAgeRelaxation || "Current age (23) satisfies limit requirement."}
                  </div>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "flex-start", gap: "0.6rem" }}>
                <Icon name="check" size={18} style={{ color: "#7fe0a0", marginTop: "2px" }} />
                <div>
                  <strong>Academic Profile Requirement</strong>
                  <div style={{ fontSize: "0.85rem", opacity: 0.85, marginTop: "0.15rem" }}>
                    Eligible. Your qualification ({profile.qualification}) meets the required standard.
                  </div>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "flex-start", gap: "0.6rem" }}>
                <Icon name={decoderOpp.missingSkills.length === 0 ? "check" : "alert"} size={18} style={{ color: decoderOpp.missingSkills.length === 0 ? "#7fe0a0" : "#ffd27a", marginTop: "2px" }} />
                <div>
                  <strong>Skills Matching</strong>
                  <div style={{ fontSize: "0.85rem", opacity: 0.85, marginTop: "0.15rem" }}>
                    {decoderOpp.missingSkills.length === 0 ? "Eligible. All mandatory skills verified." : `Missing skill: ${decoderOpp.missingSkills.join(", ")}`}
                  </div>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "flex-start", gap: "0.6rem" }}>
                <Icon name={decoderOpp.missingDocs.length === 0 ? "check" : "alert"} size={18} style={{ color: decoderOpp.missingDocs.length === 0 ? "#7fe0a0" : "#ffd27a", marginTop: "2px" }} />
                <div>
                  <strong>Documents Checklist</strong>
                  <div style={{ fontSize: "0.85rem", opacity: 0.85, marginTop: "0.15rem" }}>
                    {decoderOpp.missingDocs.length === 0 ? "Eligible. All documents verified." : `Missing document: ${decoderOpp.missingDocs.join(", ")}`}
                  </div>
                </div>
              </div>
            </div>

            <div style={{ background: "rgba(255,255,255,0.06)", padding: "1rem", borderRadius: "8px", fontSize: "0.85rem", lineHeight: 1.4 }}>
              <strong>AI Match Summary Reason:</strong> {decoderOpp.reasoning}
            </div>

            <Button onClick={() => setDecoderOpp(null)} variant="white" style={{ marginTop: "1rem" }}>Close</Button>
          </div>
        </div>
      )}

    </div>
  );
}

// ============================================================================
// ALERT CENTER DRAWER
// ============================================================================
function AlertCenterDrawer({ onClose, Icon, Button }) {
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 1100, display: "flex", justifyContent: "flex-end", animation: "fadein 0.2s" }}>
      <div onClick={onClose} style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.5)" }} />
      <div className="liquid-glass-strong" style={{ position: "relative", width: "100%", maxWidth: "380px", height: "100vh", padding: "2rem 1.5rem", color: "#fff", display: "flex", flexDirection: "column", gap: "1.5rem", boxShadow: "-4px 0 30px rgba(0,0,0,0.5)", overflowY: "auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ margin: 0, fontSize: "1.75rem", fontFamily: "var(--font-heading)", fontStyle: "italic" }}>Alert Center</h3>
          <button onClick={onClose} style={{ border: "none", background: "none", color: "#fff", fontSize: "1.5rem", cursor: "pointer" }}>×</button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", marginTop: "1rem" }}>
          
          <div className="liquid-glass" style={{ padding: "1rem", borderRadius: "var(--radius-card)", borderLeft: "4px solid #ff6b6b", background: "rgba(255,107,107,0.05)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "#ff6b6b", fontSize: "0.85rem", fontWeight: "bold" }}>
              <Icon name="alert" size={14} /> URGENT DEADLINE
            </div>
            <p style={{ margin: "0.4rem 0 0", fontSize: "0.88rem", lineHeight: 1.35 }}>
              <strong>RRB NTPC Clerk</strong> application deadline closes in 22 days (05 July). Upload your Caste Certificate to qualify.
            </p>
          </div>

          <div className="liquid-glass" style={{ padding: "1rem", borderRadius: "var(--radius-card)", borderLeft: "4px solid #ffd27a", background: "rgba(255,210,122,0.05)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "#ffd27a", fontSize: "0.85rem", fontWeight: "bold" }}>
              <Icon name="spark" size={14} /> FREE SKILL FIX RECOMMENDATION
            </div>
            <p style={{ margin: "0.4rem 0 0", fontSize: "0.88rem", lineHeight: 1.35 }}>
              Register for the free <strong>PMKVY Java Developer</strong> course by 15 July to unlock ₹8,000 stipend potential.
            </p>
          </div>

          <div className="liquid-glass" style={{ padding: "1rem", borderRadius: "var(--radius-card)", borderLeft: "4px solid #8cc6ff", background: "rgba(140,198,255,0.05)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "#8cc6ff", fontSize: "0.85rem", fontWeight: "bold" }}>
              <Icon name="bell" size={14} /> DOCUMENT REMINDER
            </div>
            <p style={{ margin: "0.4rem 0 0", fontSize: "0.88rem", lineHeight: 1.35 }}>
              Ensure your Aadhaar mobile link is active for verification matching across schemes.
            </p>
          </div>

        </div>

        <Button onClick={onClose} variant="white" style={{ marginTop: "auto" }}>Close alerts</Button>
      </div>
    </div>
  );
}

// ============================================================================
// VOICE CHAT DIALOG
// ============================================================================
function VoiceChatDialog({ onClose, Icon, Button }) {
  const [lang, setLang] = useState("en-IN");
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello Aanya! I am your UDAAN AI Coaching Agent. Tap the microphone to speak, or type a message about government jobs, scholarships, or training programs." }
  ]);
  const [isListening, setIsListening] = useState(false);
  const [statusText, setStatusText] = useState("");
  
  const recognitionRef = useRef(null);
  const synth = window.speechSynthesis;

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = true;

      rec.onstart = () => {
        setIsListening(true);
        setStatusText("Listening... Speak now!");
      };

      rec.onresult = (event) => {
        let text = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          text += event.results[i][0].transcript;
        }
        setInputText(text);
      };

      rec.onerror = (e) => {
        setIsListening(false);
        setStatusText("Microphone Error: " + e.error);
      };

      rec.onend = () => {
        setIsListening(false);
        setStatusText("");
      };

      recognitionRef.current = rec;
    }
  }, []);

  const startListening = () => {
    if (!recognitionRef.current) {
      alert("Microphone input is not supported in this browser. Please use Chrome.");
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      return;
    }
    synth.cancel();
    setInputText("");
    recognitionRef.current.lang = lang;
    try {
      recognitionRef.current.start();
    } catch(e) {}
  };

  const handleSend = () => {
    const query = inputText.trim();
    if (!query) return;

    const userMsg = { role: "user", text: query };
    setMessages(prev => [...prev, userMsg]);
    setInputText("");

    setTimeout(() => {
      let responseText = "I see. I am processing your query about job seeker schemes. You currently meet age limits and B.Tech criteria. I recommend completing the Java Upgrade course.";
      const q = query.toLowerCase();
      if (q.includes("ssc") || q.includes("job") || q.includes("cgl")) {
        responseText = "For SSC CGL 2026, you are 100% eligible. Your current age is 23 (limit is 30, plus 3 years OBC relaxation = 33). You can apply immediately.";
      } else if (q.includes("caste") || q.includes("certificate") || q.includes("rrb")) {
        responseText = "Your RRB NTPC opportunity requires a Caste Certificate. Once you upload it, your application readiness will rise to 100% for this job.";
      } else if (q.includes("scam") || q.includes("shield")) {
        responseText = "My Scam Shield scanner can protect you. Paste any job offer in the checker card below, and I will highlight suspicious processing or registration fees.";
      } else if (q.includes("free") || q.includes("pmkvy") || q.includes("java")) {
        responseText = "You can enroll in the Free PMKVY Java Developer Course directly on the dashboard. This will resolve the Java Skill gap and unlock your skilling stipend.";
      }

      setMessages(prev => [...prev, { role: "assistant", text: responseText }]);

      const utterance = new SpeechSynthesisUtterance(responseText);
      utterance.lang = lang.split("-")[0];
      synth.speak(utterance);
    }, 800);
  };

  return (
    <div style={{ position: "fixed", right: "20px", bottom: "100px", zIndex: 1200, width: "90%", maxWidth: "380px", display: "flex", flexDirection: "column", animation: "fadein 0.2s" }}>
      <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", display: "flex", flexDirection: "column", height: "480px", color: "#fff", boxShadow: "0 10px 40px rgba(0,0,0,0.6)", border: "1px solid rgba(255,255,255,0.15)" }}>
        
        {/* Chat Header */}
        <div style={{ padding: "1rem", borderBottom: "1px solid rgba(255,255,255,0.1)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Icon name="message" size={20} />
            <span style={{ fontWeight: 600, fontSize: "0.95rem" }}>UDAAN AI Seeker Coach</span>
          </div>
          <button onClick={onClose} style={{ border: "none", background: "none", color: "#fff", fontSize: "1.2rem", cursor: "pointer" }}>×</button>
        </div>

        {/* Languages Selector */}
        <div style={{ padding: "0.5rem 1rem", borderBottom: "1px solid rgba(255,255,255,0.06)", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.8rem" }}>
          <span>Speak language:</span>
          <select value={lang} onChange={(e) => setLang(e.target.value)} style={{ padding: "0.2rem", background: "rgba(0,0,0,0.5)", color: "#fff", border: "1px solid rgba(255,255,255,0.2)", borderRadius: "4px" }}>
            <option value="en-IN">English (India)</option>
            <option value="te-IN">Telugu (తెలుగు)</option>
            <option value="hi-IN">Hindi (हिंदी)</option>
          </select>
        </div>

        {/* Messages list */}
        <div style={{ flex: 1, padding: "1rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.75rem", fontSize: "0.88rem" }}>
          {messages.map((m, i) => (
            <div key={i} style={{ alignSelf: m.role === "user" ? "flex-end" : "flex-start", maxWidth: "80%", background: m.role === "user" ? "rgba(255,255,255,0.2)" : "rgba(255,255,255,0.08)", padding: "0.6rem 0.8rem", borderRadius: "10px", lineHeight: 1.35 }}>
              {m.text}
            </div>
          ))}
          {statusText && <div style={{ fontSize: "0.75rem", fontStyle: "italic", opacity: 0.8, color: "#ffd27a" }}>{statusText}</div>}
        </div>

        {/* Input box */}
        <div style={{ padding: "1rem", borderTop: "1px solid rgba(255,255,255,0.1)", display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <button onClick={startListening} style={{ width: "36px", height: "36px", borderRadius: "50%", background: isListening ? "#ff6b6b" : "rgba(255,255,255,0.15)", border: "none", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", animation: isListening ? "pulse 1s infinite" : "none" }}>
            <Icon name="mic" size={16} style={{ color: "#fff" }} />
          </button>
          <input type="text" value={inputText} onChange={(e) => setInputText(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSend()} placeholder="Ask about jobs, eligibility, scams..." style={{ flex: 1, padding: "0.5rem 0.75rem", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.2)", background: "rgba(255,255,255,0.05)", color: "#fff", outline: "none", fontSize: "0.88rem" }} />
          <button onClick={handleSend} style={{ border: "none", background: "#fff", color: "#000", padding: "0.5rem 0.85rem", borderRadius: "8px", fontSize: "0.85rem", fontWeight: "bold", cursor: "pointer" }}>Send</button>
        </div>

      </div>
    </div>
  );
}

window.UdaanDashboard = Dashboard;
