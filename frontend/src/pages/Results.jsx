import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useRecommendations } from "../hooks/useRecommendations.js";
import MusicSection    from "../components/Recommendations/MusicSection.jsx";
import MovieSection    from "../components/Recommendations/MovieSection.jsx";
import BookSection     from "../components/Recommendations/BookSection.jsx";
import FoodSection     from "../components/Recommendations/FoodSection.jsx";
import ActivitySection from "../components/Recommendations/ActivitySection.jsx";
import ContrastToggle  from "../components/Controls/ContrastToggle.jsx";

const EMOTION_EMOJI = { sadness:"😢", joy:"😊", anger:"😠", fear:"😨", love:"🥰", surprise:"😲" };
const EMOTION_MSG   = {
  sadness:"Wrapping you in comfort", joy:"Riding that wave of happiness",
  anger:"Channel that energy",       fear:"Finding your calm",
  love:"Celebrating the warmth",     surprise:"Embracing the unexpected",
};

// Podcast section inline
function PodcastSection({ items = [], loading }) {
  if (!loading && items.length === 0) return null;
  return (
    <section className="mb-10 animate-fade-up">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-2xl">🎙️</span>
        <h3 className="font-display text-xl font-semibold" style={{ color:"var(--blush)" }}>Podcasts</h3>
        {!loading && <span className="text-xs px-2 py-0.5 rounded-full ml-auto" style={{background:"rgba(237,158,89,0.12)",color:"var(--amber)"}}>{items.length} picks</span>}
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {loading
          ? [...Array(4)].map((_,i) => <div key={i} className="rec-card h-44 shimmer" />)
          : items.map((item, i) => (
              <a key={i} href={item.url || "#"} target="_blank" rel="noopener noreferrer"
                className="rec-card block p-4 group" style={{ textDecoration:"none" }}>
                <div style={{
                  height:80, borderRadius:10, marginBottom:10,
                  background:"linear-gradient(135deg,var(--velvet),var(--rose))",
                  display:"flex", alignItems:"center", justifyContent:"center", fontSize:32
                }}>🎙️</div>
                <h4 style={{fontWeight:600,fontSize:13,color:"var(--blush)",marginBottom:4,
                  display:"-webkit-box",WebkitLineClamp:2,WebkitBoxOrient:"vertical",overflow:"hidden"}}>
                  {item.title}
                </h4>
                {item.podcast && <p style={{fontSize:11,opacity:0.5,color:"var(--blush)"}}>{item.podcast}</p>}
              </a>
            ))
        }
      </div>
    </section>
  );
}

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const { emotion, moodLogId, mode: initMode } = location.state || {};

  // Track current mode locally so toggle works
  const [currentMode, setCurrentMode] = useState(initMode || "amplify");

  const { recs, loading, error, fetch } = useRecommendations();

  // Fetch on mount
  useEffect(() => {
    if (emotion && moodLogId) {
      fetch(moodLogId, emotion, currentMode);
    }
  }, []); // only on mount

  // Handle mode toggle — always re-fetch with new mode
  const handleModeChange = (newMode) => {
    if (newMode === currentMode) return; // no change
    setCurrentMode(newMode);
    fetch(moodLogId, emotion, newMode);
  };

  if (!emotion) return (
    <div style={{ minHeight:"100vh", display:"flex", alignItems:"center", justifyContent:"center" }}>
      <div className="glass p-10 text-center">
        <p style={{ fontSize:18, marginBottom:16, color:"var(--blush)" }}>No mood detected yet.</p>
        <button className="btn-primary px-8 py-3" onClick={() => navigate("/")}>Back to Home</button>
      </div>
    </div>
  );

  return (
    <div style={{ minHeight:"100vh", paddingTop:96, paddingBottom:64, paddingLeft:24, paddingRight:24 }}>
      <div style={{ maxWidth:1200, margin:"0 auto" }}>

        {/* Header */}
        <div className="text-center animate-fade-up" style={{ marginBottom:40 }}>
          <div style={{ fontSize:72, marginBottom:16 }} className="animate-float">
            {EMOTION_EMOJI[emotion] || "🎭"}
          </div>
          <h1 className="font-display" style={{ fontSize:"clamp(2rem,4vw,3rem)", fontWeight:700, color:"var(--blush)", marginBottom:10 }}>
            {EMOTION_MSG[emotion] || "Your vibe"}
          </h1>
          <div style={{ display:"flex", alignItems:"center", justifyContent:"center", gap:12 }}>
            <span className="emotion-badge" style={{ textTransform:"capitalize" }}>{emotion}</span>
            <span style={{ fontSize:13, opacity:0.4, color:"var(--blush)" }}>
              {currentMode === "contrast" ? "↭ Shifting your mood" : "✦ Matching your mood"}
            </span>
          </div>
        </div>

        {/* Mode toggle */}
        <div className="flex justify-center mb-6 animate-fade-up delay-100">
          <ContrastToggle mode={currentMode} onChange={handleModeChange} />
        </div>



        {/* AI note */}
        {recs?.note && !loading && (
          <div className="glass p-6 mb-8 text-center animate-fade-up">
            <p style={{ fontSize:15, lineHeight:1.8, opacity:0.75, fontStyle:"italic", color:"var(--blush)" }}>
              "{recs.note}"
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="glass p-4 mb-6 text-center">
            <p style={{ fontSize:13, color:"var(--rose)" }}>{error}</p>
            <p style={{ fontSize:11, opacity:0.4, marginTop:4, color:"var(--blush)" }}>
              Check your backend .env for API keys
            </p>
          </div>
        )}

        {/* Sections */}
        <MusicSection    items={recs?.music}           loading={loading} />
        <MovieSection    movies={recs?.movies}         tvShows={recs?.tv_shows}  loading={loading} />
        <BookSection     items={recs?.books}           loading={loading} />
        <FoodSection     items={recs?.food}            loading={loading} />
        <PodcastSection  items={recs?.podcasts}        loading={loading} />
        <ActivitySection activities={recs?.activities} loading={loading} />

        <div className="text-center" style={{ marginTop:40 }}>
          <button className="btn-ghost px-8 py-3" onClick={() => navigate("/")}>← Try Again</button>
        </div>
      </div>
    </div>
  );
}