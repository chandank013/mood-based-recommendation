import { useState } from "react";

const EMOTION_MAP = [
  [1,1,"anger"],[1,5,"fear"],[1,9,"sadness"],
  [5,1,"surprise"],[5,5,"fear"],[5,9,"sadness"],
  [9,1,"joy"],[9,5,"love"],[9,9,"joy"],
];

function mapToEmotion(valence, arousal) {
  let closest = "joy", minDist = Infinity;
  EMOTION_MAP.forEach(([v, a, em]) => {
    const d = Math.hypot(valence - v, arousal - a);
    if (d < minDist) { minDist = d; closest = em; }
  });
  return closest;
}

const LABELS = {
  valence: ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"],
  arousal: ["Very Calm",     "Calm",     "Moderate","Energetic","Very Energetic"],
};

export default function SliderInput({ onSubmit, loading }) {
  const [valence, setValence] = useState(5);
  const [arousal, setArousal] = useState(5);

  const emotion = mapToEmotion(valence, arousal);

  const EMOTION_EMOJI = { joy:"😊", sadness:"😢", anger:"😠", fear:"😨", love:"🥰", surprise:"😲" };

  return (
    <div className="w-full">
      <p className="text-sm font-medium mb-5 opacity-60" style={{ color: "var(--blush)" }}>
        Set your emotional coordinates
      </p>

      {/* Valence */}
      <div className="mb-5">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-medium opacity-60" style={{ color: "var(--blush)" }}>Valence (Mood)</span>
          <span className="text-xs font-semibold" style={{ color: "var(--amber)" }}>
            {LABELS.valence[Math.round((valence - 1) / 2.25)]}
          </span>
        </div>
        <input type="range" min={1} max={10} value={valence}
          onChange={e => setValence(Number(e.target.value))}
          className="w-full h-2 rounded-full appearance-none cursor-pointer"
          style={{ background: `linear-gradient(to right, var(--rose) ${valence * 10}%, rgba(233,188,185,0.15) ${valence * 10}%)` }}
        />
        <div className="flex justify-between text-xs mt-1 opacity-30" style={{ color: "var(--blush)" }}>
          <span>😞 Negative</span><span>😊 Positive</span>
        </div>
      </div>

      {/* Arousal */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-medium opacity-60" style={{ color: "var(--blush)" }}>Arousal (Energy)</span>
          <span className="text-xs font-semibold" style={{ color: "var(--amber)" }}>
            {LABELS.arousal[Math.round((arousal - 1) / 2.25)]}
          </span>
        </div>
        <input type="range" min={1} max={10} value={arousal}
          onChange={e => setArousal(Number(e.target.value))}
          className="w-full h-2 rounded-full appearance-none cursor-pointer"
          style={{ background: `linear-gradient(to right, var(--amber) ${arousal * 10}%, rgba(233,188,185,0.15) ${arousal * 10}%)` }}
        />
        <div className="flex justify-between text-xs mt-1 opacity-30" style={{ color: "var(--blush)" }}>
          <span>😴 Calm</span><span>⚡ Energetic</span>
        </div>
      </div>

      {/* Predicted emotion */}
      <div className="glass p-3 flex items-center justify-center gap-3 mb-4 rounded-2xl">
        <span className="text-2xl">{EMOTION_EMOJI[emotion]}</span>
        <div>
          <p className="text-xs opacity-50" style={{ color: "var(--blush)" }}>Detected emotion</p>
          <p className="capitalize font-semibold" style={{ color: "var(--amber)" }}>{emotion}</p>
        </div>
      </div>

      <button className="btn-primary w-full py-3 text-sm" disabled={loading}
        onClick={() => onSubmit(`valence:${valence} arousal:${arousal}`)}>
        {loading ? "Analysing..." : "Find My Vibe ✦"}
      </button>
    </div>
  );
}