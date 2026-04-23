import { useEffect, useState } from "react";
import { getMoodHistory, getMoodSummary } from "../services/api.js";
import { useAuth } from "../hooks/useAuth.jsx";
import JourneyChart  from "../components/MoodJourney/JourneyChart.jsx";
import MoodHistory   from "../components/MoodJourney/MoodHistory.jsx";
import TrendingMoods from "../components/SocialMood/TrendingMoods.jsx";
import MoodPulse     from "../components/SocialMood/MoodPulse.jsx";
import AuthModal     from "../components/Auth/AuthModal.jsx";

const SESSION_KEY   = "moodly_session";
const DAYS_OPTS     = [7, 14, 30];
const EMOTION_EMOJI = { sadness:"😢", joy:"😊", anger:"😠", fear:"😨", love:"🥰", surprise:"😲" };

export default function Journey() {
  const { user, isLoggedIn } = useAuth();
  const sessionId = (() => { try { return localStorage.getItem(SESSION_KEY) || ""; } catch { return ""; } })();

  const [history,   setHistory]   = useState([]);
  const [summary,   setSummary]   = useState([]);
  const [days,      setDays]      = useState(7);
  const [loading,   setLoading]   = useState(true);
  const [tab,       setTab]       = useState("journey");
  const [showAuth,  setShowAuth]  = useState(false);

  useEffect(() => {
    if (!isLoggedIn && !sessionId) { setLoading(false); return; }
    setLoading(true);
    const params = isLoggedIn ? {} : { session_id: sessionId };
    Promise.all([
      getMoodHistory(params.session_id, days),
      getMoodSummary(params.session_id),
    ])
      .then(([h, s]) => {
        setHistory(h.data.history || []);
        setSummary(s.data.summary || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [isLoggedIn, days]);

  const dominant = summary[0];

  return (
    <div style={{ minHeight:"100vh", paddingTop:96, paddingBottom:64, paddingLeft:24, paddingRight:24 }}>
      <div style={{ maxWidth:1000, margin:"0 auto" }}>

        {/* Header */}
        <div className="text-center animate-fade-up" style={{ marginBottom:36 }}>
          <h1 className="font-display" style={{ fontSize:"clamp(2rem,4vw,3rem)", fontWeight:700, color:"var(--blush)", marginBottom:8 }}>
            {isLoggedIn ? `${user.username}'s Journey` : "Your Mood Journey"}
          </h1>
          <p style={{ fontSize:14, opacity:0.4, color:"var(--blush)" }}>
            {isLoggedIn
              ? "Your complete mood history, synced across devices"
              : "Track how your emotions evolve over time"}
          </p>
        </div>

        {/* Auth banner — shown when not logged in */}
        {!isLoggedIn && (
          <div className="glass animate-fade-up delay-100" style={{
            padding:"16px 24px", marginBottom:28,
            display:"flex", alignItems:"center", justifyContent:"space-between",
            border:"1px solid rgba(237,158,89,0.25)", gap:16, flexWrap:"wrap",
          }}>
            <div>
              <p style={{ fontSize:14, fontWeight:600, color:"var(--amber)", marginBottom:3 }}>
                ✦ Save your journey permanently
              </p>
              <p style={{ fontSize:12, opacity:0.5, color:"var(--blush)" }}>
                Create a free account to track moods across sessions and devices
              </p>
            </div>
            <button className="btn-primary" style={{ padding:"9px 22px", fontSize:13, flexShrink:0 }}
              onClick={() => setShowAuth(true)}>
              Sign Up Free →
            </button>
          </div>
        )}

        {/* Page tabs */}
        <div className="flex justify-center animate-fade-up delay-100" style={{ marginBottom:32 }}>
          <div className="glass p-1 inline-flex rounded-full gap-1">
            {[{ key:"journey", label:"◈ Journey" }, { key:"community", label:"❋ Community" }].map(({ key, label }) => (
              <button key={key} onClick={() => setTab(key)}
                className={key === tab ? "tab-active" : ""}
                style={{
                  padding:"8px 24px", fontSize:14, fontWeight:500, borderRadius:50,
                  background:"transparent", border:"none", cursor:"pointer",
                  color: key === tab ? "var(--night)" : "var(--blush)",
                  opacity: key !== tab ? 0.5 : 1, transition:"all 0.3s",
                }}>
                {label}
              </button>
            ))}
          </div>
        </div>

        {tab === "journey" && (
          <>
            {/* Summary cards */}
            {summary.length > 0 && (
              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(140px,1fr))", gap:12, marginBottom:28 }}
                className="animate-fade-up delay-200">
                {summary.slice(0,6).map(s => (
                  <div key={s.emotion} className="glass p-4 text-center">
                    <span style={{ fontSize:32, display:"block", marginBottom:4 }}>{EMOTION_EMOJI[s.emotion] || "✦"}</span>
                    <p style={{ textTransform:"capitalize", fontWeight:600, fontSize:13, color:"var(--blush)", marginBottom:2 }}>{s.emotion}</p>
                    <p className="font-display" style={{ fontSize:24, fontWeight:700, color:"var(--amber)" }}>{s.percentage}%</p>
                    <p style={{ fontSize:11, opacity:0.35, color:"var(--blush)" }}>{s.count} entries</p>
                  </div>
                ))}
              </div>
            )}

            {/* Dominant mood */}
            {dominant && (
              <div className="glass animate-fade-up delay-200" style={{ padding:20, marginBottom:20, display:"flex", alignItems:"center", gap:16 }}>
                <span style={{ fontSize:44 }}>{EMOTION_EMOJI[dominant.emotion]}</span>
                <div>
                  <p style={{ fontSize:11, opacity:0.4, textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:4, color:"var(--blush)" }}>
                    Dominant mood
                  </p>
                  <p className="font-display" style={{ fontSize:26, fontWeight:600, textTransform:"capitalize", color:"var(--amber)" }}>
                    {dominant.emotion}
                  </p>
                </div>
                <div style={{ marginLeft:"auto", textAlign:"right" }}>
                  <p className="font-display" style={{ fontSize:36, fontWeight:700, color:"var(--blush)" }}>{dominant.percentage}%</p>
                  <p style={{ fontSize:11, opacity:0.35, color:"var(--blush)" }}>of the time</p>
                </div>
              </div>
            )}

            {/* Days filter */}
            <div style={{ display:"flex", gap:8, marginBottom:20 }} className="animate-fade-up delay-300">
              {DAYS_OPTS.map(d => (
                <button key={d} onClick={() => setDays(d)}
                  className={days === d ? "tab-active btn-primary" : "btn-ghost"}
                  style={{ padding:"6px 18px", fontSize:13 }}>
                  {d}d
                </button>
              ))}
            </div>

            {/* Chart */}
            {loading
              ? <div className="glass shimmer" style={{ height:220, marginBottom:20 }} />
              : <JourneyChart history={history} />
            }

            {/* History */}
            {loading
              ? <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
                  {[...Array(5)].map((_,i) => <div key={i} className="glass shimmer" style={{ height:60 }} />)}
                </div>
              : history.length > 0
                ? <MoodHistory history={history} />
                : (
                  <div className="glass p-10 text-center">
                    <span style={{ fontSize:40, display:"block", marginBottom:12, opacity:0.2 }}>◈</span>
                    <p style={{ opacity:0.35, fontSize:14, color:"var(--blush)", marginBottom:16 }}>
                      No mood entries yet. Start by sharing how you feel.
                    </p>
                  </div>
                )
            }
          </>
        )}

        {tab === "community" && (
          <div style={{ display:"flex", flexDirection:"column", gap:20 }} className="animate-fade-in">
            <TrendingMoods />
            <MoodPulse />
          </div>
        )}
      </div>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </div>
  );
}