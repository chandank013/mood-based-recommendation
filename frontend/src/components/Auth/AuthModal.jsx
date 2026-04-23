import { useState } from "react";
import { useAuth } from "../../hooks/useAuth.jsx";

export default function AuthModal({ onClose, onSuccess }) {
  const [mode,       setMode]       = useState("login");
  const [email,      setEmail]      = useState("");
  const [password,   setPassword]   = useState("");
  const [username,   setUsername]   = useState("");
  const [localErr,   setLocalErr]   = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const { login, register, loading, error, clearError } = useAuth();

  const switchMode = (m) => {
    setMode(m); setLocalErr(""); setSuccessMsg(""); clearError();
    setEmail(""); setPassword(""); setUsername("");
  };

  const handleSubmit = async () => {
    setLocalErr(""); setSuccessMsg("");
    if (!email || !password)
      return setLocalErr("Please fill all fields");
    if (mode === "register" && !username)
      return setLocalErr("Username is required");
    if (mode === "register" && password.length < 6)
      return setLocalErr("Password must be at least 6 characters");

    if (mode === "login") {
      // Login → fire onSuccess after state settles
      await login(email, password, onSuccess);
    } else {
      // Register → don't auto-login, redirect to login tab
      const result = await register(username, email, password);
      if (result.success) {
        const registeredEmail = email;
        setUsername(""); setPassword("");
        setMode("login");
        setEmail(registeredEmail); // pre-fill email
        clearError();
        setSuccessMsg("✓ Account created! Please sign in to continue.");
      }
    }
  };

  const displayError = localErr || error;

  return (
    <div style={{
      position:"fixed", inset:0, zIndex:200,
      display:"flex", alignItems:"center", justifyContent:"center",
      background:"rgba(27,25,49,0.93)", backdropFilter:"blur(14px)",
    }}>
      <div style={{
        width:"100%", maxWidth:420, padding:36, margin:16,
        background:"rgba(68,23,78,0.5)",
        backdropFilter:"blur(20px)",
        WebkitBackdropFilter:"blur(20px)",
        border:"1px solid rgba(233,188,185,0.15)",
        borderRadius:24,
        boxShadow:"0 24px 64px rgba(0,0,0,0.5)",
      }}>

        {/* Header */}
        <div style={{ textAlign:"center", marginBottom:28 }}>
          <span style={{ fontSize:44, display:"block", marginBottom:10 }}>🎭</span>
          <h2 style={{ fontFamily:"'Playfair Display',serif", fontSize:26, fontWeight:700,
            color:"var(--blush)", marginBottom:6 }}>
            {mode === "login" ? "Welcome back" : "Join Moodly"}
          </h2>
          <p style={{ fontSize:13, opacity:0.45, color:"var(--blush)" }}>
            {mode === "login"
              ? "Sign in to access your mood journey"
              : "Create a free account to get started"}
          </p>
        </div>

        {/* Tab toggle */}
        <div style={{
          display:"flex", gap:4, padding:4,
          background:"rgba(27,25,49,0.5)",
          borderRadius:50, marginBottom:24,
          border:"1px solid rgba(233,188,185,0.1)",
        }}>
          {[{ key:"login", label:"Sign In" }, { key:"register", label:"Register" }].map(({ key, label }) => (
            <button key={key} onClick={() => switchMode(key)} style={{
              flex:1, padding:"9px 0", fontSize:13, fontWeight:500,
              borderRadius:50, border:"none", cursor:"pointer", transition:"all 0.3s",
              background: key === mode
                ? "linear-gradient(135deg,var(--amber),var(--rose))"
                : "transparent",
              color: key === mode ? "var(--night)" : "var(--blush)",
              opacity: key !== mode ? 0.5 : 1,
            }}>
              {label}
            </button>
          ))}
        </div>

        {/* Fields */}
        <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
          {mode === "register" && (
            <div>
              <label style={{ fontSize:12, opacity:0.5, color:"var(--blush)", display:"block", marginBottom:6 }}>
                Username
              </label>
              <input className="mood-input" style={{ width:"100%", padding:"12px 14px" }}
                type="text" placeholder="e.g. moodmaster"
                value={username} onChange={e => setUsername(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleSubmit()} />
            </div>
          )}

          <div>
            <label style={{ fontSize:12, opacity:0.5, color:"var(--blush)", display:"block", marginBottom:6 }}>
              Email
            </label>
            <input className="mood-input" style={{ width:"100%", padding:"12px 14px" }}
              type="email" placeholder="you@example.com"
              value={email} onChange={e => setEmail(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSubmit()} />
          </div>

          <div>
            <label style={{ fontSize:12, opacity:0.5, color:"var(--blush)", display:"block", marginBottom:6 }}>
              Password
            </label>
            <input className="mood-input" style={{ width:"100%", padding:"12px 14px" }}
              type="password"
              placeholder={mode === "register" ? "Min 6 characters" : "Your password"}
              value={password} onChange={e => setPassword(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSubmit()} />
          </div>
        </div>

        {/* Success message */}
        {successMsg && (
          <p style={{ marginTop:12, fontSize:12, textAlign:"center",
            color:"#4ade80", padding:"8px 12px", borderRadius:8,
            background:"rgba(74,222,128,0.08)", border:"1px solid rgba(74,222,128,0.2)" }}>
            {successMsg}
          </p>
        )}

        {/* Error */}
        {displayError && !successMsg && (
          <p style={{ marginTop:12, fontSize:12, color:"var(--rose)", textAlign:"center" }}>
            ⚠ {displayError}
          </p>
        )}

        {/* Submit */}
        <button onClick={handleSubmit} disabled={loading} style={{
          width:"100%", padding:"14px 0", marginTop:20, fontSize:15,
          fontWeight:600, borderRadius:50, border:"none", cursor:"pointer",
          background:"linear-gradient(135deg,var(--amber),var(--rose))",
          color:"var(--night)", opacity: loading ? 0.6 : 1,
          transition:"all 0.3s",
          boxShadow:"0 4px 20px rgba(237,158,89,0.3)",
        }}>
          {loading
            ? "Please wait..."
            : mode === "login" ? "Sign In ✦" : "Create Account ✦"}
        </button>

        {/* Go back — only when skippable */}
        {onClose && (
          <button onClick={onClose} style={{
            width:"100%", marginTop:10, padding:"10px 0", fontSize:13,
            background:"transparent", border:"none", cursor:"pointer",
            color:"var(--blush)", opacity:0.35,
          }}>
            ← Go back
          </button>
        )}
      </div>
    </div>
  );
}