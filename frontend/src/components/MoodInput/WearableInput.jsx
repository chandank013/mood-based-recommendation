import { useState } from "react";

export default function WearableInput({ onReading, loading }) {
  const [bpm,       setBpm]       = useState(null);
  const [connected, setConnected] = useState(false);
  const [scanning,  setScanning]  = useState(false);
  const [err,       setErr]       = useState(null);

  const connect = async () => {
    setErr(null);
    setScanning(true);
    try {
      const device = await navigator.bluetooth.requestDevice({
        filters:          [{ services: ["heart_rate"] }],
        optionalServices: ["heart_rate"],
      });
      const server      = await device.gatt.connect();
      const service     = await server.getPrimaryService("heart_rate");
      const char        = await service.getCharacteristic("heart_rate_measurement");
      await char.startNotifications();
      char.addEventListener("characteristicvaluechanged", (e) => {
        const val = e.target.value;
        const bpmVal = val.getUint8(1);
        setBpm(bpmVal);
        setConnected(true);
        onReading(bpmVal);
      });
    } catch (e) {
      if (e.name !== "NotFoundError")
        setErr("Bluetooth connection failed. Make sure your device is nearby.");
    } finally {
      setScanning(false);
    }
  };

  const BPM_LABEL =
    !bpm         ? null
    : bpm < 60   ? { label: "Resting",  color: "var(--velvet)", emoji: "🧘" }
    : bpm < 80   ? { label: "Calm",     color: "var(--wine)",   emoji: "😌" }
    : bpm < 100  ? { label: "Normal",   color: "var(--amber)",  emoji: "😊" }
    : bpm < 130  ? { label: "Elevated", color: "var(--rose)",   emoji: "😤" }
    :              { label: "High",     color: "var(--rose)",   emoji: "😠" };

  return (
    <div className="w-full text-center">
      {/* BPM ring */}
      <div className="relative mx-auto mb-6 flex items-center justify-center"
        style={{ width: 140, height: 140 }}>
        <div className={`absolute inset-0 rounded-full ${connected ? "animate-pulse-glow" : ""}`}
          style={{ background: "rgba(68,23,78,0.3)", border: `2px solid ${connected ? "var(--amber)" : "rgba(233,188,185,0.2)"}` }} />
        <div className="relative z-10 flex flex-col items-center">
          {bpm ? (
            <>
              <span className="text-3xl font-display font-bold" style={{ color: "var(--amber)" }}>{bpm}</span>
              <span className="text-xs opacity-60" style={{ color: "var(--blush)" }}>BPM</span>
              <span className="text-lg mt-1">{BPM_LABEL?.emoji}</span>
            </>
          ) : (
            <span className="text-4xl">❤️</span>
          )}
        </div>
      </div>

      {BPM_LABEL && (
        <div className="glass p-3 mb-4 rounded-2xl inline-block">
          <span className="text-sm font-semibold" style={{ color: BPM_LABEL.color }}>{BPM_LABEL.label} heart rate</span>
        </div>
      )}

      {err && <p className="text-xs mb-3" style={{ color: "var(--rose)" }}>{err}</p>}

      {!connected ? (
        <button className="btn-ghost px-6 py-2 text-sm" onClick={connect} disabled={scanning}>
          {scanning ? "Scanning..." : "🔵 Connect Wearable"}
        </button>
      ) : (
        <p className="text-xs opacity-50" style={{ color: "var(--blush)" }}>
          ● Live — mood updating automatically
        </p>
      )}

      {/* Manual fallback */}
      <div className="mt-5">
        <p className="text-xs opacity-40 mb-2" style={{ color: "var(--blush)" }}>Or enter manually:</p>
        <div className="flex gap-2 justify-center">
          <input type="number" min={40} max={200} placeholder="BPM"
            className="mood-input w-24 px-3 py-2 text-sm text-center"
            onChange={e => { const v = Number(e.target.value); if (v > 30 && v < 220) { setBpm(v); onReading(v); }}}
          />
        </div>
      </div>
    </div>
  );
}