import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMoodDetection }   from "../hooks/useMoodDetection.js";
import TextInput      from "../components/MoodInput/TextInput.jsx";
import EmojiPicker    from "../components/MoodInput/EmojiPicker.jsx";
import SliderInput    from "../components/MoodInput/SliderInput.jsx";
import WebcamCapture  from "../components/MoodInput/WebcamCapture.jsx";
import VoiceCapture   from "../components/MoodInput/VoiceCapture.jsx";
import WearableInput  from "../components/MoodInput/WearableInput.jsx";
import MoodBlend      from "../components/MoodInput/MoodBlend.jsx";
import ContrastToggle from "../components/Controls/ContrastToggle.jsx";
import ContextPanel   from "../components/Controls/ContextPanel.jsx";

const TABS = [
  { key: "text",     icon: "✍️",  label: "Text"     },
  { key: "emoji",    icon: "😊",  label: "Emoji"    },
  { key: "slider",   icon: "🎚️", label: "Sliders"  },
  { key: "webcam",   icon: "📷",  label: "Camera"   },
  { key: "voice",    icon: "🎙️", label: "Voice"    },
  { key: "wearable", icon: "💓",  label: "Wearable" },
  { key: "blend",    icon: "🎨",  label: "Blend"    },
];

const EMOTION_EMOJI = {
  sadness:"😢", joy:"😊", anger:"😠",
  fear:"😨", love:"🥰", surprise:"😲",
};

export default function Home() {
  const navigate     = useNavigate();
  const [tab,        setTab]        = useState("text");
  const [mode,       setMode]       = useState("amplify");
  const [contextWho, setContextWho] = useState(null);

  const {
    fromText, fromEmoji, fromFace, fromVoice,
    loading, error, emotion,
  } = useMoodDetection();

  const handleResult = (detectedEmotion, logId) => {
    if (!detectedEmotion || !logId) return;
    navigate("/results", { state: { emotion: detectedEmotion, moodLogId: logId, mode } });
  };

  const onText     = async (text)          => { const d = await fromText(text, mode, contextWho); if (d) handleResult(d.emotion, d.mood_log_id); };
  const onEmoji    = async (emoji, slider) => { const d = await fromEmoji(emoji, slider, mode);   if (d) handleResult(d.emotion, d.mood_log_id); };
  const onFace     = async (b64)           => { const d = await fromFace(b64, mode);               if (d) handleResult(d.emotion, d.mood_log_id); };
  const onVoice    = async (b64)           => { const d = await fromVoice(b64, mode);              if (d) handleResult(d.emotion, d.mood_log_id); };
  const onBlend    = async (text)          => { const d = await fromText(text, mode, contextWho);  if (d) handleResult(d.emotion, d.mood_log_id); };
  const onWearable = async (bpm)           => { const d = await fromText(`heart rate ${bpm} bpm`, mode); if (d) handleResult(d.emotion, d.mood_log_id); };

  return (
    <div style={{ minHeight:"100vh", paddingTop:88, paddingBottom:64, paddingLeft:24, paddingRight:24 }}>
      <div style={{ maxWidth:900, margin:"0 auto" }}>

        {/* Hero */}
        <div className="text-center animate-fade-up" style={{ marginBottom:32 }}>
          <h1 className="font-display" style={{
            fontSize:"clamp(2.4rem,5vw,3.8rem)", fontWeight:700,
            color:"var(--blush)", lineHeight:1.15, marginBottom:12
          }}>
            How are you<br />
            <span style={{ color:"var(--amber)", fontStyle:"italic" }}>feeling today?</span>
          </h1>
          <p style={{ fontSize:16, opacity:0.5, color:"var(--blush)" }}>
            Tell me your mood — I'll curate the perfect experience for you
          </p>
        </div>

        {/* Mode toggle */}
        <div className="flex justify-center animate-fade-up delay-100" style={{ marginBottom:28 }}>
          <ContrastToggle mode={mode} onChange={setMode} />
        </div>

        {/* Main card — full width */}
        <div className="glass animate-fade-up delay-200" style={{ padding:32, marginBottom:16 }}>

          {/* Tabs */}
          <div style={{ display:"flex", gap:6, marginBottom:28, overflowX:"auto", paddingBottom:4 }}>
            {TABS.map(({ key, icon, label }) => (
              <button key={key} onClick={() => setTab(key)}
                className={tab === key ? "tab-active" : "btn-ghost"}
                style={{
                  flexShrink:0, padding:"8px 16px", fontSize:13, fontWeight:500,
                  borderRadius:12, display:"flex", alignItems:"center", gap:6, cursor:"pointer"
                }}>
                <span>{icon}</span>
                <span>{label}</span>
              </button>
            ))}
          </div>

          {/* Active input */}
          {tab === "text"     && <TextInput     onSubmit={onText}      loading={loading} />}
          {tab === "emoji"    && <EmojiPicker   onSubmit={onEmoji}     loading={loading} />}
          {tab === "slider"   && <SliderInput   onSubmit={onText}      loading={loading} />}
          {tab === "webcam"   && <WebcamCapture onCapture={onFace}     loading={loading} />}
          {tab === "voice"    && <VoiceCapture  onCapture={onVoice}    loading={loading} />}
          {tab === "wearable" && <WearableInput onCapture={onWearable} loading={loading} />}
          {tab === "blend"    && <MoodBlend     onSubmit={onBlend}     loading={loading} />}

          {error && (
            <p style={{ marginTop:12, fontSize:13, textAlign:"center", color:"var(--rose)" }}>
              {error}
            </p>
          )}
        </div>

        {/* Context panel — full width */}
        <div className="animate-fade-up delay-300">
          <ContextPanel contextWho={contextWho} setContextWho={setContextWho} />
        </div>

        {/* Loading overlay */}
        {loading && (
          <div style={{
            position:"fixed", inset:0, zIndex:50,
            display:"flex", alignItems:"center", justifyContent:"center",
            background:"rgba(27,25,49,0.88)", backdropFilter:"blur(8px)"
          }}>
            <div className="glass p-10 text-center">
              <div style={{ fontSize:64, marginBottom:16 }} className="animate-float">
                {emotion ? EMOTION_EMOJI[emotion] : "🎭"}
              </div>
              <p className="font-display" style={{ fontSize:22, fontWeight:600, color:"var(--blush)", marginBottom:8 }}>
                Reading your mood...
              </p>
              <p style={{ fontSize:13, opacity:0.45, color:"var(--blush)" }}>Analysing with AI</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}