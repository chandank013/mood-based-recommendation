import { useState, useRef } from "react";

export default function VoiceCapture({ onCapture, loading }) {
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);

  const [recording, setRecording] = useState(false);
  const [done, setDone] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [err, setErr] = useState(null);

  // ─────────────────────────────
  // Start Recording
  // ─────────────────────────────
  const start = async () => {
    setErr(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const mediaRecorder = new MediaRecorder(stream);

      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        if (chunksRef.current.length === 0) {
          setErr("No audio recorded. Please try again.");
          return;
        }

        const blob = new Blob(chunksRef.current, {
          type: "audio/webm"
        });

        // 🔥 Convert to base64
        const reader = new FileReader();

        reader.onloadend = () => {
          const base64Audio = reader.result;

          if (!base64Audio) {
            setErr("Failed to process audio.");
            return;
          }

          // ✅ Send to backend
          onCapture(base64Audio);
          setDone(true);
        };

        reader.readAsDataURL(blob);

        // Stop mic
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorder.start();

      mediaRef.current = mediaRecorder;

      setRecording(true);
      setSeconds(0);

      timerRef.current = setInterval(() => {
        setSeconds((s) => s + 1);
      }, 1000);

    } catch (e) {
      console.error(e);
      setErr("Microphone access denied. Please allow permission.");
    }
  };

  // ─────────────────────────────
  // Stop Recording
  // ─────────────────────────────
  const stop = () => {
    if (!mediaRef.current) return;

    if (seconds < 2) {
      setErr("Recording too short. Please speak for a few seconds.");
      return;
    }

    mediaRef.current.stop();
    clearInterval(timerRef.current);
    setRecording(false);
  };

  // ─────────────────────────────
  // Reset
  // ─────────────────────────────
  const reset = () => {
    setDone(false);
    setSeconds(0);
    setErr(null);
  };

  // ─────────────────────────────
  // UI
  // ─────────────────────────────
  return (
    <div className="w-full text-center">
      <div
        className="mx-auto mb-5 flex flex-col items-center justify-center py-10 gap-3"
        style={{
          background: "rgba(27,25,49,0.6)",
          border: "1.5px solid rgba(233,188,185,0.12)",
          borderRadius: 16
        }}
      >
        {recording ? (
          <>
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center animate-pulse"
              style={{
                background: "linear-gradient(135deg,var(--rose),var(--wine))"
              }}
            >
              <span className="text-2xl">🎙️</span>
            </div>

            <p className="text-sm font-semibold" style={{ color: "var(--amber)" }}>
              Recording... {seconds}s
            </p>

            <p className="text-xs opacity-40" style={{ color: "var(--blush)" }}>
              Speak naturally about how you feel
            </p>
          </>
        ) : done ? (
          <>
            <span className="text-5xl">✅</span>
            <p className="text-sm" style={{ color: "var(--blush)" }}>
              Audio captured ({seconds}s)
            </p>
          </>
        ) : (
          <>
            <span className="text-5xl">🎙️</span>
            <p className="text-sm opacity-40" style={{ color: "var(--blush)" }}>
              Press record and speak for 5–15 seconds
            </p>
          </>
        )}
      </div>

      {/* Error */}
      {err && (
        <p className="text-xs mb-3" style={{ color: "var(--rose)" }}>
          {err}
        </p>
      )}

      {/* Buttons */}
      <div className="flex gap-3 justify-center">
        {!recording && !done && (
          <button
            className="btn-primary px-8 py-2.5 text-sm"
            onClick={start}
            disabled={loading}
          >
            🔴 Start Recording
          </button>
        )}

        {recording && (
          <button
            className="btn-ghost px-8 py-2.5 text-sm"
            onClick={stop}
          >
            ⏹ Stop
          </button>
        )}

        {done && (
          <button
            className="btn-ghost px-6 py-2 text-sm"
            onClick={reset}
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  );
}