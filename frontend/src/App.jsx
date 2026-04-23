import { BrowserRouter, Routes, Route, Link, useLocation, useNavigate } from "react-router-dom";
import { Component, useState } from "react";
import { AuthProvider, useAuth } from "./hooks/useAuth.jsx";
import AuthModal from "./components/Auth/AuthModal.jsx";
import Home    from "./pages/Home.jsx";
import Results from "./pages/Results.jsx";
import Journey from "./pages/Journey.jsx";

// ── Auth Gate — wraps entire app, shows login first ───────────────────────────
function AuthGate({ children }) {
  const { isLoggedIn } = useAuth();
  const navigate       = useNavigate();

  if (!isLoggedIn) {
    return (
      <div style={{ minHeight:"100vh", display:"flex", alignItems:"center", justifyContent:"center" }}>
        {/* Background orbs visible behind modal */}
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
        <AuthModal
          onClose={null}          /* no skip — must login */
          onSuccess={() => navigate("/")}
        />
      </div>
    );
  }

  return children;
}

// ── Protected Route (for Journey) ─────────────────────────────────────────────
function ProtectedRoute({ children }) {
  const { isLoggedIn } = useAuth();
  const navigate       = useNavigate();

  if (!isLoggedIn) {
    return (
      <AuthModal
        onClose={() => navigate("/")}
        onSuccess={() => navigate("/journey")}
      />
    );
  }
  return children;
}

// ── Navbar ────────────────────────────────────────────────────────────────────
function Navbar() {
  const { pathname }                 = useLocation();
  const navigate                     = useNavigate();
  const { user, logout, isLoggedIn } = useAuth();
  const [showMenu, setShowMenu]      = useState(false);

  const linkStyle = (path) => ({
    padding:"8px 18px", borderRadius:50, fontSize:13, fontWeight:500,
    textDecoration:"none", transition:"all 0.3s",
    background: pathname === path
      ? "linear-gradient(135deg,var(--amber),var(--rose))"
      : "transparent",
    color: pathname === path ? "var(--night)" : "var(--blush)",
    border: pathname === path ? "none" : "1.5px solid rgba(233,188,185,0.22)",
  });

  if (!isLoggedIn) return null; // hide navbar on auth screen

  return (
    <nav style={{ position:"fixed", top:0, left:0, right:0, zIndex:50, padding:"12px 16px" }}>
      <div style={{
        maxWidth:1100, margin:"0 auto",
        background:"rgba(68,23,78,0.3)",
        backdropFilter:"blur(16px)",
        WebkitBackdropFilter:"blur(16px)",
        border:"1px solid rgba(233,188,185,0.12)",
        borderRadius:50,
        display:"flex", alignItems:"center", justifyContent:"space-between",
        padding:"10px 24px",
      }}>
        {/* Logo */}
        <Link to="/" style={{ display:"flex", alignItems:"center", gap:8, textDecoration:"none" }}>
          <span style={{ fontSize:22 }}>🎭</span>
          <span style={{ fontFamily:"'Playfair Display',serif", fontSize:20, fontWeight:600, color:"var(--blush)" }}>
            Moodly
          </span>
        </Link>

        {/* Links */}
        <div style={{ display:"flex", alignItems:"center", gap:6 }}>
          <Link to="/" style={linkStyle("/")}>✦ Discover</Link>

          {/* Username dropdown */}
          <div style={{ position:"relative" }}>
            <button onClick={() => setShowMenu(!showMenu)} style={{
              padding:"8px 16px", borderRadius:50, fontSize:13, fontWeight:500,
              background:"rgba(237,158,89,0.15)",
              border:"1.5px solid rgba(237,158,89,0.3)",
              color:"var(--amber)", cursor:"pointer",
              display:"flex", alignItems:"center", gap:8,
            }}>
              <span style={{
                width:24, height:24, borderRadius:"50%",
                background:"linear-gradient(135deg,var(--amber),var(--rose))",
                display:"inline-flex", alignItems:"center", justifyContent:"center",
                fontSize:11, fontWeight:700, color:"var(--night)", flexShrink:0,
              }}>
                {(user?.username?.[0] || "U").toUpperCase()}
              </span>
              {user?.username}
            </button>

            {showMenu && (
              <div style={{
                position:"absolute", top:"calc(100% + 10px)", right:0,
                minWidth:170, padding:8, borderRadius:14, zIndex:100,
                background:"rgba(27,25,49,0.97)",
                backdropFilter:"blur(16px)",
                border:"1px solid rgba(233,188,185,0.12)",
                boxShadow:"0 8px 32px rgba(0,0,0,0.4)",
              }}>
                <div style={{ padding:"8px 14px 10px", borderBottom:"1px solid rgba(233,188,185,0.08)", marginBottom:6 }}>
                  <p style={{ fontSize:13, fontWeight:600, color:"var(--blush)" }}>{user?.username}</p>
                  <p style={{ fontSize:11, opacity:0.4, color:"var(--blush)", marginTop:2 }}>{user?.email}</p>
                </div>
                <button onClick={() => { navigate("/journey"); setShowMenu(false); }} style={{
                  width:"100%", textAlign:"left", padding:"8px 14px", fontSize:13,
                  color:"var(--blush)", background:"transparent", border:"none",
                  cursor:"pointer", borderRadius:8,
                }}>◈ My Journey</button>
                <hr style={{ border:"none", borderTop:"1px solid rgba(233,188,185,0.08)", margin:"4px 0" }} />
                <button onClick={() => { logout(); setShowMenu(false); navigate("/"); }} style={{
                  width:"100%", textAlign:"left", padding:"8px 14px", fontSize:13,
                  color:"var(--rose)", background:"transparent", border:"none",
                  cursor:"pointer", borderRadius:8,
                }}>↩ Sign Out</button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

// ── Error boundary ────────────────────────────────────────────────────────────
class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(e) { return { error: e }; }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding:40, color:"#E9BCB9", fontFamily:"monospace", maxWidth:800, margin:"80px auto" }}>
          <h2 style={{ color:"#ED9E59", marginBottom:12, fontFamily:"'Playfair Display',serif" }}>⚠ Error</h2>
          <pre style={{ background:"rgba(255,255,255,0.05)", padding:20, borderRadius:12,
            whiteSpace:"pre-wrap", fontSize:12, lineHeight:1.6 }}>
            {this.state.error?.message}{"\n\n"}{this.state.error?.stack}
          </pre>
          <button style={{ marginTop:20, padding:"10px 24px", background:"#ED9E59",
            color:"#1B1931", borderRadius:50, border:"none", cursor:"pointer", fontWeight:600 }}
            onClick={() => this.setState({ error: null })}>Retry</button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ── Inner app ─────────────────────────────────────────────────────────────────
function InnerApp() {
  return (
    <AuthGate>
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />
      <div style={{ position:"relative", zIndex:10, minHeight:"100vh" }}>
        <Navbar />
        <Routes>
          <Route path="/"        element={<ErrorBoundary><Home /></ErrorBoundary>} />
          <Route path="/results" element={<ErrorBoundary><Results /></ErrorBoundary>} />
          <Route path="/journey" element={
            <ErrorBoundary>
              <ProtectedRoute>
                <Journey />
              </ProtectedRoute>
            </ErrorBoundary>
          } />
        </Routes>
      </div>
    </AuthGate>
  );
}

// ── Root ──────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <InnerApp />
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}