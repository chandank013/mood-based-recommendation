import { useState, useRef, useCallback } from "react";

export default function WebcamCapture({ onCapture, loading }) {
  const videoRef   = useRef(null);
  const [active,   setActive]   = useState(false);
  const [captured, setCaptured] = useState(false);
  const [err,      setErr]      = useState(null);

  const start = async () => {
    setErr(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
      setActive(true);
    } catch {
      setErr("Camera access denied. Please allow camera permission.");
    }
  };

  const capture = useCallback(() => {
    const canvas = document.createElement("canvas");
    canvas.width  = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext("2d").drawImage(videoRef.current, 0, 0);
    const b64 = canvas.toDataURL("image/jpeg", 0.85);
    videoRef.current.srcObject?.getTracks().forEach(t => t.stop());
    setActive(false);
    setCaptured(true);
    onCapture(b64);
  }, [onCapture]);

  const reset = () => { setCaptured(false); setActive(false); };

  return (
    <div className="w-full text-center">
      <div className="relative mx-auto mb-4 rounded-2xl overflow-hidden"
        style={{ width: 280, height: 200, background: "rgba(27,25,49,0.6)", border: "1.5px solid rgba(233,188,185,0.12)" }}>
        <video ref={videoRef} className={`w-full h-full object-cover ${active ? "block" : "hidden"}`} />
        {!active && (
          <div className="flex flex-col items-center justify-center h-full gap-2">
            <span className="text-5xl">{captured ? "✅" : "📷"}</span>
            <span className="text-sm opacity-40" style={{ color: "var(--blush)" }}>
              {captured ? "Photo captured!" : "Camera preview"}
            </span>
          </div>
        )}
      </div>

      {err && <p className="text-xs mb-3" style={{ color: "var(--rose)" }}>{err}</p>}

      <div className="flex gap-3 justify-center">
        {!active && !captured && <button className="btn-ghost px-6 py-2 text-sm" onClick={start}>Start Camera</button>}
        {active  && <button className="btn-primary px-6 py-2 text-sm" onClick={capture} disabled={loading}>
          {loading ? "Analysing..." : "📸 Capture & Analyse"}
        </button>}
        {captured && <button className="btn-ghost px-6 py-2 text-sm" onClick={reset}>Try Again</button>}
      </div>
    </div>
  );
}