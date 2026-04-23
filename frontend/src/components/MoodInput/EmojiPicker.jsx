import { useState } from "react";

const EMOJIS = [
  { emoji: "😊", label: "Happy",     value: "😊" },
  { emoji: "😢", label: "Sad",       value: "😢" },
  { emoji: "😠", label: "Angry",     value: "😠" },
  { emoji: "😨", label: "Scared",    value: "😨" },
  { emoji: "🥰", label: "Loving",    value: "🥰" },
  { emoji: "😲", label: "Surprised", value: "😲" },
];

export default function EmojiPicker({ onSubmit, loading }) {
  const [selected, setSelected] = useState(null);
  const [slider,   setSlider]   = useState(5);

  return (
    <div className="w-full">
      <p className="text-sm font-medium mb-4 opacity-60" style={{ color: "var(--blush)" }}>Pick your vibe</p>
      <div className="grid grid-cols-3 gap-3 mb-5">
        {EMOJIS.map(({ emoji, label, value }) => (
          <button key={value} onClick={() => setSelected(value)}
            className={`p-4 rounded-2xl flex flex-col items-center gap-1 transition-all duration-300 ${
              selected === value ? "scale-105 animate-pulse-glow" : "rec-card"
            }`}
            style={selected === value ? { border: "2px solid var(--amber)" } : {}}>
            <span className="text-3xl">{emoji}</span>
            <span className="text-xs font-medium" style={{ color: "var(--blush)" }}>{label}</span>
          </button>
        ))}
      </div>
      <div className="mb-5">
        <div className="flex justify-between text-xs mb-2 opacity-50" style={{ color: "var(--blush)" }}>
          <span>Low</span><span>Intensity</span><span>High</span>
        </div>
        <input type="range" min={1} max={10} value={slider}
          onChange={e => setSlider(Number(e.target.value))}
          className="w-full h-2 rounded-full appearance-none cursor-pointer"
          style={{ background: `linear-gradient(to right, var(--amber) ${slider * 10}%, rgba(233,188,185,0.15) ${slider * 10}%)` }}
        />
        <p className="text-center text-sm font-semibold mt-2" style={{ color: "var(--amber)" }}>{slider} / 10</p>
      </div>
      <button className="btn-primary w-full py-3 text-sm"
        disabled={!selected || loading}
        onClick={() => selected && onSubmit(selected, slider)}>
        {loading ? "Analysing..." : "Find My Vibe ✦"}
      </button>
    </div>
  );
}