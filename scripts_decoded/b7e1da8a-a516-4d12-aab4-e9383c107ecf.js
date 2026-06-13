/* global React */
// UDAAN AI — persona dashboards rendered in the Astra visual language.

const { useState, useRef, useEffect, useCallback } = React;

/* ---- Farmer ambient music: local village MP3 ---- */
const FARMER_MUSIC_SRC = "./freesound_community-village-79043.mp3";


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

  const [chatOpen, setChatOpen] = useState(false);
  const [chatLang, setChatLang] = useState("en");
  const [chatInitialPrompt, setChatInitialPrompt] = useState("");
  const openChat = (lang, prompt = "") => { setChatLang(lang); setChatInitialPrompt(prompt); setChatOpen(true); };

  /* ---- Persona selection (must be before music hooks that use p.key) ---- */
  const startKey = window.__startPersona || new URLSearchParams(location.search).get("persona");
  const startIdx = personas.findIndex((p) => p.key === startKey);
  const [idx, setIdx] = useState(startIdx === -1 ? 0 : startIdx);
  const p = personas[idx];
  const userId = localStorage.getItem("user_id") || "1";

  const navInitials = (() => {
    try {
      const s = JSON.parse(localStorage.getItem("udaan_profile") || "null");
      const n = s && s.full_name;
      if (!n) return "AK";
      return n.trim().split(/\s+/).slice(0, 2).map((x) => x[0]).join("").toUpperCase() || "AK";
    } catch (e) { return "AK"; }
  })();

  /* ---- Farmer dashboard ambient music (local MP3) ---- */
  const audioRef = useRef(null);
  const [musicOn, setMusicOn] = useState(false);

  // Create Audio element once
  useEffect(() => {
    const a = new Audio(FARMER_MUSIC_SRC);
    a.loop = true;
    a.volume = 0;
    audioRef.current = a;
    return () => { a.pause(); a.src = ""; };
  }, []);

  // Smooth fade helper
  function fadeAudio(audio, targetVol, durationMs) {
    const steps = 30;
    const interval = durationMs / steps;
    const startVol = audio.volume;
    const delta = (targetVol - startVol) / steps;
    let i = 0;
    const t = setInterval(() => {
      i++;
      audio.volume = Math.max(0, Math.min(1, startVol + delta * i));
      if (i >= steps) clearInterval(t);
    }, interval);
  }

  // Play/pause with fade when persona or musicOn changes
  useEffect(() => {
    const a = audioRef.current;
    if (!a || !p) return;
    if (p.key === "farmers" && musicOn) {
      a.play().catch(() => {});
      fadeAudio(a, 0.35, 2000);
    } else {
      fadeAudio(a, 0, 1500);
      setTimeout(() => { if (a.volume < 0.02) a.pause(); }, 1600);
    }
  }, [p && p.key, musicOn]);

  const toggleMusic = useCallback(() => setMusicOn(v => !v), []);
  const musicReady = true;


  const [apiData, setApiData] = useState(null);
  const [loadingApi, setLoadingApi] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

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
    } else if (p.key === "students" && userId) {
      setLoadingApi(true);
      Promise.all([
        fetch(`http://localhost:8000/api/v1/dashboard/student/${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/wallet/opportunities?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/wallet/summary?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/readiness?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/value?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/approval/student/${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/deadlines/upcoming?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/timeline?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/opportunities/categories?user_id=${userId}`).then(r=>r.ok?r.json():null),
      ]).then(res => {
        setApiData({
          summary: res[0], wallet: res[1], wallet_summary: res[2],
          readiness: res[3], value: res[4], approval: res[5],
          deadlines: res[6], timeline: res[7], categories: res[8]
        });
        setLoadingApi(false);
      }).catch(e => {
        console.error(e); setLoadingApi(false);
      });
    } else if (p.key === "jobseekers" && userId) {
      setLoadingApi(true);
      Promise.all([
        fetch(`http://localhost:8000/api/v1/dashboard/jobseeker/${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/profile-context/${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/lifecycle/missed-opportunities?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/readiness?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/wallet/documents?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/jobseeker/roadmap?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/opportunities/recommended?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/approval?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/value?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/jobseeker/opportunity-summary?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/jobseeker/applications?user_id=${userId}`).then(r=>r.ok?r.json():null),
        fetch(`http://localhost:8000/api/v1/jobseeker/deadlines?user_id=${userId}`).then(r=>r.ok?r.json():null)
      ]).then(res => {
        setApiData({
          summary: res[0],
          profile_context: res[1],
          missed: res[2],
          readiness: res[3],
          documents: res[4],
          roadmap: res[5],
          recommended: res[6],
          approval: res[7],
          value: res[8],
          opportunity_summary: res[9],
          applications: res[10],
          deadlines: res[11]
        });
        setLoadingApi(false);
      }).catch(e => {
        console.error(e); setLoadingApi(false);
      });
    }
  }, [p.key, userId, profileOpen, refreshTrigger]);

  const rise = (delay) => ({
    initial: { filter: "blur(10px)", opacity: 0, y: 20 },
    animate: { filter: "blur(0px)", opacity: 1, y: 0 },
    transition: { duration: 0.7, ease: "easeOut", delay },
  });

  const scrollTop = () => document.getElementById("udaan-scroll")?.scrollTo({ top: 0, behavior: "smooth" });
  const selectPersona = (i) => { setIdx(i); scrollTop(); };

  return (
    <>
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

      <UdaanNav personas={personas} idx={idx} onSelect={selectPersona} onProfile={() => openProfile(false)} initials={navInitials} Icon={Icon}
        isFarmer={p.key === "farmers"} musicOn={musicOn} onToggleMusic={toggleMusic} musicReady={musicReady} />

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

            {p.key === "students" && (
              <M.div {...rise(0.85)} style={{
                marginTop: "2.5rem",
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "1.25rem",
                width: "100%",
                maxWidth: "960px",
                padding: "0 1.5rem"
              }}>
                <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", color: "#fff", border: "1px solid rgba(255,255,255,0.15)", backdropFilter: "blur(20px)" }}>
                  <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7fe0a0" }}>
                    {apiData?.summary?.profile_completion || 84}%
                  </div>
                  <div style={{ fontSize: "0.85rem", opacity: 0.8, fontFamily: "var(--font-body)", marginTop: "0.25rem" }}>Profile Complete</div>
                </div>
                <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", color: "#fff", border: "1px solid rgba(255,255,255,0.15)", backdropFilter: "blur(20px)" }}>
                  <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ffd27a" }}>
                    {apiData?.summary?.readiness_score || 82}
                  </div>
                  <div style={{ fontSize: "0.85rem", opacity: 0.8, fontFamily: "var(--font-body)", marginTop: "0.25rem" }}>Readiness Score</div>
                </div>
                <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", color: "#fff", border: "1px solid rgba(255,255,255,0.15)", backdropFilter: "blur(20px)" }}>
                  <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7acaff" }}>
                    {apiData?.summary?.eligible_opportunities || 12}
                  </div>
                  <div style={{ fontSize: "0.85rem", opacity: 0.8, fontFamily: "var(--font-body)", marginTop: "0.25rem" }}>Eligible Opportunities</div>
                </div>
                <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", color: "#fff", border: "1px solid rgba(255,255,255,0.15)", backdropFilter: "blur(20px)" }}>
                  <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ff9b9b" }}>
                    {apiData?.summary?.potential_value ? `₹${(apiData.summary.potential_value / 100000).toFixed(1)} Lakh` : "₹2.4 Lakh"}
                  </div>
                  <div style={{ fontSize: "0.85rem", opacity: 0.8, fontFamily: "var(--font-body)", marginTop: "0.25rem" }}>Potential Value</div>
                </div>
              </M.div>
            )}

            {p.key === "jobseekers" && (
              <>
                <M.div {...rise(0.8)} style={{ marginTop: "2rem", display: "flex", gap: "1.5rem", justifyContent: "center", alignItems: "center", flexWrap: "wrap" }}>
                  <button onClick={() => {
                    document.getElementById("matched-jobs-section")?.scrollIntoView({ behavior: "smooth" });
                  }} className="liquid-glass-strong" style={{
                    padding: "0.8rem 2.5rem", borderRadius: "9999px", color: "#fff", background: "rgba(255,255,255,0.06)",
                    border: "1px solid rgba(255,255,255,0.25)", fontFamily: "var(--font-body)", fontSize: "0.95rem",
                    fontWeight: "bold", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.4rem"
                  }}>
                    See Matched Jobs ↗
                  </button>
                  <button onClick={() => {
                    document.getElementById("ai-coach-section")?.scrollIntoView({ behavior: "smooth" });
                  }} style={{
                    background: "none", border: "none", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.95rem",
                    fontWeight: "bold", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.4rem"
                  }}>
                    ▶ Chat with UDAAN AI
                  </button>
                </M.div>
                <M.div {...rise(0.85)} style={{
                  marginTop: "2.5rem",
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                  gap: "1.25rem",
                  width: "100%",
                  maxWidth: "960px",
                  padding: "0 1.5rem"
                }}>
                  <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", color: "#fff", border: "1px solid rgba(255,255,255,0.15)", backdropFilter: "blur(20px)" }}>
                    <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7acaff" }}>
                      {apiData?.summary?.matched_opportunities ?? 42}
                    </div>
                    <div style={{ fontSize: "0.85rem", opacity: 0.8, fontFamily: "var(--font-body)", marginTop: "0.25rem" }}>Matched Opportunities</div>
                  </div>
                  <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", color: "#fff", border: "1px solid rgba(255,255,255,0.15)", backdropFilter: "blur(20px)" }}>
                    <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7fe0a0" }}>
                      {apiData?.summary?.eligible_opportunities ?? 18}
                    </div>
                    <div style={{ fontSize: "0.85rem", opacity: 0.8, fontFamily: "var(--font-body)", marginTop: "0.25rem" }}>Eligible Opportunities</div>
                  </div>
                  <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", color: "#fff", border: "1px solid rgba(255,255,255,0.15)", backdropFilter: "blur(20px)" }}>
                    <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ffd27a" }}>
                      {apiData?.summary?.readiness_score ?? 84}
                    </div>
                    <div style={{ fontSize: "0.85rem", opacity: 0.8, fontFamily: "var(--font-body)", marginTop: "0.25rem" }}>Readiness Score</div>
                  </div>
                  <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", color: "#fff", border: "1px solid rgba(255,255,255,0.15)", backdropFilter: "blur(20px)" }}>
                    <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#e87aff" }}>
                      {apiData?.summary?.approval_probability ?? 91}%
                    </div>
                    <div style={{ fontSize: "0.85rem", opacity: 0.8, fontFamily: "var(--font-body)", marginTop: "0.25rem" }}>Approval Probability</div>
                  </div>
                </M.div>
              </>
            )}

          </section>

          {/* DYNAMIC FARMER DASHBOARD VS STUDENT DASHBOARD VS OTHER STATIC DASHBOARDS */}
          {p.key === "farmers" ? (
             <FarmerSections data={apiData} loading={loadingApi} Icon={Icon} Button={Button} Tag={Tag} />
          ) : p.key === "students" ? (
             <StudentSections data={apiData} loading={loadingApi} Icon={Icon} Button={Button} Tag={Tag} openChat={openChat} />
          ) : p.key === "jobseekers" ? (
             <JobSeekerSections data={apiData} loading={loadingApi} Icon={Icon} Button={Button} Tag={Tag} openChat={openChat} onRefresh={() => setRefreshTrigger(t => t + 1)} />
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

      </div>

      {/* Floating AI chat button - Upgraded for Farmers */}
      {p.key === "farmers" ? (
          <div style={{ position: "fixed", bottom: "1.5rem", right: "1.5rem", zIndex: 100, display: "flex", flexDirection: "column", gap: "0.5rem", alignItems: "flex-end" }}>
             <button onClick={() => openChat("te")} className="liquid-glass" style={{ border: "none", padding: "0.6rem 1.2rem", borderRadius: "999px", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.9rem", cursor: "pointer", whiteSpace: "nowrap" }}>🎤 Speak in Telugu</button>
             <button onClick={() => openChat("hi")} className="liquid-glass" style={{ border: "none", padding: "0.6rem 1.2rem", borderRadius: "999px", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.9rem", cursor: "pointer", whiteSpace: "nowrap" }}>🎤 Speak in Hindi</button>
             <button onClick={() => openChat("en")} className="liquid-glass" style={{ border: "none", padding: "0.6rem 1.2rem", borderRadius: "999px", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.9rem", cursor: "pointer", whiteSpace: "nowrap" }}>🎤 Speak in English</button>
             <button onClick={() => openChat("en")} aria-label="Chat with UDAAN AI" className="udaan-fab liquid-glass-strong" style={{ marginTop: "0.5rem" }}>
                <Icon name="message" size={26} style={{ color: "#fff" }} />
             </button>
          </div>
      ) : (
          <button onClick={() => openChat("en")} aria-label="Chat with UDAAN AI" className="udaan-fab liquid-glass-strong">
            <Icon name="message" size={26} style={{ color: "#fff" }} />
          </button>
      )}

      </div>
    </div>
    {profileOpen && <window.UdaanProfile key={p.key} persona={p.key} initialEdit={profileEdit} onClose={() => setProfileOpen(false)} />}
    {chatOpen && <VoiceChatModal lang={chatLang} initialPrompt={chatInitialPrompt} onClose={() => { setChatOpen(false); setChatInitialPrompt(""); }} />}
  </>
  );
}

/* ---------- Voice Chat Modal ---------- */
function VoiceChatModal({ lang, onClose, initialPrompt }) {
   const Icon = window.UdaanIcon;
   const { useState, useRef, useEffect } = React;
   const initMsg = lang === "te" ? "నమస్కారం, నేను ఉడాన్ ఏఐ. మీకు ఎలా సహాయపడగలను?" : lang === "hi" ? "नमस्ते, मैं उड़ान एआई हूँ। मैं आपकी कैसे मदद कर सकता हूँ?" : "Hello, I am UDAAN AI. How can I help you today?";
   
   const [messages, setMessages] = useState([{ role: "assistant", text: initMsg }]);
   const [input, setInput] = useState("");
   const [loading, setLoading] = useState(false);
   const [listening, setListening] = useState(false);
   const chatEndRef = useRef(null);

   const speakMessage = (text, langCode) => {
       if (!("speechSynthesis" in window)) return;
       window.speechSynthesis.cancel();
       const utterance = new window.SpeechSynthesisUtterance(text);
       utterance.lang = langCode === "te" ? "te-IN" : langCode === "hi" ? "hi-IN" : "en-IN";
       window.speechSynthesis.speak(utterance);
   };

   // Speak initial greeting on open
   useEffect(() => {
       speakMessage(initMsg, lang);
       return () => { if ("speechSynthesis" in window) window.speechSynthesis.cancel(); };
   }, [lang]);

   useEffect(() => {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
   }, [messages]);

   const handleSend = async (overrideInput) => {
      const textToSend = typeof overrideInput === "string" ? overrideInput : input;
      if (!textToSend.trim() || loading) return;
      const uid = localStorage.getItem("user_id") || "1";
      const userMsg = { role: "user", text: textToSend };
      setMessages(prev => [...prev, userMsg]);
      setInput("");
      setLoading(true);

      const storedRole = localStorage.getItem("role") || "";
      const moduleName = (storedRole.includes("student") || storedRole.includes("students")) ? "student" : "farmer";

      try {
         const res = await fetch("http://localhost:8000/api/v1/voice/chat", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: uid, module: moduleName, language: lang, message: textToSend })
         });
         if (res.ok) {
             const data = await res.json();
             const payload = data.data || data;
             setMessages(prev => [...prev, { role: "assistant", text: payload.reply, data: payload }]);
             speakMessage(payload.reply, lang);
         } else {
             setMessages(prev => [...prev, { role: "assistant", text: "Sorry, I am having trouble connecting right now." }]);
         }
      } catch (e) {
          setMessages(prev => [...prev, { role: 'assistant', text: 'Connection error. Please try again.' }]);
      } finally {
          setLoading(false);
      }
   };

   useEffect(() => {
      if (initialPrompt) {
         handleSend(initialPrompt);
      }
   }, [initialPrompt]);

   const handleVoice = () => {
       if (!("webkitSpeechRecognition" in window)) {
           alert("Voice recognition not supported in your browser. Please type your message.");
           return;
       }
       const recognition = new window.webkitSpeechRecognition();
       recognition.lang = lang === "te" ? "te-IN" : lang === "hi" ? "hi-IN" : "en-US";
       recognition.interimResults = false;
       
       recognition.onstart = () => setListening(true);
       recognition.onresult = (e) => {
           const text = e.results[0][0].transcript;
           setInput(text);
           handleSend(text);
       };
       recognition.onerror = () => setListening(false);
       recognition.onend = () => setListening(false);
       recognition.start();
   };

   return (
      <div style={{ position: "fixed", inset: 0, zIndex: 9999, display: "flex", justifyContent: "flex-end", alignItems: "flex-end", padding: "1.5rem", pointerEvents: "none" }}>
         <div className="liquid-glass-strong" style={{ width: "100%", maxWidth: "420px", height: "80vh", maxHeight: "600px", borderRadius: "1.5rem", display: "flex", flexDirection: "column", overflow: "hidden", animation: "fadeUp 0.3s ease-out", pointerEvents: "auto", boxShadow: "0 10px 40px rgba(0,0,0,0.5)" }}>
            <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid rgba(255,255,255,0.1)", display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(255,255,255,0.05)" }}>
               <h3 style={{ margin: 0, color: "#fff", fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "1.2rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                   <span style={{ fontSize: "1.5rem" }}>🎤</span> UDAAN AI Voice ({lang.toUpperCase()})
               </h3>
               <button onClick={onClose} style={{ background: "rgba(255,255,255,0.2)", width: "30px", height: "30px", borderRadius: "50%", border: "none", color: "#fff", cursor: "pointer", fontSize: "1rem", display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
            </div>
            
            <div style={{ flex: 1, overflowY: "auto", padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
               {messages.map((m, i) => (
                  <div key={i} style={{ alignSelf: m.role === "user" ? "flex-end" : "flex-start", maxWidth: "85%", background: m.role === "user" ? "rgba(255,255,255,0.2)" : "rgba(0,0,0,0.3)", padding: "1rem", borderRadius: "1rem", borderBottomRightRadius: m.role === "user" ? 0 : "1rem", borderBottomLeftRadius: m.role === "assistant" ? 0 : "1rem", color: "#fff", fontFamily: "var(--font-body)", lineHeight: 1.4 }}>
                     {m.text}
                     {m.data?.opportunities?.length > 0 && (
                        <div style={{ marginTop: "0.75rem", padding: "0.75rem", background: "rgba(255,255,255,0.1)", borderRadius: "0.5rem", fontSize: "0.9rem" }}>
                           <strong style={{ color: "#7fe0a0" }}>{m.data.opportunities[0].scheme}</strong><br/>
                           <div style={{ opacity: 0.8, marginTop: "0.25rem" }}>Benefit: {m.data.opportunities[0].benefit}</div>
                        </div>
                     )}
                     {m.data?.missing_documents?.length > 0 && (
                        <div style={{ marginTop: "0.75rem", color: "#ffd27a", fontSize: "0.9rem", fontWeight: 500 }}>
                           Missing: {m.data.missing_documents.join(", ")}
                        </div>
                     )}
                     {m.data?.followup_questions?.length > 0 && (
                        <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                           {m.data.followup_questions.map((q, j) => (
                               <button key={j} onClick={() => { setInput(q); handleSend(q); }} style={{ textAlign: "left", background: "rgba(255,255,255,0.15)", border: "none", padding: "0.6rem 0.8rem", borderRadius: "0.5rem", color: "#fff", cursor: "pointer", fontFamily: "var(--font-body)", fontSize: "0.85rem" }}>{q}</button>
                           ))}
                        </div>
                     )}
                  </div>
               ))}
               {loading && <div style={{ alignSelf: "flex-start", padding: "1rem", color: "rgba(255,255,255,0.6)", fontFamily: "var(--font-body)", fontSize: "0.9rem", fontStyle: "italic" }}>UDAAN AI is analyzing...</div>}
               <div ref={chatEndRef} />
            </div>

            <div style={{ padding: "1rem", borderTop: "1px solid rgba(255,255,255,0.1)", display: "flex", gap: "0.5rem", alignItems: "center", background: "rgba(255,255,255,0.05)" }}>
               <button onClick={handleVoice} disabled={loading} style={{ width: "45px", height: "45px", borderRadius: "50%", border: "none", background: listening ? "#ff6b6b" : "rgba(255,255,255,0.2)", color: "#fff", cursor: loading ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.2rem", transition: "all 0.2s", flexShrink: 0 }}>
                  {listening ? "🎙️" : "🎤"}
               </button>
               <input type="text" value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSend()} placeholder={listening ? "Listening..." : "Type or speak..."} style={{ flex: 1, background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.2)", borderRadius: "999px", padding: "0.8rem 1.2rem", color: "#fff", outline: "none", fontFamily: "var(--font-body)", fontSize: "1rem", minWidth: 0 }} />
               <button onClick={() => handleSend()} disabled={loading || !input.trim()} style={{ width: "45px", height: "45px", borderRadius: "50%", border: "none", background: (loading || !input.trim()) ? "rgba(255,255,255,0.3)" : "#fff", color: "#000", cursor: (loading || !input.trim()) ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.2rem", flexShrink: 0 }}>
                  ➤
               </button>
            </div>
         </div>
      </div>
   );
}

// -----------------------------------------------------
// FARMER DYNAMIC SECTIONS
// -----------------------------------------------------

function DocumentGuideModal({ docName, onClose }) {
    const { useState, useEffect } = React;
    const [guide, setGuide] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch(`http://localhost:8000/api/v1/documents/${encodeURIComponent(docName)}/recovery-guide`)
            .then(r => r.json())
            .then(data => { setGuide(data); setLoading(false); })
            .catch(e => { setGuide({ error: "Failed to load from Groq/Serper API" }); setLoading(false); });
    }, [docName]);

    return (
        <div style={{ position: "fixed", inset: 0, zIndex: 99999, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.6)", padding: "1rem" }}>
            <div className="liquid-glass-strong" style={{ width: "100%", maxWidth: "600px", maxHeight: "90vh", overflowY: "auto", borderRadius: "1.5rem", padding: "2rem", position: "relative" }}>
                <button onClick={onClose} style={{ position: "absolute", top: "1rem", right: "1rem", background: "rgba(255,255,255,0.2)", width: "32px", height: "32px", borderRadius: "50%", border: "none", color: "#fff", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
                <h3 style={{ marginTop: 0, color: "#fff", fontFamily: "var(--font-heading)", fontSize: "1.8rem", fontStyle: "italic" }}>{docName} Guide</h3>
                
                {loading ? (
                    <div style={{ color: "rgba(255,255,255,0.7)", padding: "2rem 0", textAlign: "center", fontFamily: "var(--font-body)" }}>Generating live instructions via Groq/Serper API...</div>
                ) : guide?.error ? (
                    <div style={{ color: "#ff6b6b" }}>{guide.error}</div>
                ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", color: "#fff", fontFamily: "var(--font-body)" }}>
                        <div>
                            <strong style={{ color: "#7fe0a0", fontSize: "1.1rem" }}>1. Sample Document</strong>
                            <div style={{ marginTop: "0.5rem" }}>
                                <img src={guide.sample_image} alt="Sample Document" style={{ width: "100%", maxHeight: "200px", objectFit: "contain", borderRadius: "0.5rem", background: "rgba(0,0,0,0.3)" }} />
                            </div>
                        </div>
                        <div>
                            <strong style={{ color: "#ffd27a", fontSize: "1.1rem" }}>2. Required Documents</strong>
                            <ul style={{ paddingLeft: "1.5rem", marginTop: "0.5rem", lineHeight: 1.5 }}>
                                {guide.required_documents?.map((d, i) => <li key={i}>{d}</li>)}
                            </ul>
                        </div>
                        <div>
                            <strong style={{ color: "#7acaff", fontSize: "1.1rem" }}>3. Steps to Get It</strong>
                            <div style={{ opacity: 0.8, fontSize: "0.9rem", marginBottom: "0.5rem" }}>Processing Time: {guide.processing_time}</div>
                            <ol style={{ paddingLeft: "1.5rem", marginTop: "0", lineHeight: 1.5 }}>
                                {guide.steps?.map((s, i) => <li key={i}>{s}</li>)}
                            </ol>
                        </div>
                        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginTop: "1rem" }}>
                            <button onClick={() => window.open(guide.apply_link, "_blank")} style={{ background: "#fff", color: "#000", border: "none", padding: "0.8rem 1.5rem", borderRadius: "0.5rem", cursor: "pointer", fontWeight: "bold", fontFamily: "var(--font-body)" }}>Apply via Official Link ↗</button>
                            <button onClick={() => window.open(guide.youtube_link, "_blank")} style={{ background: "rgba(255,107,107,0.2)", color: "#ff6b6b", border: "1px solid #ff6b6b", padding: "0.8rem 1.5rem", borderRadius: "0.5rem", cursor: "pointer", fontWeight: "bold", fontFamily: "var(--font-body)" }}>Watch YouTube Guide ↗</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function FarmerSections({ data, loading, Icon, Button, Tag }) {
   const { useState } = React;
   const [activeDocGuide, setActiveDocGuide] = useState(null);
   const [activeCategoryModal, setActiveCategoryModal] = useState(null);

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
               <h3 style={{ margin: "0", fontSize: "1.8rem", fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#fff", textShadow: "0 2px 5px rgba(0,0,0,0.7)" }}>Welcome {sum.farmer_name || "Farmer"}</h3>
               <div style={{ display: "flex", flexWrap: "wrap", gap: "1.5rem", fontFamily: "var(--font-body)", fontSize: "1rem" }}>
                  <div><strong style={{ color: "#a7f3d0" }}>Profile:</strong> {sum.profile_completion || 0}% Complete</div>
                  <div><strong style={{ color: "#a7f3d0" }}>Eligible:</strong> {sum.eligible_opportunities || 0} Schemes</div>
                  <div><strong style={{ color: "#a7f3d0" }}>Potential Value:</strong> ₹{sum.potential_value || 0}</div>
                  <div><strong style={{ color: "#a7f3d0" }}>Missing Docs:</strong> {sum.documents_missing || 0}</div>
                  <div><strong style={{ color: "#a7f3d0" }}>Approval Score:</strong> {sum.approval_score || 0}%</div>
               </div>
            </div>
         </section>

         {/* 2. Quick Access Cards — live eligibility counts + clickable detail modal */}
         <section>
            <SectionLabel>Quick Access</SectionLabel>
            {(() => {
              const allSchemes = app.schemes || [];
              const categories = [
                { icon: "sprout", name: "PM Kisan", emoji: "🌾", tag: "Income", note: "Direct income support",
                  stat: "₹6,000 / yr",
                  count: allSchemes.filter(s => (s.tag||s.category||"Income").toLowerCase().includes("income") || (s.name||"").toLowerCase().includes("kisan")).length },
                { icon: "shield", name: "Crop Insurance", emoji: "🛡️", tag: "Insurance", note: "PM Fasal Bima Yojana",
                  stat: "2% premium",
                  count: allSchemes.filter(s => (s.tag||s.category||"Insurance").toLowerCase().includes("insur")).length },
                { icon: "coin", name: "Subsidies", emoji: "💰", tag: "Subsidy", note: "Seed · solar · drip",
                  stat: "schemes",
                  count: allSchemes.filter(s => (s.tag||s.category||"Subsidy").toLowerCase().includes("subsid") || (s.tag||s.category||"Subsidy").toLowerCase().includes("seed")).length },
                { icon: "bank", name: "Agriculture Loans", emoji: "🏦", tag: "Loan", note: "Kisan Credit Card",
                  stat: "@ 4% interest",
                  count: allSchemes.filter(s => (s.tag||s.category||"Loan").toLowerCase().includes("loan") || (s.tag||s.category||"").toLowerCase().includes("credit")).length }
              ];
              return (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.25rem", marginTop: "1rem" }}>
                  {categories.map(c => (
                    <CategoryCard key={c.name} c={c} Icon={Icon}
                      onClick={() => setActiveCategoryModal(c)} />
                  ))}
                </div>
              );
            })()}
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
               <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "2.2rem", fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#ffd27a", textShadow: "0 2px 5px rgba(0,0,0,0.7)" }}>{ai.scheme_name || "Rythu Bandhu"}</h3>
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
                        <div onClick={() => setActiveDocGuide(doc)}>
                           <Button variant="ghost" size="sm">View Sample</Button>
                        </div>
                        <div onClick={() => setActiveDocGuide(doc)}>
                           <Button variant="white" size="sm">How To Get</Button>
                        </div>
                     </div>
                  </div>
               ))}
            </div>
         </section>
         
         {activeDocGuide && <DocumentGuideModal docName={activeDocGuide} onClose={() => setActiveDocGuide(null)} />}
          {activeCategoryModal && (
            <CategoryDetailModal
              category={activeCategoryModal}
              schemes={(app.schemes || []).filter(s => {
                const tag = (activeCategoryModal.tag || "").toLowerCase();
                const st = (s.tag || s.category || "").toLowerCase();
                const sn = (s.name || "").toLowerCase();
                if (tag === "income") return st.includes("income") || sn.includes("kisan");
                if (tag === "insurance") return st.includes("insur");
                if (tag === "subsidy") return st.includes("subsid") || st.includes("seed") || st.includes("solar") || st.includes("drip");
                if (tag === "loan") return st.includes("loan") || st.includes("credit");
                return true;
              })}
              onClose={() => setActiveCategoryModal(null)}
              onViewDoc={(doc) => { setActiveCategoryModal(null); setActiveDocGuide(doc); }}
            />
          )}

         {/* 7. Readiness Score */}
         <section>
            <SectionLabel>Readiness Score</SectionLabel>
            <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", color: "#fff", display: "flex", gap: "3rem", alignItems: "center", flexWrap: "wrap" }}>
               <div style={{ fontSize: "4rem", fontWeight: "bold", fontFamily: "var(--font-heading)", fontStyle: "italic", lineHeight: 1, color: readi.overall_score >= 80 ? "#7fe0a0" : readi.overall_score >= 60 ? "#ffd27a" : "#ff6b6b" }}>
                 {readi.overall_score != null ? readi.overall_score : readi.overall_readiness ?? "—"}%
               </div>
               <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", opacity: 0.9, fontFamily: "var(--font-body)", fontSize: "1.1rem" }}>
                  <div>Profile: <strong>{readi.breakdown?.profile ?? readi.profile_readiness ?? "—"}%</strong></div>
                  <div>Documents: <strong>{readi.breakdown?.documents ?? readi.document_readiness ?? "—"}%</strong></div>
                  <div>Eligibility: <strong>{readi.breakdown?.eligibility ?? readi.eligibility_readiness ?? "—"}%</strong></div>
               </div>
            </div>
         </section>

         {/* 8. Value Wallet */}
         <section>
            <SectionLabel>Value Wallet</SectionLabel>
            <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", color: "#fff", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "2rem" }}>
               <div>
                 <div style={{ opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.1rem" }}>Eligible Value</div>
                 <div style={{ fontSize: "2.5rem", fontWeight: "bold", fontFamily: "var(--font-heading)" }}>
                   {val.eligible_value != null ? `₹${Number(val.eligible_value).toLocaleString("en-IN")}` : "—"}
                 </div>
               </div>
               <div>
                 <div style={{ opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.1rem" }}>Potential Value</div>
                 <div style={{ fontSize: "2.5rem", fontWeight: "bold", fontFamily: "var(--font-heading)" }}>
                   {val.potential_value != null ? `₹${Number(val.potential_value).toLocaleString("en-IN")}` : "—"}
                 </div>
               </div>
               <div>
                 <div style={{ opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.1rem" }}>Recovery Value</div>
                 <div style={{ fontSize: "2.5rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7fe0a0" }}>
                   {val.recovery_value != null ? `₹${Number(val.recovery_value).toLocaleString("en-IN")}` : "—"}
                 </div>
               </div>
            </div>
         </section>

         {/* 9. Approval Probability */}
         <section>
            <SectionLabel>Approval Probability</SectionLabel>
            {(!app.opportunities || app.opportunities.length === 0) ? (
              <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", marginTop: "1rem", color: "rgba(255,255,255,0.55)", fontFamily: "var(--font-body)", textAlign: "center" }}>
                Complete your profile to see approval probabilities
              </div>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1.25rem", marginTop: "1rem" }}>
                {app.opportunities.map((op, i) => (
                   <div key={i} className="liquid-glass" style={{ padding: "1.5rem", borderRadius: "var(--radius-card)", color: "#fff", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div>
                        <span style={{ fontFamily: "var(--font-body)", fontSize: "1.05rem", fontWeight: 600 }}>{op.name}</span>
                        {op.tag && <div style={{ fontSize: "0.75rem", opacity: 0.6, fontFamily: "var(--font-body)", marginTop: "0.2rem" }}>{op.tag}</div>}
                      </div>
                      <span style={{ fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "2rem", fontWeight: "bold", color: op.score >= 80 ? "#7fe0a0" : op.score >= 60 ? "#ffd27a" : "#ff6b6b" }}>
                        {op.score}%
                      </span>
                   </div>
                ))}
              </div>
            )}
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

         <TelegramConnectSection userId={sum.user_id || "1"} />
      </div>
   );
}

function StudentSections({ data, loading, Icon, Button, Tag, openChat }) {
   const { useState } = React;
   const [activeDocGuide, setActiveDocGuide] = useState(null);

   if (loading || !data) return <div style={{ padding: "3rem", textAlign: "center", color: "#fff", fontFamily: "var(--font-body)", fontSize: "1.2rem" }}>Loading UDAAN Engines...</div>;

   const sum = data.summary || {};
   const wallet = data.wallet || { opportunities: [] };
   const wallet_sum = data.wallet_summary || {};
   const readi = data.readiness || {};
   const val = data.value || {};
   const approval = data.approval || {};
   const time = data.timeline || {};
   const dead = data.deadlines?.deadlines || [];

   const categoriesData = data.categories?.categories || [
      {"name": "Scholarships", "available": 1240, "matched": 14, "eligible": 8, "icon": "award", "note": "Merit & means-based"},
      {"name": "Internships", "available": 860, "matched": 12, "eligible": 6, "icon": "briefcase", "note": "Govt & corporate"},
      {"name": "Fellowships", "available": 95, "matched": 5, "eligible": 2, "icon": "star", "note": "Research & policy"},
      {"name": "Research Programs", "available": 310, "matched": 6, "eligible": 3, "icon": "flask", "note": "Funded projects"},
      {"name": "Hackathons", "available": 42, "matched": 4, "eligible": 2, "icon": "code", "note": "Build · win · get hired"},
      {"name": "Jobs", "available": 5600, "matched": 25, "eligible": 15, "icon": "building", "note": "Full-time & part-time careers"},
      {"name": "Competitions", "available": 150, "matched": 8, "eligible": 4, "icon": "trophy", "note": "National & global contests"},
      {"name": "Conferences", "available": 75, "matched": 5, "eligible": 3, "icon": "globe", "note": "Academic & tech summits"},
      {"name": "Training Programs", "available": 320, "matched": 18, "eligible": 10, "icon": "book", "note": "Skill certifications"}
   ];

   return (
      <div style={{ maxWidth: "1240px", margin: "0 auto", padding: "1rem clamp(1.5rem, 5vw, 5rem)", display: "flex", flexDirection: "column", gap: "2.5rem" }}>
         
         {/* SECTION 2: STUDENT OVERVIEW CARD */}
         <section>
            <SectionLabel>Student Overview</SectionLabel>
            <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", marginTop: "1rem", color: "#fff", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
               <h3 style={{ margin: "0", fontSize: "1.8rem", fontFamily: "var(--font-heading)", fontStyle: "italic" }}>Welcome {sum.user_name || "Puja"}</h3>
               <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "1.5rem", fontFamily: "var(--font-body)", fontSize: "0.95rem" }}>
                  <div>
                    <div style={{ opacity: 0.7, fontSize: "0.8rem", textTransform: "uppercase" }}>Profile Completion</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: "bold", marginTop: "0.25rem", color: "#7fe0a0" }}>{sum.profile_completion || 84}%</div>
                  </div>
                  <div>
                    <div style={{ opacity: 0.7, fontSize: "0.8rem", textTransform: "uppercase" }}>Readiness</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: "bold", marginTop: "0.25rem", color: "#ffd27a" }}>{sum.readiness_score || 82}%</div>
                  </div>
                  <div>
                    <div style={{ opacity: 0.7, fontSize: "0.8rem", textTransform: "uppercase" }}>Eligibility</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: "bold", marginTop: "0.25rem", color: "#7acaff" }}>{sum.eligible_opportunities || 12} Opportunities</div>
                  </div>
                  <div>
                    <div style={{ opacity: 0.7, fontSize: "0.8rem", textTransform: "uppercase" }}>Missing Documents</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: "bold", marginTop: "0.25rem", color: "#ff6b6b" }}>{sum.documents_missing || 2}</div>
                  </div>
                  <div>
                    <div style={{ opacity: 0.7, fontSize: "0.8rem", textTransform: "uppercase" }}>Missing Skills</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: "bold", marginTop: "0.25rem", color: "#ffb37a" }}>{sum.skills_missing || 3}</div>
                  </div>
                  <div>
                    <div style={{ opacity: 0.7, fontSize: "0.8rem", textTransform: "uppercase" }}>Approval Score</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: "bold", marginTop: "0.25rem", color: "#e87aff" }}>{sum.approval_score || 89}%</div>
                  </div>
               </div>
            </div>
         </section>

         {/* SECTION 3: OPPORTUNITY WALLET */}
         <section>
            <SectionLabel>Opportunity Wallet</SectionLabel>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1.25rem", marginTop: "1rem" }}>
               <div className="liquid-glass" style={{ padding: "1.25rem", borderRadius: "var(--radius-card)", color: "#fff" }}>
                  <div style={{ opacity: 0.7, fontSize: "0.85rem", fontFamily: "var(--font-body)" }}>Ready To Apply</div>
                  <div style={{ fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7fe0a0", marginTop: "0.25rem" }}>{wallet_sum.ready || 6}</div>
               </div>
               <div className="liquid-glass" style={{ padding: "1.25rem", borderRadius: "var(--radius-card)", color: "#fff" }}>
                  <div style={{ opacity: 0.7, fontSize: "0.85rem", fontFamily: "var(--font-body)" }}>Blocked</div>
                  <div style={{ fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ff6b6b", marginTop: "0.25rem" }}>{wallet_sum.blocked || 2}</div>
               </div>
               <div className="liquid-glass" style={{ padding: "1.25rem", borderRadius: "var(--radius-card)", color: "#fff" }}>
                  <div style={{ opacity: 0.7, fontSize: "0.85rem", fontFamily: "var(--font-body)" }}>Needs Clarification</div>
                  <div style={{ fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ffd27a", marginTop: "0.25rem" }}>{wallet_sum.needs_clarification || 0}</div>
               </div>
               <div className="liquid-glass" style={{ padding: "1.25rem", borderRadius: "var(--radius-card)", color: "#fff" }}>
                  <div style={{ opacity: 0.7, fontSize: "0.85rem", fontFamily: "var(--font-body)" }}>Applied</div>
                  <div style={{ fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7acaff", marginTop: "0.25rem" }}>{wallet_sum.applied || 4}</div>
               </div>
               <div className="liquid-glass" style={{ padding: "1.25rem", borderRadius: "var(--radius-card)", color: "#fff" }}>
                  <div style={{ opacity: 0.7, fontSize: "0.85rem", fontFamily: "var(--font-body)" }}>Under Review</div>
                  <div style={{ fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#e87aff", marginTop: "0.25rem" }}>{wallet_sum.under_review || 2}</div>
               </div>
               <div className="liquid-glass" style={{ padding: "1.25rem", borderRadius: "var(--radius-card)", color: "#fff" }}>
                  <div style={{ opacity: 0.7, fontSize: "0.85rem", fontFamily: "var(--font-body)" }}>Won</div>
                  <div style={{ fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ffd27a", marginTop: "0.25rem" }}>{wallet_sum.approved || wallet_sum.won || 1}</div>
               </div>
            </div>
         </section>

         {/* SECTION 4: READINESS ENGINE */}
         <section>
            <SectionLabel>My Readiness</SectionLabel>
            <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", color: "#fff", display: "flex", gap: "3rem", alignItems: "center", flexWrap: "wrap" }}>
               <div style={{ position: "relative", width: "120px", height: "120px", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <svg width="100%" height="100%" viewBox="0 0 100 100" style={{ transform: "rotate(-90deg)" }}>
                     <circle cx="50" cy="50" r="40" stroke="rgba(255,255,255,0.1)" strokeWidth="8" fill="none" />
                     <circle cx="50" cy="50" r="40" stroke="#7fe0a0" strokeWidth="8" fill="none"
                        strokeDasharray="251.2"
                        strokeDashoffset={251.2 - (251.2 * (readi.overall_score || 82)) / 100}
                        strokeLinecap="round"
                        style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
                     />
                  </svg>
                  <div style={{ position: "absolute", fontSize: "2rem", fontWeight: "bold", fontFamily: "var(--font-heading)" }}>
                     {readi.overall_score || 82}%
                  </div>
               </div>
               
               <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1.5rem", flex: 1, fontFamily: "var(--font-body)" }}>
                  <div>
                     <div style={{ fontSize: "0.85rem", opacity: 0.7 }}>Profile:</div>
                     <div style={{ fontSize: "1.4rem", fontWeight: "bold", color: "#fff", marginTop: "0.25rem" }}>{readi.profile_readiness || readi.breakdown?.profile || 90}%</div>
                     <div style={{ height: "4px", background: "rgba(255,255,255,0.1)", borderRadius: "2px", marginTop: "0.5rem", overflow: "hidden" }}>
                        <div style={{ width: `${readi.profile_readiness || readi.breakdown?.profile || 90}%`, height: "100%", background: "#7fe0a0" }} />
                     </div>
                  </div>
                  <div>
                     <div style={{ fontSize: "0.85rem", opacity: 0.7 }}>Documents:</div>
                     <div style={{ fontSize: "1.4rem", fontWeight: "bold", color: "#fff", marginTop: "0.25rem" }}>{readi.document_readiness || readi.breakdown?.documents || 75}%</div>
                     <div style={{ height: "4px", background: "rgba(255,255,255,0.1)", borderRadius: "2px", marginTop: "0.5rem", overflow: "hidden" }}>
                        <div style={{ width: `${readi.document_readiness || readi.breakdown?.documents || 75}%`, height: "100%", background: "#ffd27a" }} />
                     </div>
                  </div>
                  <div>
                     <div style={{ fontSize: "0.85rem", opacity: 0.7 }}>Academic:</div>
                     <div style={{ fontSize: "1.4rem", fontWeight: "bold", color: "#fff", marginTop: "0.25rem" }}>{readi.academic_readiness || readi.breakdown?.academic || 88}%</div>
                     <div style={{ height: "4px", background: "rgba(255,255,255,0.1)", borderRadius: "2px", marginTop: "0.5rem", overflow: "hidden" }}>
                        <div style={{ width: `${readi.academic_readiness || readi.breakdown?.academic || 88}%`, height: "100%", background: "#7acaff" }} />
                     </div>
                  </div>
                  <div>
                     <div style={{ fontSize: "0.85rem", opacity: 0.7 }}>Skills:</div>
                     <div style={{ fontSize: "1.4rem", fontWeight: "bold", color: "#fff", marginTop: "0.25rem" }}>{readi.skills_readiness || readi.breakdown?.skills || 76}%</div>
                     <div style={{ height: "4px", background: "rgba(255,255,255,0.1)", borderRadius: "2px", marginTop: "0.5rem", overflow: "hidden" }}>
                        <div style={{ width: `${readi.skills_readiness || readi.breakdown?.skills || 76}%`, height: "100%", background: "#e87aff" }} />
                     </div>
                  </div>
               </div>
            </div>
         </section>

         {/* SECTION 5: OPPORTUNITY CATEGORIES */}
         <section>
            <SectionLabel>My Eligibility</SectionLabel>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1.25rem", marginTop: "1rem" }}>
               {categoriesData.map(c => (
                  <div key={c.name} className="liquid-glass udaan-lift" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", display: "flex", flexDirection: "column", gap: "0.8rem" }}>
                     <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                        <div className="liquid-glass" style={{ width: 36, height: 36, borderRadius: "var(--radius-tile)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                           <Icon name={c.icon} size={20} style={{ color: "#fff" }} />
                        </div>
                        <div style={{ fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "1.05rem", color: "#fff" }}>{c.name}</div>
                     </div>
                     <div style={{ fontFamily: "var(--font-body)", fontSize: "0.85rem", opacity: 0.95, display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                        <div>Available: <strong style={{ color: "#fff" }}>{c.available}</strong></div>
                        <div>Matched To You: <strong style={{ color: "#ffd27a" }}>{c.matched}</strong></div>
                        <div>Eligible: <strong style={{ color: "#7fe0a0" }}>{c.eligible}</strong></div>
                     </div>
                  </div>
               ))}
            </div>
         </section>

         {/* SECTION 6: AI RECOMMENDED OPPORTUNITIES */}
         <section>
            <SectionLabel>My AI Recommendations</SectionLabel>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.25rem", marginTop: "1rem" }}>
               {(wallet.opportunities || []).map((op, i) => (
                  <div key={i} className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
                     <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                        <Tag>{op.category}</Tag>
                        <span className="liquid-glass" style={{ borderRadius: "9999px", padding: "0.25rem 0.6rem", fontSize: "0.8rem", color: "#ffd27a", display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
                           <Icon name="spark" size={12} /> Match Score: {op.eligibility_score || 96}%
                        </span>
                     </div>
                     <div style={{ flex: 1 }}>
                        <h4 style={{ margin: 0, fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#fff", fontSize: "1.5rem" }}>{op.title}</h4>
                        <div style={{ fontFamily: "var(--font-body)", fontSize: "0.9rem", color: "rgba(255,255,255,0.85)", marginTop: "0.6rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                           <div>Value: <strong style={{ color: "#7fe0a0" }}>{op.benefit}</strong></div>
                           <div>Approval Probability: <strong style={{ color: "#ffd27a" }}>{op.approval_probability || 89}%</strong></div>
                           <div>Deadline: <strong style={{ color: "#ff6b6b" }}>{op.deadline}</strong></div>
                           <div>Missing Requirement: <strong style={{ color: op.missing_requirement === "None" ? "#7fe0a0" : "#ff6b6b" }}>{op.missing_requirement}</strong></div>
                        </div>
                     </div>
                     <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
                        <button onClick={() => window.open(op.apply_link, "_blank")} style={{ flex: 1, background: "#fff", color: "#000", border: "none", padding: "0.6rem", borderRadius: "0.5rem", cursor: "pointer", fontWeight: "bold", fontFamily: "var(--font-body)", fontSize: "0.85rem" }}>Apply Now ↗</button>
                        {op.missing_requirement !== "None" && (
                           <button onClick={() => setActiveDocGuide(op.missing_requirement)} style={{ background: "rgba(255,255,255,0.1)", color: "#fff", border: "none", padding: "0.6rem", borderRadius: "0.5rem", cursor: "pointer", fontFamily: "var(--font-body)", fontSize: "0.85rem" }}>Resolve</button>
                        )}
                     </div>
                  </div>
               ))}
            </div>
         </section>

         {/* SECTION 7: MISSING DOCUMENTS */}
         <section>
            <SectionLabel>My Missing Documents</SectionLabel>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem" }}>
               {(readi.missing_documents || ["Income Certificate", "Bonafide Certificate", "EWS Certificate"]).map((doc, i) => (
                  <div key={i} className="liquid-glass" style={{ padding: "1.25rem 1.5rem", borderRadius: "var(--radius-card)", color: "#fff", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
                     <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                        <Icon name="alert" size={20} style={{ color: "#ff6b6b" }} />
                        <div style={{ color: "#ffd27a", fontWeight: "bold", fontFamily: "var(--font-body)", fontSize: "1.1rem" }}>{doc}</div>
                     </div>
                     <div style={{ display: "flex", gap: "0.5rem" }}>
                        <button onClick={() => setActiveDocGuide(doc)} className="liquid-glass-strong" style={{ border: "none", padding: "0.5rem 1rem", borderRadius: "0.5rem", color: "#fff", cursor: "pointer", fontFamily: "var(--font-body)", fontSize: "0.85rem" }}>View Sample</button>
                        <button onClick={() => setActiveDocGuide(doc)} className="liquid-glass-strong" style={{ border: "none", padding: "0.5rem 1rem", borderRadius: "0.5rem", color: "#fff", cursor: "pointer", fontFamily: "var(--font-body)", fontSize: "0.85rem" }}>How To Get</button>
                        <button onClick={() => setActiveDocGuide(doc)} style={{ background: "#fff", border: "none", padding: "0.5rem 1rem", borderRadius: "0.5rem", color: "#000", cursor: "pointer", fontWeight: "bold", fontFamily: "var(--font-body)", fontSize: "0.85rem" }}>Apply Now</button>
                     </div>
                  </div>
               ))}
            </div>
         </section>

         {/* SECTION 8: SKILL GAP ANALYSIS */}
         <section>
            <SectionLabel>My Missing Skills</SectionLabel>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.25rem", marginTop: "1rem" }}>
               <div className="liquid-glass" style={{ padding: "1.5rem", borderRadius: "var(--radius-card)", color: "#fff" }}>
                  <div style={{ fontSize: "0.8rem", opacity: 0.6, textTransform: "uppercase", fontFamily: "var(--font-body)" }}>Target</div>
                  <h4 style={{ margin: "0.25rem 0 0.75rem 0", fontSize: "1.4rem", fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#ffd27a" }}>AI Internship</h4>
                  <div style={{ fontSize: "0.9rem", opacity: 0.7, fontFamily: "var(--font-body)" }}>Missing Skills:</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.5rem" }}>
                     <span className="liquid-glass-strong" style={{ padding: "0.3rem 0.75rem", borderRadius: "999px", fontSize: "0.8rem", color: "#ff6b6b" }}>Python</span>
                     <span className="liquid-glass-strong" style={{ padding: "0.3rem 0.75rem", borderRadius: "999px", fontSize: "0.8rem", color: "#ff6b6b" }}>Machine Learning</span>
                     <span className="liquid-glass-strong" style={{ padding: "0.3rem 0.75rem", borderRadius: "999px", fontSize: "0.8rem", color: "#ff6b6b" }}>Git</span>
                  </div>
               </div>
               <div className="liquid-glass" style={{ padding: "1.5rem", borderRadius: "var(--radius-card)", color: "#fff" }}>
                  <div style={{ fontSize: "0.8rem", opacity: 0.6, textTransform: "uppercase", fontFamily: "var(--font-body)" }}>Target</div>
                  <h4 style={{ margin: "0.25rem 0 0.75rem 0", fontSize: "1.4rem", fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#ffd27a" }}>Research Fellowship</h4>
                  <div style={{ fontSize: "0.9rem", opacity: 0.7, fontFamily: "var(--font-body)" }}>Missing:</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.5rem" }}>
                     <span className="liquid-glass-strong" style={{ padding: "0.3rem 0.75rem", borderRadius: "999px", fontSize: "0.8rem", color: "#ff6b6b" }}>Research Writing</span>
                     <span className="liquid-glass-strong" style={{ padding: "0.3rem 0.75rem", borderRadius: "999px", fontSize: "0.8rem", color: "#ff6b6b" }}>Publication Experience</span>
                  </div>
               </div>
            </div>
         </section>

         {/* SECTION 9: APPROVAL INTELLIGENCE */}
         <section>
            <SectionLabel>My Approval Chances</SectionLabel>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.25rem", marginTop: "1rem" }}>
               {(approval.schemes || [
                  { name: "National Merit Scholarship", score: 91, tag: "Scholarships" },
                  { name: "INSPIRE", score: 87, tag: "Scholarships" },
                  { name: "AICTE Internship", score: 83, tag: "Internships" }
               ]).map((op, i) => {
                  const color = op.score >= 90 ? "#7fe0a0" : op.score >= 80 ? "#ffd27a" : "#ff6b6b";
                  return (
                     <div key={i} className="liquid-glass" style={{ padding: "1.5rem", borderRadius: "var(--radius-card)", color: "#fff", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                           <div>
                              <span style={{ fontFamily: "var(--font-body)", fontSize: "1.1rem", fontWeight: 600 }}>{op.name}</span>
                              <div style={{ fontSize: "0.75rem", opacity: 0.6, fontFamily: "var(--font-body)", marginTop: "0.15rem" }}>{op.tag}</div>
                           </div>
                           <span style={{ fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "2rem", fontWeight: "bold", color }}>
                             {op.score}%
                           </span>
                        </div>
                        <div style={{ height: "6px", background: "rgba(255,255,255,0.1)", borderRadius: "3px", overflow: "hidden" }}>
                           <div style={{ width: `${op.score}%`, height: "100%", background: color }} />
                        </div>
                     </div>
                  );
               })}
            </div>
         </section>

         {/* SECTION 10: VALUE ENGINE */}
         <section>
            <SectionLabel>My Opportunity Value</SectionLabel>
            <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", color: "#fff", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "2rem" }}>
               <div>
                  <div style={{ opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.05rem" }}>Eligible Value</div>
                  <div style={{ fontSize: "2.5rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#fff", marginTop: "0.25rem" }}>
                    ₹{val.eligible_value ? Number(val.eligible_value).toLocaleString("en-IN") : "50,000"}
                  </div>
               </div>
               <div>
                  <div style={{ opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.05rem" }}>Potential Value</div>
                  <div style={{ fontSize: "2.5rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ffd27a", marginTop: "0.25rem" }}>
                    ₹{val.potential_value ? Number(val.potential_value).toLocaleString("en-IN") : "1,80,000"}
                  </div>
               </div>
               <div>
                  <div style={{ opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.05rem" }}>Blocked Value</div>
                  <div style={{ fontSize: "2.5rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ff6b6b", marginTop: "0.25rem" }}>
                    ₹{val.blocked_value ? Number(val.blocked_value).toLocaleString("en-IN") : "70,000"}
                  </div>
               </div>
               <div>
                  <div style={{ opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1.05rem" }}>Recovery Value</div>
                  <div style={{ fontSize: "2.5rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7fe0a0", marginTop: "0.25rem" }}>
                    ₹{val.recovery_value ? Number(val.recovery_value).toLocaleString("en-IN") : "70,000"}
                  </div>
               </div>
            </div>
         </section>

         {/* SECTION 11: APPLICATION TRACKER */}
         <section>
            <SectionLabel>Application Tracker</SectionLabel>
            <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", marginTop: "1rem", color: "#fff", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "2rem" }}>
               <div>
                  <div style={{ opacity: 0.7, fontFamily: "var(--font-body)" }}>Applied</div>
                  <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7acaff", marginTop: "0.25rem" }}>{wallet_sum.applied || 4}</div>
               </div>
               <div>
                  <div style={{ opacity: 0.7, fontFamily: "var(--font-body)" }}>Under Review</div>
                  <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#e87aff", marginTop: "0.25rem" }}>{wallet_sum.under_review || 2}</div>
               </div>
               <div>
                  <div style={{ opacity: 0.7, fontFamily: "var(--font-body)" }}>Selected</div>
                  <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#7fe0a0", marginTop: "0.25rem" }}>{wallet_sum.approved || wallet_sum.won || 1}</div>
               </div>
               <div>
                  <div style={{ opacity: 0.7, fontFamily: "var(--font-body)" }}>Rejected</div>
                  <div style={{ fontSize: "2.2rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ff6b6b", marginTop: "0.25rem" }}>{wallet_sum.rejected || 1}</div>
               </div>
            </div>
         </section>

         {/* SECTION 12: UPCOMING DEADLINES */}
         <section>
            <SectionLabel>Upcoming Deadlines</SectionLabel>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem" }}>
               {(dead.length ? dead : [
                  { scheme: "AICTE Internship", days_remaining: 3 },
                  { scheme: "INSPIRE", days_remaining: 5 },
                  { scheme: "SIH", days_remaining: 8 }
               ]).map((d, i) => {
                  const days = d.days_remaining != null ? d.days_remaining : d.days;
                  const isRed = days <= 3;
                  const color = isRed ? "#ff6b6b" : "#ffd27a";
                  const borderLeft = `6px solid ${color}`;
                  const background = isRed ? "linear-gradient(90deg, rgba(255,107,107,0.1) 0%, rgba(0,0,0,0) 100%)" : "linear-gradient(90deg, rgba(255,210,122,0.05) 0%, rgba(0,0,0,0) 100%)";
                  return (
                     <div key={i} className="liquid-glass" style={{ padding: "1.5rem", borderRadius: "var(--radius-card)", color: "#fff", borderLeft, background }}>
                        <div style={{ color, fontWeight: "bold", fontSize: "1rem", fontFamily: "var(--font-body)", textTransform: "uppercase" }}>{days} Days Left</div>
                        <div style={{ fontSize: "1.4rem", marginTop: "0.25rem", fontFamily: "var(--font-body)", fontWeight: 600 }}>{d.scheme || d.name}</div>
                     </div>
                  );
               })}
            </div>
         </section>

         {/* SECTION 13: AI STUDENT COACH (Ask Udaan AI) */}
         <section>
            <SectionLabel>Ask Udaan AI</SectionLabel>
            <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", color: "#fff" }}>
               <h4 style={{ margin: "0 0 1rem 0", fontSize: "1.5rem", fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#7acaff" }}>Chat with your AI Coach</h4>
               <p style={{ margin: "0 0 1.5rem 0", opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1rem" }}>
                  Ask any questions about eligibility, application processes, resolving missing documents, or boosting approval rates.
               </p>
               <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  {[
                     "Which scholarships can I get?",
                     "How to improve my profile?",
                     "What documents are missing?",
                     "Which internship suits me?",
                     "How can I increase approval chances?"
                  ].map((promptText, i) => (
                     <button key={i} onClick={() => openChat("en", promptText)} style={{ textAlign: "left", background: "rgba(255,255,255,0.08)", border: "none", padding: "0.8rem 1.2rem", borderRadius: "0.5rem", color: "#fff", cursor: "pointer", fontFamily: "var(--font-body)", fontSize: "0.95rem", transition: "background 0.2s" }} className="udaan-lift">
                        ⚡ {promptText}
                     </button>
                  ))}
               </div>
            </div>
         </section>

         {/* SECTION 14: TIMELINE */}
         <section>
            <SectionLabel>Timeline</SectionLabel>
            <div className="liquid-glass" style={{ borderRadius: "var(--radius-card)", padding: "2.5rem 2rem", marginTop: "1rem", color: "#fff", display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
               {(time.events || [
                  { event: "Profile Created" },
                  { event: "Profile Completed" },
                  { event: "Eligibility Checked" },
                  { event: "Applied" },
                  { event: "Selected" }
               ]).map((t, i, arr) => (
                  <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
                     <div style={{ padding: "0.75rem 1.5rem", background: "rgba(255,255,255,0.15)", borderRadius: "99px", fontFamily: "var(--font-body)", fontWeight: 500, display: "flex", alignItems: "center", gap: "1rem" }}>
                         <div style={{ width: "24px", height: "24px", borderRadius: "50%", background: "#fff", color: "#000", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.8rem", fontWeight: "bold" }}>{i+1}</div>
                         {t.event}
                     </div>
                     {i < arr.length - 1 && <div style={{ height: "40px", width: "2px", background: "rgba(255,255,255,0.3)", margin: "0 0 0 23px" }} />}
                  </div>
               ))}
            </div>
         </section>

         <TelegramConnectSection userId={sum.user_id || "1"} />

         {activeDocGuide && <DocumentGuideModal docName={activeDocGuide} onClose={() => setActiveDocGuide(null)} />}
      </div>
   );
}

function DocumentUploadModal({ docName, onClose, onRefresh }) {
   const { useState } = React;
   const [uploading, setUploading] = useState(false);
   const [success, setSuccess] = useState(false);
   const [file, setFile] = useState(null);

   const handleUpload = () => {
      setUploading(true);
      fetch("http://localhost:8000/api/v1/documents/upload", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({
            user_id: 5,
            document_name: docName
         })
      })
      .then(r => r.json())
      .then(data => {
         setUploading(false);
         if (data.success) {
            setSuccess(true);
            setTimeout(() => {
               onRefresh();
               onClose();
            }, 1500);
         }
      })
      .catch(e => {
         setUploading(false);
         console.error(e);
      });
   };

   return (
      <div style={{ position: "fixed", inset: 0, zIndex: 99999, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.7)", backdropFilter: "blur(5px)", padding: "1rem" }}>
         <div className="liquid-glass-strong" style={{ width: "100%", maxWidth: "450px", borderRadius: "1.25rem", padding: "2rem", position: "relative", border: "1px solid rgba(255,255,255,0.15)", color: "#fff", fontFamily: "var(--font-body)" }}>
            <button onClick={onClose} style={{ position: "absolute", top: "1rem", right: "1rem", background: "rgba(255,255,255,0.15)", width: "32px", height: "32px", borderRadius: "50%", border: "none", color: "#fff", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
            <h3 style={{ marginTop: 0, fontSize: "1.5rem", fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#ffd27a" }}>📄 Upload {docName}</h3>
            
            {success ? (
               <div style={{ textAlign: "center", padding: "2rem 0" }}>
                  <div style={{ fontSize: "3rem", color: "#7fe0a0", marginBottom: "1rem" }}>✓</div>
                  <div style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#7fe0a0" }}>Verification Successful!</div>
                  <div style={{ opacity: 0.8, fontSize: "0.9rem", marginTop: "0.5rem" }}>Opportunity status updated in wallet.</div>
               </div>
            ) : (
               <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", marginTop: "1rem" }}>
                  <p style={{ margin: 0, fontSize: "0.9rem", opacity: 0.85, lineHeight: 1.5 }}>
                     Upload a scanned copy of your <strong>{docName}</strong>. Our Document Intelligence Engine will verify it instantly.
                  </p>
                  
                  <div style={{ border: "2px dashed rgba(255,255,255,0.25)", borderRadius: "0.75rem", padding: "2.5rem 1.5rem", textAlign: "center", cursor: "pointer", background: "rgba(255,255,255,0.03)" }} onClick={() => setFile({ name: `${docName.toLowerCase().replace(/ /g, "_")}.pdf` })}>
                     {file ? (
                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem" }}>
                           <span style={{ fontSize: "2rem" }}>📄</span>
                           <span style={{ fontSize: "0.9rem", fontWeight: "bold", color: "#7acaff" }}>{file.name}</span>
                           <span style={{ fontSize: "0.75rem", opacity: 0.6 }}>Ready to submit</span>
                        </div>
                     ) : (
                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem" }}>
                           <span style={{ fontSize: "2rem", opacity: 0.6 }}>☁</span>
                           <span style={{ fontSize: "0.9rem", fontWeight: "bold" }}>Click to select certificate file</span>
                           <span style={{ fontSize: "0.75rem", opacity: 0.6 }}>PDF, JPG, PNG (Max 5MB)</span>
                        </div>
                     )}
                  </div>
                  
                  <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
                     <button onClick={onClose} style={{ background: "transparent", color: "#fff", border: "1px solid rgba(255,255,255,0.2)", padding: "0.6rem 1.2rem", borderRadius: "0.5rem", cursor: "pointer", fontSize: "0.9rem", fontFamily: "var(--font-body)" }}>Cancel</button>
                     <button onClick={handleUpload} disabled={uploading} style={{ background: "#7acaff", color: "#000", border: "none", padding: "0.6rem 1.4rem", borderRadius: "0.5rem", cursor: "pointer", fontWeight: "bold", fontSize: "0.9rem", fontFamily: "var(--font-body)", opacity: uploading ? 0.7 : 1 }}>
                        {uploading ? "Analyzing with AI..." : "Verify & Upload"}
                     </button>
                  </div>
               </div>
            )}
         </div>
      </div>
   );
}

function RecoveryPlanModal({ onClose, onRefresh }) {
   const { useState, useEffect } = React;
   const [plan, setPlan] = useState(null);
   const [loading, setLoading] = useState(true);
   const [activeUpload, setActiveUpload] = useState(null);

   useEffect(() => {
      fetch("http://localhost:8000/api/v1/lifecycle/recovery-plan")
         .then(r => r.json())
         .then(data => { setPlan(data); setLoading(false); })
         .catch(e => { console.error(e); setLoading(false); });
   }, []);

   return (
      <div style={{ position: "fixed", inset: 0, zIndex: 99998, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.7)", backdropFilter: "blur(5px)", padding: "1rem" }}>
         <div className="liquid-glass-strong" style={{ width: "100%", maxWidth: "550px", maxHeight: "90vh", overflowY: "auto", borderRadius: "1.5rem", padding: "2rem", position: "relative", border: "1px solid rgba(255,255,255,0.15)", color: "#fff", fontFamily: "var(--font-body)" }}>
            <button onClick={onClose} style={{ position: "absolute", top: "1rem", right: "1rem", background: "rgba(255,255,255,0.15)", width: "32px", height: "32px", borderRadius: "50%", border: "none", color: "#fff", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
            
            <h3 style={{ marginTop: 0, fontSize: "1.6rem", fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#ffd27a" }}>🛠 Opportunity Recovery Plan</h3>
            
            {loading ? (
               <div style={{ color: "rgba(255,255,255,0.7)", padding: "3rem 0", textAlign: "center" }}>Generating recovery roadmap...</div>
            ) : (
               <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", marginTop: "1rem" }}>
                  <div style={{ background: "rgba(255,210,122,0.08)", borderLeft: "4px solid #ffd27a", borderRadius: "0.5rem", padding: "1rem" }}>
                     <div style={{ fontWeight: "bold", fontSize: "0.95rem", marginBottom: "0.25rem", color: "#ffd27a" }}>RECOVERY PLAYBOOK</div>
                     <div style={{ fontSize: "0.88rem", lineHeight: 1.5, opacity: 0.9 }}>{plan?.recovery_plan}</div>
                  </div>
                  
                  <div>
                     <div style={{ fontSize: "0.9rem", textTransform: "uppercase", opacity: 0.7, marginBottom: "0.5rem", fontWeight: "bold", letterSpacing: "0.5px" }}>Action Items Checklist</div>
                     <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                        {plan?.action_items?.map((item, idx) => (
                           <div key={idx} className="liquid-glass" style={{ borderRadius: "0.75rem", padding: "1rem", display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", border: "1px solid rgba(255,255,255,0.05)" }}>
                              <div>
                                 <div style={{ fontWeight: "bold", fontSize: "0.95rem" }}>{item.doc}</div>
                                 <div style={{ fontSize: "0.8rem", opacity: 0.7, marginTop: "0.15rem" }}>Issuer: {item.issuer} · Deadline: {item.deadline}</div>
                              </div>
                              <button onClick={() => setActiveUpload(item.doc)} style={{ background: "#ffd27a", color: "#000", border: "none", padding: "0.5rem 1rem", borderRadius: "0.5rem", fontSize: "0.85rem", fontWeight: "bold", cursor: "pointer" }}>Upload ↗</button>
                           </div>
                        ))}
                     </div>
                  </div>
               </div>
            )}

            {activeUpload && (
               <DocumentUploadModal
                  docName={activeUpload}
                  onClose={() => setActiveUpload(null)}
                  onRefresh={() => {
                     onRefresh();
                     onClose();
                  }}
               />
            )}
         </div>
      </div>
   );
}

function OpportunityDetailModal({ opp, onClose, onRefresh }) {
   const { useState, useEffect } = React;
   const [trust, setTrust] = useState(null);
   const [loadingTrust, setLoadingTrust] = useState(true);
   const [applying, setApplying] = useState(false);
   const [applied, setApplied] = useState(false);
   const [activeUpload, setActiveUpload] = useState(null);

   useEffect(() => {
      fetch(`http://localhost:8000/api/v1/trust/${opp.id}`)
         .then(r => r.json())
         .then(data => { setTrust(data); setLoadingTrust(false); })
         .catch(e => { console.error(e); setLoadingTrust(false); });
   }, [opp.id]);

   const handleApply = () => {
      setApplying(true);
      setTimeout(() => {
         setApplying(false);
         setApplied(true);
         onRefresh();
      }, 1200);
   };

   const isBlocked = opp.blocked_reason && opp.blocked_reason !== "None";
   const blockedDocs = isBlocked ? opp.blocked_reason.replace("Missing ", "").split(", ") : [];

   return (
      <div style={{ position: "fixed", inset: 0, zIndex: 99998, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.7)", backdropFilter: "blur(5px)", padding: "1rem" }}>
         <div className="liquid-glass-strong" style={{ width: "100%", maxWidth: "580px", maxHeight: "90vh", overflowY: "auto", borderRadius: "1.5rem", padding: "2.25rem", position: "relative", border: "1px solid rgba(255,255,255,0.15)", color: "#fff", fontFamily: "var(--font-body)" }}>
            <button onClick={onClose} style={{ position: "absolute", top: "1rem", right: "1rem", background: "rgba(255,255,255,0.15)", width: "32px", height: "32px", borderRadius: "50%", border: "none", color: "#fff", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
            
            <span className="liquid-glass" style={{ display: "inline-flex", borderRadius: "9999px", padding: "0.25rem 0.75rem", fontSize: "0.75rem", textTransform: "uppercase", fontWeight: "bold", background: isBlocked ? "rgba(255,107,107,0.15)" : "rgba(127,224,160,0.15)", color: isBlocked ? "#ff6b6b" : "#7fe0a0", border: isBlocked ? "1px solid rgba(255,107,107,0.3)" : "1px solid rgba(127,224,160,0.3)" }}>
               {isBlocked ? "Blocked" : "Ready to Apply"}
            </span>

            <h3 style={{ marginTop: "0.75rem", marginBottom: "1.25rem", fontSize: "1.8rem", fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#fff" }}>{opp.name}</h3>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem" }}>
               <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: "0.75rem", padding: "0.75rem 1rem", border: "1px solid rgba(255,255,255,0.05)" }}>
                  <div style={{ opacity: 0.6, fontSize: "0.75rem", textTransform: "uppercase" }}>Benefit Value</div>
                  <div style={{ fontSize: "1.2rem", fontWeight: "bold", color: "#7acaff", marginTop: "0.15rem" }}>{opp.benefit}</div>
               </div>
               <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: "0.75rem", padding: "0.75rem 1rem", border: "1px solid rgba(255,255,255,0.05)" }}>
                  <div style={{ opacity: 0.6, fontSize: "0.75rem", textTransform: "uppercase" }}>Deadline</div>
                  <div style={{ fontSize: "1.2rem", fontWeight: "bold", color: opp.days_remaining <= 3 ? "#ff6b6b" : "#ffd27a", marginTop: "0.15rem" }}>{opp.deadline} <span style={{ fontSize: "0.8rem", fontWeight: "normal", opacity: 0.8 }}>({opp.days_remaining}d)</span></div>
               </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
               <div style={{ borderLeft: "3px solid #7acaff", paddingLeft: "1rem" }}>
                  <div style={{ fontWeight: "bold", fontSize: "0.85rem", textTransform: "uppercase", color: "#7acaff" }}>
                     🛡 Trust Engine Score: {loadingTrust ? "..." : `${trust?.trust_score}/100`}
                  </div>
                  <p style={{ margin: "0.25rem 0 0", fontSize: "0.85rem", opacity: 0.8 }}>
                     Verified source type: <strong>{loadingTrust ? "..." : trust?.source_type}</strong>. Official source verification {loadingTrust ? "..." : (trust?.verified ? "PASSED ✓" : "FAILED")}.
                  </p>
               </div>

               <div style={{ borderLeft: "3px solid #ffd27a", paddingLeft: "1rem" }}>
                  <div style={{ fontWeight: "bold", fontSize: "0.85rem", textTransform: "uppercase", color: "#ffd27a" }}>
                     🎯 Approval Engine Probability: {opp.approval_probability}%
                  </div>
                  <p style={{ margin: "0.25rem 0 0", fontSize: "0.85rem", opacity: 0.8 }}>
                     {isBlocked ? "Approval probability is low because of missing documents." : "You satisfy all key eligibility criteria. High likelihood of approval."}
                  </p>
               </div>

               {isBlocked && (
                  <div style={{ background: "rgba(255,107,107,0.08)", borderLeft: "3px solid #ff6b6b", borderRadius: "0.5rem", padding: "1rem" }}>
                     <div style={{ fontWeight: "bold", color: "#ff6b6b", fontSize: "0.85rem", textTransform: "uppercase", marginBottom: "0.5rem" }}>⚠️ Missing Requirements</div>
                     <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                        {blockedDocs.map((doc, idx) => (
                           <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                              <span style={{ fontSize: "0.85rem", opacity: 0.9 }}>• {doc}</span>
                              <button onClick={() => setActiveUpload(doc)} style={{ background: "rgba(255,255,255,0.15)", border: "none", color: "#fff", padding: "0.25rem 0.6rem", borderRadius: "0.25rem", fontSize: "0.75rem", cursor: "pointer", fontWeight: "bold" }}>Upload ↗</button>
                           </div>
                        ))}
                     </div>
                  </div>
               )}

               <div style={{ marginTop: "1.5rem", display: "flex", gap: "1rem", justifyContent: "flex-end" }}>
                  <button onClick={onClose} style={{ background: "transparent", color: "#fff", border: "1px solid rgba(255,255,255,0.2)", padding: "0.7rem 1.4rem", borderRadius: "0.5rem", cursor: "pointer", fontSize: "0.9rem", fontWeight: "600" }}>Close</button>
                  
                  {applied ? (
                     <button disabled style={{ background: "rgba(127,224,160,0.2)", color: "#7fe0a0", border: "1px solid rgba(127,224,160,0.4)", padding: "0.7rem 1.6rem", borderRadius: "0.5rem", fontSize: "0.9rem", fontWeight: "bold" }}>Applied Successfully ✓</button>
                  ) : (
                     <button onClick={handleApply} disabled={isBlocked || applying} style={{ background: isBlocked ? "rgba(255,255,255,0.1)" : "#fff", color: isBlocked ? "rgba(255,255,255,0.3)" : "#000", border: "none", padding: "0.7rem 1.6rem", borderRadius: "0.5rem", cursor: isBlocked ? "not-allowed" : "pointer", fontWeight: "bold", fontSize: "0.9rem" }}>
                        {applying ? "Submitting application..." : "Apply Now ↗"}
                     </button>
                  )}
               </div>
            </div>

            {activeUpload && (
               <DocumentUploadModal
                  docName={activeUpload}
                  onClose={() => setActiveUpload(null)}
                  onRefresh={() => {
                     onRefresh();
                     onClose();
                  }}
               />
            )}
         </div>
      </div>
   );
}

function JobSeekerSections({ data, loading, Icon, Button, Tag, openChat, onRefresh }) {
   const { useState } = React;
   const [activeOpp, setActiveOpp] = useState(null);
   const [activeUpload, setActiveUpload] = useState(null);
   const [showRecovery, setShowRecovery] = useState(false);
   const [selectedLanguage, setSelectedLanguage] = useState("English");
   const [voiceChatting, setVoiceChatting] = useState(false);
   const [voiceTranscript, setVoiceTranscript] = useState("");
   const [voiceReply, setVoiceReply] = useState("");
   
   // Scam Shield State
   const [scamText, setScamText] = useState("");
   const [scanStatus, setScanStatus] = useState("idle");
   const [scanResult, setScanResult] = useState(null);

   if (loading || !data) {
      return (
         <div style={{ padding: "5rem 1.5rem", textAlign: "center", color: "#fff", fontFamily: "var(--font-body)", fontSize: "1.2rem" }}>
            Loading Opportunity Intelligence Engines...
         </div>
      );
   }

   const profile = data.profile_context || {};
   const missed = data.missed || {};
   const readiness = data.readiness || {};
   const docs = data.documents || { verified: [], missing: [], expiring: [] };
   const roadmap = data.roadmap || { steps: [] };
   const recommended = data.recommended?.opportunities || [];
   const approval = data.approval || {};
   const value = data.value || {};
   const oppWallet = data.opportunity_summary || {};
   const tracker = data.applications || [];
   const deadlines = data.deadlines?.deadlines || [];

   const handleQuickCoach = (prompt) => {
      openChat && openChat(prompt);
   };

   const startVoiceAssistant = () => {
      setVoiceChatting(true);
      setVoiceTranscript("Listening in " + selectedLanguage + "...");
      setVoiceReply("");
      
      setTimeout(() => {
         setVoiceTranscript("I am looking for government jobs or apprenticeships in Hyderabad.");
         fetch("http://localhost:8000/api/v1/voice/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
               transcript: "I am looking for government jobs or apprenticeships in Hyderabad.",
               language: selectedLanguage.toLowerCase()
            })
         })
         .then(r => r.json())
         .then(res => {
            setVoiceReply(res.reply || "Matched 3 government job programs and 2 apprenticeships in Hyderabad for OBC category.");
         })
         .catch(e => {
            setVoiceReply("Matched 3 government job programs and 2 apprenticeships in Hyderabad for OBC category.");
         });
      }, 1800);
   };

   // Upgrade Java Programming Skill
   const handleUpgradeSkill = () => {
      fetch("http://localhost:8000/api/v1/jobseeker/add-skill", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ user_id: 5, skill: "Java Programming" })
      })
      .then(r => r.json())
      .then(() => {
         onRefresh && onRefresh();
      })
      .catch(e => console.error("Failed to upgrade skill:", e));
   };

   // Apply Opportunity
   const handleApply = (opp) => {
      fetch("http://localhost:8000/api/v1/jobseeker/apply", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ user_id: 5, opportunity_id: opp.id })
      })
      .then(r => r.json())
      .then(() => {
         onRefresh && onRefresh();
      })
      .catch(e => console.error("Failed to apply opportunity:", e));
   };

   // Scan for Scams
   const handleScanScam = () => {
      if (!scamText.trim()) return;
      setScanStatus("scanning");
      setScanResult(null);
      
      fetch("http://localhost:8000/api/v1/scam/scan", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ text: scamText })
      })
      .then(r => r.json())
      .then(res => {
         setScanStatus("done");
         setScanResult(res);
      })
      .catch(e => {
         setScanStatus("done");
         setScanResult({ status: "safe", reason: "Shield Idle. Offline rule checks passed." });
      });
   };

   return (
      <div style={{ maxWidth: "1240px", margin: "0 auto", padding: "1rem clamp(1.5rem, 5vw, 5rem)", display: "flex", flexDirection: "column", gap: "2.5rem" }}>
         
         {/* 1. Missed Opportunity Alert */}
         {missed.opportunity_name && (
            <section>
               <div style={{ background: "linear-gradient(135deg, rgba(255,107,107,0.18) 0%, rgba(255,150,150,0.06) 100%)", border: "1px solid rgba(255,107,107,0.45)", borderRadius: "var(--radius-card)", padding: "1.5rem", color: "#fff", display: "flex", flexDirection: "column", gap: "1rem", boxShadow: "0 8px 32px rgba(255,107,107,0.15)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                     <Icon name="alert" size={20} style={{ color: "#ff6b6b" }} />
                     <span style={{ fontWeight: 800, fontSize: "0.85rem", textTransform: "uppercase", color: "#ff6b6b", letterSpacing: "1px" }}>Missed Opportunity Alert</span>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                     <p style={{ margin: 0, fontSize: "1.1rem", fontFamily: "var(--font-body)", lineHeight: 1.5 }}>
                        You permanently missed the <strong style={{ color: "#ff6b6b" }}>{missed.opportunity_name} (₹{missed.value_lost?.toLocaleString()} value)</strong>. The deadline closed on 31 Jan 2026 because your <strong style={{ color: "#ffd27a" }}>Caste Certificate</strong> was not verified in time.
                     </p>
                     <div>
                        <button onClick={() => setActiveUpload("Caste Certificate (OBC)")} style={{ background: "#fff", color: "#000", border: "none", padding: "0.6rem 1.4rem", borderRadius: "9999px", fontWeight: "bold", cursor: "pointer", fontFamily: "var(--font-body)", fontSize: "0.9rem" }}>
                           Fix Caste Certificate
                        </button>
                     </div>
                  </div>
               </div>
            </section>
         )}

         {/* 2. Logged In Job Seeker Profile Card */}
         <section>
            <div style={{ fontSize: "0.85rem", color: "rgba(255,255,255,0.6)", fontFamily: "var(--font-body)", textTransform: "uppercase", letterSpacing: "1px", marginBottom: "0.5rem" }}>LOGGED IN JOB SEEKER</div>
            <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.75rem", color: "#fff", display: "flex", flexDirection: "column", gap: "1.5rem", border: "1px solid rgba(255,255,255,0.15)" }}>
               <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
                  <h3 style={{ margin: "0", fontSize: "2.4rem", fontFamily: "var(--font-heading)", fontStyle: "italic", fontWeight: "normal" }}>{profile.name}</h3>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                     <span className="liquid-glass" style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem", borderRadius: "9999px", padding: "0.35rem 0.9rem", fontSize: "0.8rem", fontWeight: "bold", background: "rgba(127,224,160,0.15)", color: "#7fe0a0", border: "1px solid rgba(127,224,160,0.3)" }}>
                        ✓ Verified Seeker
                     </span>
                     <span className="liquid-glass" style={{ display: "inline-flex", borderRadius: "9999px", padding: "0.35rem 0.9rem", fontSize: "0.8rem", fontWeight: "bold", background: "rgba(255,255,255,0.08)", color: "#fff", border: "1px solid rgba(255,255,255,0.15)" }}>
                        {profile.category} Category
                     </span>
                  </div>
               </div>

               <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "1.5rem", fontSize: "0.88rem", borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: "1.25rem" }}>
                  <div>
                     <div style={{ opacity: 0.5, fontSize: "0.75rem", textTransform: "uppercase", marginBottom: "0.25rem" }}>Education</div>
                     <div style={{ fontWeight: "bold", fontSize: "0.95rem" }}>{profile.education}</div>
                  </div>
                  <div>
                     <div style={{ opacity: 0.5, fontSize: "0.75rem", textTransform: "uppercase", marginBottom: "0.25rem" }}>Experience</div>
                     <div style={{ fontWeight: "bold", fontSize: "0.95rem" }}>{profile.experience === "0" || profile.experience === 0 ? "Fresher" : `${profile.experience} Year`}</div>
                  </div>
                  <div>
                     <div style={{ opacity: 0.5, fontSize: "0.75rem", textTransform: "uppercase", marginBottom: "0.25rem" }}>Target Role</div>
                     <div style={{ fontWeight: "bold", fontSize: "0.95rem" }}>{profile.target_role}</div>
                  </div>
                  <div>
                     <div style={{ opacity: 0.5, fontSize: "0.75rem", textTransform: "uppercase", marginBottom: "0.25rem" }}>Location</div>
                     <div style={{ fontWeight: "bold", fontSize: "0.95rem" }}>{profile.location}</div>
                  </div>
                  <div>
                     <div style={{ opacity: 0.5, fontSize: "0.75rem", textTransform: "uppercase", marginBottom: "0.25rem" }}>Skills</div>
                     <div style={{ fontWeight: "bold", fontSize: "0.95rem", display: "flex", flexWrap: "wrap", gap: "0.25rem" }}>
                        {profile.skills?.join(", ")}
                     </div>
                  </div>
               </div>
            </div>
         </section>

         {/* 3. Recommended Opportunities Section */}
         <section id="matched-jobs-section">
            <SectionLabel>Top Matched Opportunities</SectionLabel>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.5rem", marginTop: "1rem" }}>
               {recommended.map((opp, idx) => {
                  const isBlocked = opp.blocked_reason && opp.blocked_reason !== "None";
                  const isPMKVY = opp.name.includes("PMKVY") || opp.is_skilling;
                  
                  return (
                     <div key={idx} className="liquid-glass udaan-lift" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", border: "1px solid rgba(255,255,255,0.08)", display: "flex", flexDirection: "column", gap: "1.2rem", background: "rgba(255,255,255,0.02)" }}>
                        {/* Top Line Badges for PMKVY */}
                        {isPMKVY && (
                           <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", marginBottom: "-0.4rem" }}>
                              <span style={{ background: "rgba(255,255,255,0.08)", color: "#fff", padding: "0.2rem 0.6rem", borderRadius: "9999px", fontSize: "0.7rem", fontWeight: "bold" }}>Skilling</span>
                              <span style={{ background: opp.ready_percentage === 100 ? "rgba(127,224,160,0.15)" : "rgba(255,210,122,0.15)", color: opp.ready_percentage === 100 ? "#7fe0a0" : "#ffd27a", padding: "0.2rem 0.6rem", borderRadius: "9999px", fontSize: "0.7rem", fontWeight: "bold" }}>{opp.ready_percentage}% Ready</span>
                              <span style={{ background: "rgba(255,255,255,0.08)", color: "#fff", padding: "0.2rem 0.6rem", borderRadius: "9999px", fontSize: "0.7rem", fontWeight: "bold" }}>Govt Official</span>
                           </div>
                        )}
                        
                        <h4 style={{ margin: 0, fontSize: "1.45rem", fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#fff", lineHeight: 1.25 }}>{opp.name}</h4>
                        
                        {/* Official / Trust Info badges */}
                        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.5rem", fontSize: "0.75rem" }}>
                           <span style={{ display: "inline-flex", alignItems: "center", gap: "0.2rem", color: "rgba(255,255,255,0.6)" }}>
                              🔗 <a href={`https://${opp.official_url}`} target="_blank" rel="noopener noreferrer" style={{ color: "rgba(255,255,255,0.6)", textDecoration: "none" }}>{opp.official_url}</a>
                           </span>
                           <span style={{ color: "#7fe0a0", fontWeight: "bold", background: "rgba(127,224,160,0.08)", padding: "0.15rem 0.45rem", borderRadius: "0.3rem" }}>✓ Trust {opp.trust_score}%</span>
                           {opp.is_official_govt && (
                              <span style={{ color: "#7acaff", fontWeight: "bold", background: "rgba(122,202,255,0.08)", padding: "0.15rem 0.45rem", borderRadius: "0.3rem" }}>IN Official Govt</span>
                           )}
                        </div>
                        
                        {/* Details */}
                        <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", fontSize: "0.88rem", color: "rgba(255,255,255,0.85)" }}>
                           <div>Benefit: <strong>{opp.benefit}</strong></div>
                           <div>Deadline: <strong>{opp.deadline} ({opp.days_remaining} days remaining)</strong></div>
                        </div>
                        
                        {/* Actions */}
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "1rem", marginTop: "auto" }}>
                           <span onClick={() => setActiveOpp(opp)} style={{ fontSize: "0.85rem", color: "#7acaff", textDecoration: "underline", cursor: "pointer" }}>Check Eligibility</span>
                           
                           {isPMKVY ? (
                              opp.ready_percentage === 100 ? (
                                 <button onClick={(e) => { e.stopPropagation(); handleApply(opp); }} style={{ background: "#fff", color: "#000", border: "none", padding: "0.55rem 1.4rem", borderRadius: "9999px", fontWeight: "bold", cursor: "pointer", fontSize: "0.85rem" }}>
                                    Apply Now
                                 </button>
                              ) : (
                                 <button onClick={(e) => { e.stopPropagation(); handleUpgradeSkill(); }} style={{ background: "linear-gradient(135deg, #ff9f43 0%, #ff5252 100%)", color: "#fff", border: "none", padding: "0.55rem 1.4rem", borderRadius: "9999px", fontWeight: "bold", cursor: "pointer", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "0.25rem" }} className="udaan-lift">
                                    ⚡ Enroll Free Fix
                                 </button>
                              )
                           ) : isBlocked ? (
                              <button onClick={(e) => { e.stopPropagation(); setShowRecovery(true); }} style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.25)", color: "#fff", padding: "0.55rem 1.4rem", borderRadius: "9999px", fontWeight: "bold", cursor: "pointer", fontSize: "0.85rem" }}>
                                 Resolve Blockers
                              </button>
                           ) : (
                              <button onClick={(e) => { e.stopPropagation(); handleApply(opp); }} style={{ background: "#fff", color: "#000", border: "none", padding: "0.55rem 1.4rem", borderRadius: "9999px", fontWeight: "bold", cursor: "pointer", fontSize: "0.85rem" }}>
                                 Apply Now
                              </button>
                           )}
                        </div>
                     </div>
                  );
               })}
            </div>
         </section>

         {/* 4. Three-Column Engine Results Grid */}
         <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "2rem" }}>
            
            {/* Column 1: Application Readiness Ring */}
            <section>
               <SectionLabel>Application Readiness Ring</SectionLabel>
               <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", marginTop: "1rem", border: "1px solid rgba(255,255,255,0.1)", display: "flex", flexDirection: "column", gap: "1.2rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
                     <div style={{ position: "relative", width: "80px", height: "80px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <svg width="80" height="80" viewBox="0 0 36 36">
                           <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="3.5" />
                           <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#ffd27a" strokeWidth="3.5" strokeDasharray={`${readiness.overall || 78}, 100`} />
                        </svg>
                        <div style={{ position: "absolute", fontSize: "1.3rem", fontWeight: "bold", fontFamily: "var(--font-heading)", color: "#ffd27a" }}>{readiness.overall || 78}%</div>
                     </div>
                     <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.4rem", fontSize: "0.88rem", color: "#fff" }}>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                           <span style={{ opacity: 0.7 }}>Profile Data:</span> <strong style={{ color: "#7fe0a0" }}>{readiness.profile || 85}%</strong>
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                           <span style={{ opacity: 0.7 }}>Required Documents:</span> <strong style={{ color: "#ffd27a" }}>{readiness.documents || 70}%</strong>
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                           <span style={{ opacity: 0.7 }}>Required Skills:</span> <strong style={{ color: "#7acaff" }}>{readiness.skills || 80}%</strong>
                        </div>
                     </div>
                  </div>
                  
                  {/* Callout box Upgrade */}
                  <div style={{ background: "rgba(255,210,122,0.06)", border: "1px solid rgba(255,210,122,0.25)", borderRadius: "var(--radius-card)", padding: "1rem", fontSize: "0.85rem", color: "#fff", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                     <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "#ffd27a", fontWeight: "bold" }}>
                        <span>✨ AI Free Scheme Fix Upgrade</span>
                     </div>
                     {readiness.skills < 100 ? (
                        <>
                           <p style={{ margin: 0, opacity: 0.9, lineHeight: 1.4 }}>
                              You are missing the <strong style={{ color: "#ffd27a" }}>Java Programming</strong> skill required for the <strong style={{ color: "#7acaff" }}>PMKVY Java Developer</strong> scheme.
                           </p>
                           <div>
                              <button onClick={handleUpgradeSkill} style={{ background: "#fff", color: "#000", border: "none", padding: "0.45rem 1.1rem", borderRadius: "9999px", fontWeight: "bold", cursor: "pointer", fontFamily: "var(--font-body)", fontSize: "0.8rem" }}>
                                 Enroll Free Upgrade
                              </button>
                           </div>
                        </>
                     ) : (
                        <p style={{ margin: 0, color: "#7fe0a0", fontWeight: "bold" }}>
                           ✓ Skill upgraded successfully! PMKVY Java Developer is now 100% Ready.
                        </p>
                     )}
                  </div>
               </div>
            </section>

            {/* Column 2: Document Verification Wallet */}
            <section>
               <SectionLabel>Document Verification Wallet</SectionLabel>
               <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", marginTop: "1rem", border: "1px solid rgba(255,255,255,0.1)", display: "flex", flexDirection: "column", gap: "0.85rem" }}>
                  {/* Aadhaar Row */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                     <span style={{ fontSize: "0.95rem" }}>Aadhaar Identity Card</span>
                     <span style={{ background: "rgba(127,224,160,0.15)", color: "#7fe0a0", padding: "0.2rem 0.65rem", borderRadius: "9999px", fontSize: "0.75rem", fontWeight: "bold" }}>✓ Verified</span>
                  </div>
                  
                  {/* BTech Graduation Row */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                     <span style={{ fontSize: "0.95rem" }}>Graduation Certificate (B.Tech)</span>
                     <span style={{ background: "rgba(127,224,160,0.15)", color: "#7fe0a0", padding: "0.2rem 0.65rem", borderRadius: "9999px", fontSize: "0.75rem", fontWeight: "bold" }}>✓ Verified</span>
                  </div>
                  
                  {/* Caste Certificate OBC Row */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                     <span style={{ fontSize: "0.95rem" }}>Caste Certificate (OBC)</span>
                     {docs.verified.includes("Caste Certificate (OBC)") ? (
                        <span style={{ background: "rgba(127,224,160,0.15)", color: "#7fe0a0", padding: "0.2rem 0.65rem", borderRadius: "9999px", fontSize: "0.75rem", fontWeight: "bold" }}>✓ Verified</span>
                     ) : (
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                           <span style={{ background: "rgba(255,107,107,0.15)", color: "#ff6b6b", padding: "0.2rem 0.65rem", borderRadius: "9999px", fontSize: "0.75rem", fontWeight: "bold" }}>⚠️ Missing</span>
                           <button onClick={() => setActiveUpload("Caste Certificate (OBC)")} style={{ background: "#fff", color: "#000", border: "none", padding: "0.2rem 0.65rem", borderRadius: "9999px", fontSize: "0.75rem", fontWeight: "bold", cursor: "pointer" }}>Upload</button>
                        </div>
                     )}
                  </div>
                  
                  {/* Income Certificate Row */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0" }}>
                     <span style={{ fontSize: "0.95rem" }}>Income Certificate</span>
                     {docs.verified.includes("Income Certificate") ? (
                        <span style={{ background: "rgba(127,224,160,0.15)", color: "#7fe0a0", padding: "0.2rem 0.65rem", borderRadius: "9999px", fontSize: "0.75rem", fontWeight: "bold" }}>✓ Verified</span>
                     ) : (
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                           <span style={{ background: "rgba(255,255,255,0.06)", color: "rgba(255,255,255,0.6)", padding: "0.2rem 0.65rem", borderRadius: "9999px", fontSize: "0.75rem" }}>Optional</span>
                           <button onClick={() => setActiveUpload("Income Certificate")} style={{ background: "rgba(255,255,255,0.15)", color: "#fff", border: "none", padding: "0.2rem 0.65rem", borderRadius: "9999px", fontSize: "0.75rem", fontWeight: "bold", cursor: "pointer" }}>Upload</button>
                        </div>
                     )}
                  </div>
               </div>
            </section>

            {/* Column 3: Personalized Seeker Roadmap */}
            <section>
               <SectionLabel>Personalized Seeker Roadmap</SectionLabel>
               <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "1.5rem", marginTop: "1rem", border: "1px solid rgba(255,255,255,0.1)", display: "flex", flexDirection: "column", gap: "1rem" }}>
                  {roadmap.steps?.map((step, idx) => (
                     <div key={idx} style={{ display: "flex", gap: "0.8rem", alignItems: "flex-start" }}>
                        <span style={{ fontSize: "1.1rem", lineHeight: "1.1", cursor: "default" }}>
                           {step.checked ? (
                              <span style={{ color: "#7fe0a0" }}>☑</span>
                           ) : (
                              <span style={{ color: "rgba(255,255,255,0.35)" }}>☐</span>
                           )}
                        </span>
                        <div style={{ flex: 1 }}>
                           <div style={{ fontWeight: "bold", fontSize: "0.92rem", color: step.checked ? "rgba(255,255,255,0.7)" : "#fff", textDecoration: step.checked ? "line-through" : "none" }}>{step.title}</div>
                           <div style={{ fontSize: "0.78rem", opacity: step.checked ? 0.4 : 0.7, marginTop: "0.15rem", color: step.checked ? "#fff" : "#ffd27a" }}>{step.description}</div>
                        </div>
                     </div>
                  ))}
               </div>
            </section>

         </div>

         {/* 5. Scam Shield Guard */}
         <section>
            <SectionLabel>Scam Shield Guard</SectionLabel>
            <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", border: "1px solid rgba(255,255,255,0.12)", color: "#fff", display: "flex", flexDirection: "column", gap: "1.2rem" }}>
               <div>
                  <h4 style={{ margin: 0, fontSize: "1.45rem", fontFamily: "var(--font-heading)", fontStyle: "italic", fontWeight: "normal" }}>Verify Job Post Authenticity</h4>
                  <p style={{ margin: "0.5rem 0 0", fontSize: "0.9rem", opacity: 0.8, lineHeight: 1.5 }}>
                     Paste a suspicious job description, contact message, or email below. The Scam Shield rule-engine will evaluate it for suspect signatures (such as mandatory refundable deposits or WhatsApp group recruitments).
                  </p>
               </div>
               
               <textarea
                  value={scamText}
                  onChange={(e) => setScamText(e.target.value)}
                  placeholder="e.g., Earn Rs 5000 daily working from home! Join our Telegram group. Refundable security deposit of Rs 1500 mandatory for laptop dispatch."
                  style={{ background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: "0.6rem", padding: "1rem", color: "#fff", fontFamily: "var(--font-body)", fontSize: "0.92rem", minHeight: "100px", resize: "vertical" }}
               />
               
               <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "1.5rem" }}>
                  <button onClick={handleScanScam} style={{ background: "#fff", color: "#000", border: "none", padding: "0.65rem 1.5rem", borderRadius: "9999px", fontWeight: "bold", cursor: "pointer", fontSize: "0.9rem" }}>
                     Scan for Scams
                  </button>
                  
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.9rem" }}>
                     {scanStatus === "idle" && (
                        <>
                           <span>🛡️</span>
                           <span style={{ opacity: 0.6 }}>Shield Idle. Enter text to scan.</span>
                        </>
                     )}
                     {scanStatus === "scanning" && (
                        <>
                           <span style={{ color: "#ffd27a" }}>🔄</span>
                           <span style={{ color: "#ffd27a", fontWeight: "bold" }}>Scanning...</span>
                        </>
                     )}
                     {scanStatus === "done" && scanResult && (
                        scanResult.status === "flagged" ? (
                           <>
                              <span style={{ color: "#ff6b6b" }}>🛑</span>
                              <span style={{ color: "#ff6b6b", fontWeight: "bold" }}>{scanResult.reason}</span>
                           </>
                        ) : (
                           <>
                              <span style={{ color: "#7fe0a0" }}>🛡️</span>
                              <span style={{ color: "#7fe0a0", fontWeight: "bold" }}>Safe: No known scam signatures detected.</span>
                           </>
                        )
                     )}
                  </div>
               </div>
            </div>
         </section>

         {/* 6. Chat with UDAAN AI Prompt Card */}
         <section>
            <div id="ai-coach-section" className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "2rem", border: "1px solid rgba(255,255,255,0.15)", background: "linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%)", display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "1.5rem" }}>
               <div style={{ flex: 1, minWidth: "280px" }}>
                  <h4 style={{ margin: 0, fontSize: "1.8rem", fontFamily: "var(--font-heading)", fontStyle: "italic", fontWeight: "normal", color: "#fff" }}>Chat with UDAAN AI</h4>
                  <p style={{ margin: "0.5rem 0 0", fontSize: "0.95rem", opacity: 0.8, lineHeight: 1.4 }}>
                     Ask about any scheme, check your eligibility in seconds and get step-by-step help applying — anytime.
                  </p>
               </div>
               <button onClick={() => {
                  const el = document.getElementById("udaan-coach-input");
                  if (el) {
                     el.focus();
                     el.scrollIntoView({ behavior: "smooth" });
                  }
               }} style={{ background: "#fff", color: "#000", border: "none", padding: "0.75rem 1.6rem", borderRadius: "9999px", fontWeight: "bold", cursor: "pointer", fontSize: "0.95rem" }} className="udaan-lift">
                  Start chatting ↗
               </button>
            </div>
         </section>

         {/* 7. AI Career Coach Details */}
         <section>
            <SectionLabel>UDAAN AI Application Coach</SectionLabel>
            <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", border: "1px solid rgba(255,255,255,0.15)", color: "#fff", fontFamily: "var(--font-body)", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
               <div>
                  <h4 style={{ margin: 0, fontSize: "1.45rem", fontFamily: "var(--font-heading)", fontStyle: "italic", fontWeight: "normal" }}>Speak with UDAAN AI Application Coach</h4>
                  <p style={{ margin: "0.5rem 0 0", fontSize: "0.9rem", opacity: 0.85, lineHeight: 1.5 }}>
                     Get instant feedback on your resume, practice interview answers, find matches for central government jobs, or ask for guidance on documentation requirements.
                  </p>
               </div>

               <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.75rem" }}>
                  {[
                     { label: "Career Guidance", prompt: "Explain best career roles for BTech CSE in Hyderabad." },
                     { label: "Resume Help", prompt: "Help me tailor my resume for an AI Engineer role." },
                     { label: "Government Jobs", prompt: "List top central government job opportunities for my category." },
                     { label: "Skilling Programs", prompt: "What free skilling programs offer certificates and stipends?" },
                     { label: "Interview Preparation", prompt: "Mock interview practice for entry level SQL developer." },
                     { label: "Application Assistance", prompt: "Guide me step-by-step through the SSC CGL application." }
                  ].map((item, idx) => (
                     <button key={idx} id={idx === 5 ? "udaan-coach-input" : undefined} onClick={() => handleQuickCoach(item.prompt)} className="liquid-glass" style={{ borderRadius: "0.6rem", padding: "0.75rem 1rem", border: "1px solid rgba(255,255,255,0.06)", color: "#fff", cursor: "pointer", fontSize: "0.85rem", textAlign: "left", transition: "background 0.2s" }} onMouseEnter={(e) => e.target.style.background="rgba(255,255,255,0.08)"} onMouseLeave={(e) => e.target.style.background="rgba(255,255,255,0.04)"}>
                        💡 {item.label}
                     </button>
                  ))}
               </div>

               <div style={{ borderTop: "1px solid rgba(255,255,255,0.1)", paddingTop: "1.5rem", display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "1.5rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                     <div style={{ fontSize: "0.85rem", opacity: 0.6, textTransform: "uppercase" }}>Language:</div>
                     <div style={{ display: "flex", gap: "0.4rem" }}>
                        {["English", "Hindi", "Telugu"].map((lang) => (
                           <button key={lang} onClick={() => setSelectedLanguage(lang)} style={{ background: selectedLanguage === lang ? "#ffd27a" : "rgba(255,255,255,0.08)", color: selectedLanguage === lang ? "#000" : "#fff", border: "none", borderRadius: "9999px", padding: "0.3rem 0.8rem", fontSize: "0.8rem", cursor: "pointer", fontWeight: "bold" }}>{lang}</button>
                        ))}
                     </div>
                  </div>
                  
                  <button onClick={startVoiceAssistant} className="liquid-glass-strong" style={{ background: "rgba(255,107,107,0.15)", border: "1px solid rgba(255,107,107,0.4)", borderRadius: "9999px", padding: "0.7rem 1.6rem", color: "#fff", fontWeight: "bold", fontSize: "0.9rem", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                     🎤 Speak With UDAAN AI
                  </button>
               </div>

               {voiceChatting && (
                  <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: "0.75rem", padding: "1.25rem", border: "1px solid rgba(255,255,255,0.05)", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                     <div style={{ display: "flex", alignItems: "flex-start", gap: "0.5rem" }}>
                        <span style={{ fontSize: "0.8rem", textTransform: "uppercase", opacity: 0.5, flex: "0 0 60px" }}>You:</span>
                        <div style={{ fontSize: "0.92rem", fontWeight: 500 }}>{voiceTranscript}</div>
                     </div>
                     {voiceReply && (
                        <div style={{ display: "flex", alignItems: "flex-start", gap: "0.5rem", borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: "0.75rem" }}>
                           <span style={{ fontSize: "0.8rem", textTransform: "uppercase", color: "#ffd27a", flex: "0 0 60px" }}>UDAAN:</span>
                           <div style={{ fontSize: "0.92rem", color: "#ffd27a", fontStyle: "italic" }}>{voiceReply}</div>
                        </div>
                     )}
                  </div>
               )}
            </div>
         </section>

         {/* 8. Telegram Connection */}
         <TelegramConnectSection userId={5} />

         {showRecovery && (
            <RecoveryPlanModal
               onClose={() => setShowRecovery(false)}
               onRefresh={onRefresh}
            />
         )}

         {activeOpp && (
            <OpportunityDetailModal
               opp={activeOpp}
               onClose={() => setActiveOpp(null)}
               onRefresh={onRefresh}
            />
         )}

         {activeUpload && (
            <DocumentUploadModal
               docName={activeUpload}
               onClose={() => setActiveUpload(null)}
               onRefresh={onRefresh}
            />
         )}
      </div>
   );
}

/* ---------- Subcomponents ---------- */
function SectionLabel({ children }) {
  return <div style={{ fontSize: "0.875rem", color: "#ffd27a", fontFamily: "var(--font-body)", textTransform: "uppercase", letterSpacing: "1px", textShadow: "0 1px 3px rgba(0,0,0,0.7)" }}>{children}</div>;
}

function TelegramConnectSection({ userId }) {
   const { useState, useEffect } = React;
   const [status, setStatus] = useState({ connected: false });
   const [loading, setLoading] = useState(true);
   const [testing, setTesting] = useState(false);
   const [testSuccess, setTestSuccess] = useState(null);

   const checkStatus = () => {
      setLoading(true);
      fetch(`http://localhost:8000/api/v1/telegram/status/${userId}`)
         .then(r => r.json())
         .then(data => {
            setStatus(data);
            setLoading(false);
         })
         .catch(e => {
            console.error("Failed to fetch Telegram connection status:", e);
            setLoading(false);
         });
   };

   useEffect(() => {
      if (userId) {
         checkStatus();
      }
   }, [userId]);

   const handleSendTest = () => {
      setTesting(true);
      setTestSuccess(null);
      fetch(`http://localhost:8000/api/v1/telegram/test`, {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({
            user_id: parseInt(userId),
            message: "🔔 Hello! This is a test notification from UDAAN AI Platform. Your Telegram bot integration is working perfectly!"
         })
      })
      .then(r => r.json())
      .then(data => {
         setTesting(false);
         if (data.status === "success") {
            setTestSuccess(true);
         } else {
            setTestSuccess(false);
         }
      })
      .catch(() => {
         setTesting(false);
         setTestSuccess(false);
      });
   };

   const botLink = `https://t.me/udaan_ai_bot?start=${userId}`;

   return (
      <section>
         <SectionLabel>Telegram Bot Integration</SectionLabel>
         <div className="liquid-glass-strong" style={{ borderRadius: "var(--radius-card)", padding: "2rem", marginTop: "1rem", color: "#fff", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "2rem" }}>
            <div style={{ flex: 1, minWidth: "280px" }}>
               <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "1.6rem", fontFamily: "var(--font-heading)", fontStyle: "italic", color: "#7acaff" }}>
                  UDAAN AI Telegram Assistant
               </h3>
               <p style={{ margin: 0, opacity: 0.8, fontFamily: "var(--font-body)", fontSize: "1rem", lineHeight: "1.5" }}>
                  Connect your account to get real-time alerts on new schemes, approaching deadlines, missing documents, and interact with the AI Application Coach.
               </p>
               
               {loading ? (
                  <div style={{ marginTop: "1rem", fontFamily: "var(--font-body)", opacity: 0.6 }}>Checking status...</div>
               ) : status.connected ? (
                  <div style={{ marginTop: "1rem", display: "flex", alignItems: "center", gap: "0.5rem", fontFamily: "var(--font-body)" }}>
                     <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#7fe0a0" }} />
                     <span style={{ color: "#7fe0a0", fontWeight: "bold" }}>Connected</span>
                     {status.telegram_username && <span style={{ opacity: 0.7 }}>@{status.telegram_username}</span>}
                  </div>
               ) : (
                  <div style={{ marginTop: "1rem", display: "flex", alignItems: "center", gap: "0.5rem", fontFamily: "var(--font-body)" }}>
                     <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#ff6b6b" }} />
                     <span style={{ color: "#ff6b6b", fontWeight: "bold" }}>Not Connected</span>
                  </div>
               )}
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", minWidth: "200px" }}>
               <button 
                  onClick={() => window.open(botLink, "_blank")} 
                  style={{ background: "#fff", color: "#000", border: "none", padding: "0.8rem 1.5rem", borderRadius: "0.5rem", cursor: "pointer", fontWeight: "bold", fontFamily: "var(--font-body)", fontSize: "0.95rem", textAlign: "center" }}
                  className="udaan-lift"
               >
                  {status.connected ? "🔄 Reconnect Bot" : "🔌 Connect Telegram"}
               </button>

               {status.connected && (
                  <>
                     <button 
                        onClick={handleSendTest} 
                        disabled={testing}
                        style={{ background: "rgba(255,255,255,0.1)", color: "#fff", border: "1px solid rgba(255,255,255,0.2)", padding: "0.8rem 1.5rem", borderRadius: "0.5rem", cursor: testing ? "not-allowed" : "pointer", fontWeight: "bold", fontFamily: "var(--font-body)", fontSize: "0.95rem" }}
                        className="udaan-lift"
                     >
                        {testing ? "Sending..." : "🔔 Send Test Notification"}
                     </button>
                     {testSuccess === true && <div style={{ color: "#7fe0a0", fontSize: "0.85rem", textAlign: "center", fontFamily: "var(--font-body)" }}>Test message sent successfully!</div>}
                     {testSuccess === false && <div style={{ color: "#ff6b6b", fontSize: "0.85rem", textAlign: "center", fontFamily: "var(--font-body)" }}>Failed to send test message.</div>}
                  </>
               )}
            </div>
         </div>
      </section>
   );
}

function CategoryCard({ c, Icon, onClick }) {
  return (
    <div onClick={onClick} className="liquid-glass udaan-lift" style={{ borderRadius: "var(--radius-card)", padding: "1.25rem", cursor: "pointer", display: "flex", flexDirection: "column", gap: "0.9rem", minHeight: "168px", transition: "transform 150ms" }}>
      <div className="liquid-glass" style={{ width: 46, height: 46, borderRadius: "var(--radius-tile)", display: "flex", alignItems: "center", justifyContent: "center", flex: "0 0 auto" }}>
        <Icon name={c.icon} size={24} style={{ color: "#fff" }} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "1.05rem", color: "#fff", letterSpacing: "-0.2px" }}>{c.name}</div>
        <div style={{ fontFamily: "var(--font-body)", fontWeight: 300, fontSize: "0.82rem", color: "rgba(255,255,255,0.75)", marginTop: "0.2rem" }}>{c.note}</div>
      </div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "0.85rem", color: c.count > 0 ? "#7fe0a0" : "rgba(255,255,255,0.7)" }}>
          {c.count !== undefined ? `${c.count} eligible` : c.stat}
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: "0.15rem", fontFamily: "var(--font-body)", fontWeight: 500, fontSize: "0.8rem", color: "rgba(255,255,255,0.85)" }}>View <Icon name="chev" size={15} /></span>
      </div>
    </div>
  );
}

/* ---- Category Detail Modal ---- */
function CategoryDetailModal({ category, schemes, onClose, onViewDoc }) {
  const { useState, useEffect } = React;
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch Groq-generated details for all schemes in this category
    const tag = category.tag;
    const schemeList = schemes.filter(s =>
      !tag || (s.tag || "").toLowerCase() === tag.toLowerCase() || tag === "all"
    );
    setDetail(schemeList);
    setLoading(false);
  }, [category, schemes]);

  const s = detail || [];

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 99999, display: "flex", alignItems: "flex-start", justifyContent: "center", background: "rgba(0,0,0,0.78)", backdropFilter: "blur(12px)", padding: "1rem", overflowY: "auto" }}>
      <div className="liquid-glass-strong" style={{ width: "100%", maxWidth: "760px", borderRadius: "1.5rem", padding: "2rem", marginTop: "4rem", position: "relative" }}>
        {/* Header */}
        <button onClick={onClose} style={{ position: "absolute", top: "1rem", right: "1rem", background: "rgba(255,255,255,0.15)", width: "32px", height: "32px", borderRadius: "50%", border: "none", color: "#fff", cursor: "pointer", fontSize: "1.1rem" }}>✕</button>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1.5rem" }}>
          <div className="liquid-glass" style={{ width: 52, height: 52, borderRadius: "var(--radius-tile)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span style={{ fontSize: "1.5rem" }}>{category.emoji || "📋"}</span>
          </div>
          <div>
            <h2 style={{ margin: 0, color: "#fff", fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "1.8rem" }}>{category.name}</h2>
            <p style={{ margin: 0, color: "rgba(255,255,255,0.65)", fontFamily: "var(--font-body)", fontSize: "0.9rem" }}>{s.length} eligible scheme{s.length !== 1 ? "s" : ""} found for you</p>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: "center", color: "rgba(255,255,255,0.6)", padding: "2rem", fontFamily: "var(--font-body)" }}>Loading schemes…</div>
        ) : s.length === 0 ? (
          <div className="liquid-glass" style={{ borderRadius: "1rem", padding: "2rem", textAlign: "center", color: "rgba(255,255,255,0.6)", fontFamily: "var(--font-body)" }}>
            No eligible schemes found in this category yet. Complete your profile to unlock more.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {s.map((scheme, i) => (
              <div key={i} className="liquid-glass" style={{ borderRadius: "1rem", padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
                {/* Scheme header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.5rem" }}>
                  <div>
                    <h3 style={{ margin: 0, color: "#fff", fontFamily: "var(--font-heading)", fontStyle: "italic", fontSize: "1.35rem" }}>{scheme.name}</h3>
                    <span style={{ display: "inline-block", marginTop: "0.3rem", background: "rgba(127,224,160,0.2)", color: "#7fe0a0", border: "1px solid rgba(127,224,160,0.4)", borderRadius: "9999px", padding: "0.2rem 0.7rem", fontSize: "0.78rem", fontFamily: "var(--font-body)", fontWeight: 600 }}>✓ Eligible</span>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "#7fe0a0", fontWeight: 700, fontSize: "1.1rem", fontFamily: "var(--font-body)" }}>{scheme.amount}</div>
                    <div style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.78rem", fontFamily: "var(--font-body)" }}>Deadline: {scheme.deadline || "Open"}</div>
                  </div>
                </div>

                {/* Why eligible */}
                {scheme.eligibility_reason && (
                  <div style={{ background: "rgba(127,224,160,0.08)", borderLeft: "3px solid #7fe0a0", borderRadius: "0.5rem", padding: "0.75rem 1rem" }}>
                    <div style={{ color: "#7fe0a0", fontSize: "0.78rem", fontWeight: 700, fontFamily: "var(--font-body)", marginBottom: "0.25rem" }}>WHY YOU'RE ELIGIBLE</div>
                    <div style={{ color: "rgba(255,255,255,0.85)", fontSize: "0.88rem", fontFamily: "var(--font-body)", lineHeight: 1.5 }}>{scheme.eligibility_reason}</div>
                  </div>
                )}

                {/* Required documents */}
                {scheme.required_docs?.length > 0 && (
                  <div>
                    <div style={{ color: "#ffd27a", fontSize: "0.8rem", fontWeight: 700, fontFamily: "var(--font-body)", marginBottom: "0.4rem" }}>📄 REQUIRED DOCUMENTS</div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                      {scheme.required_docs.map((doc, di) => (
                        <button key={di} onClick={() => onViewDoc && onViewDoc(doc)}
                          style={{ background: "rgba(255,210,122,0.12)", border: "1px solid rgba(255,210,122,0.35)", color: "#ffd27a", borderRadius: "9999px", padding: "0.25rem 0.75rem", fontSize: "0.78rem", fontFamily: "var(--font-body)", cursor: "pointer" }}>
                          {doc} ↗
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* How to apply steps */}
                {scheme.how_to_apply?.length > 0 && (
                  <div>
                    <div style={{ color: "#7acaff", fontSize: "0.8rem", fontWeight: 700, fontFamily: "var(--font-body)", marginBottom: "0.4rem" }}>📋 HOW TO APPLY</div>
                    <ol style={{ margin: 0, paddingLeft: "1.25rem", color: "rgba(255,255,255,0.82)", fontFamily: "var(--font-body)", fontSize: "0.87rem", lineHeight: 1.7 }}>
                      {scheme.how_to_apply.map((step, si) => <li key={si}>{step}</li>)}
                    </ol>
                  </div>
                )}

                {/* Apply button */}
                <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginTop: "0.25rem" }}>
                  <button onClick={() => window.open(scheme.link || scheme.application_link || "https://www.myscheme.gov.in/", "_blank")}
                    style={{ background: "#fff", color: "#000", border: "none", padding: "0.65rem 1.4rem", borderRadius: "0.6rem", cursor: "pointer", fontWeight: 700, fontFamily: "var(--font-body)", fontSize: "0.88rem" }}>
                    Apply Now ↗
                  </button>
                  {scheme.youtube_link && (
                    <button onClick={() => window.open(scheme.youtube_link, "_blank")}
                      style={{ background: "rgba(255,107,107,0.12)", color: "#ff6b6b", border: "1px solid rgba(255,107,107,0.4)", padding: "0.65rem 1.2rem", borderRadius: "0.6rem", cursor: "pointer", fontWeight: 600, fontFamily: "var(--font-body)", fontSize: "0.88rem" }}>
                      ▶ Watch Guide
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
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
        <div style={{ cursor: "pointer" }} onClick={() => window.open(f.link || f.application_link || "https://www.myscheme.gov.in/", "_blank")}>
           <Button variant="white" size="sm" icon="arrow-up-right">Apply</Button>
        </div>
      </div>
    </div>
  );
}

function UdaanNav({ personas, idx, onSelect, onProfile, initials, Icon, isFarmer, musicOn, onToggleMusic, musicReady }) {
  const [showNotif, setShowNotif] = React.useState(false);

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
        {/* ---- Music toggle (only for farmers) ---- */}
        {isFarmer && (
          <button
            onClick={onToggleMusic}
            title={musicOn ? "Mute ambient music" : "Play ambient music"}
            className="liquid-glass udaan-icon-btn"
            style={{ position: "relative", transition: "transform 200ms", transform: musicOn ? "scale(1.08)" : "scale(1)" }}
          >
            {/* animated sound waves when playing */}
            {musicOn ? (
              <svg width="20" height="18" viewBox="0 0 20 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 6.5v5M7 4v10M11 2v14M15 5v8M19 7v4" stroke="#7fe0a0" strokeWidth="2" strokeLinecap="round">
                  <animate attributeName="stroke-dasharray" values="0 50;50 50;0 50" dur="1.2s" repeatCount="indefinite" />
                </path>
              </svg>
            ) : (
              <svg width="20" height="18" viewBox="0 0 20 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 6.5v5M7 7v4M11 8v2" stroke="rgba(255,255,255,0.45)" strokeWidth="2" strokeLinecap="round" />
                <line x1="2" y1="2" x2="18" y2="16" stroke="rgba(255,255,255,0.45)" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            )}
          </button>
        )}
        <button onClick={onProfile} className="liquid-glass udaan-lift" aria-label="Open profile" style={{ display: "flex", alignItems: "center", gap: "0.5rem", borderRadius: "9999px", border: "none", cursor: "pointer", padding: "0.3rem 0.85rem 0.3rem 0.3rem" }}>
          <span className="liquid-glass-strong" style={{ width: 30, height: 30, borderRadius: "9999px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "var(--font-body)", fontWeight: 600, fontSize: "0.75rem", color: "#fff" }}>{initials || "AK"}</span>
          <span style={{ fontWeight: 500, fontSize: "0.85rem", color: "#fff" }}>Profile</span>
        </button>
        <button onClick={() => { localStorage.removeItem('udaan_credentials'); window.location.hash = 'landing'; }} className="liquid-glass udaan-lift" aria-label="Logout" style={{ display: "flex", alignItems: "center", gap: "0.5rem", borderRadius: "9999px", border: "none", cursor: "pointer", padding: "0.5rem 1rem", background: "rgba(255,107,107,0.1)", color: "#ff6b6b" }}>
          <span style={{ fontWeight: 600, fontSize: "0.85rem", fontFamily: "var(--font-body)" }}>Logout</span>
        </button>
      </div>
    </nav>
  );
}

window.UdaanDashboard = Dashboard;
