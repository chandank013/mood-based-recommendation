import { useState } from "react";

const EMOTIONS = [
  { label: "Joy",      emoji: "😊", value: "joy",      color: "var(--amber)"  },
  { label: "Sadness",  emoji: "😢", value: "sadness",  color: "var(--velvet)" },
  { label: "Anger",    emoji: "😠", value: "anger",    color: "var(--rose)"   },
  { label: "Fear",     emoji: "😨", value: "fear",     color: "var(--wine)"   },
  { label: "Love",     emoji: "🥰", value: "love",     color: "#c084fc"       },
  { label: "Surprise", emoji: "😲", value: "surprise", color: "var(--blush)"  },
];

// Maps a blend of emotions into a descriptive label
const BLEND_LABELS = {
  "joy+sadness":   "Bittersweet",
  "joy+love":      "Blissful",
  "joy+surprise":  "Elated",
  "sadness+love":  "Nostalgic",
  "sadness+fear":  "Melancholy",
  "anger+fear":    "Anxious",
  "anger+surprise":"Shocked",
  "love+surprise": "Overwhelmed",
  "fear+surprise": "Startled",
};

function getBlendLabel(selected) {
  if (selected.length === 1) return selected[0];
  const key = [...selected].sort().join("+");
  return BLEND_LABELS[key] || selected.join(" & ");
}

export default function MoodBlend({ onSubmit, loading }) {
  const [selected,    setSelected]    = useState([]);
  const [intensities, setIntensities] = useState({});

  const toggle = (val) => {
    setSelected(prev => {
      if (prev.includes(val)) {
        const next = prev.filter(v => v !== val);
        setIntensities(i => { const c = {...i}; delete c[val]; return c; });
        return next;
      }
      if (prev.length >= 3) return prev;
      setIntensities(i => ({ ...i, [val]: 5 }));
      return [...prev, val];
    });
  };

  const setIntensity = (val, int) =>
    setIntensities(prev => ({ ...prev, [val]: int }));

  // Build blend text with intensities for the backend
  const blendText = selected
    .map(v => `${v}(${intensities[v] || 5})`)
    .join(" and ");

  const blendLabel = getBlendLabel(selected);

  // Dominant emotion = highest intensity
  const dominant = selected.reduce((best, v) =>
    (intensities[v] || 5) > (intensities[best] || 5) ? v : best,
    selected[0]
  );

  return (
    <div className="w-full">
      <p className="text-sm font-medium mb-1 opacity-60" style={{ color: "var(--blush)" }}>
        Mix up to 3 emotions you're feeling right now
      </p>
      <p className="text-xs mb-5 opacity-35" style={{ color: "var(--blush)" }}>
        e.g. Joy + Sadness = Bittersweet · Love + Surprise = Overwhelmed
      </p>

      {/* Emotion grid */}
      <div className="grid grid-cols-3 gap-3 mb-5">
        {EMOTIONS.map(({ label, emoji, value, color }) => {
          const idx    = selected.indexOf(value);
          const active = idx !== -1;
          return (
            <button key={value} onClick={() => toggle(value)}
              className={`p-3 rounded-2xl flex flex-col items-center gap-1.5 transition-all duration-300 relative select-none ${
                active ? "scale-105" : "rec-card hover:scale-102"
              }`}
              style={active
                ? { border: `2px solid ${color}`, background: `${color}18` }
                : {}
              }>
              {/* Order badge */}
              {active && (
                <span className="absolute top-2 right-2 w-5 h-5 rounded-full text-xs flex items-center justify-center font-bold"
                  style={{ background: color, color: "var(--night)" }}>
                  {idx + 1}
                </span>
              )}
              <span className="text-2xl">{emoji}</span>
              <span className="text-xs font-medium" style={{ color: active ? color : "var(--blush)" }}>
                {label}
              </span>
            </button>
          );
        })}
      </div>

      {/* Intensity sliders for each selected emotion */}
      {selected.length > 0 && (
        <div className="space-y-3 mb-5">
          {selected.map(val => {
            const em    = EMOTIONS.find(e => e.value === val);
            const intv  = intensities[val] || 5;
            return (
              <div key={val} className="glass p-3 rounded-2xl">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{em.emoji}</span>
                    <span className="text-sm font-medium capitalize" style={{ color: em.color }}>
                      {em.label}
                    </span>
                  </div>
                  <span className="text-xs font-bold" style={{ color: em.color }}>{intv}/10</span>
                </div>
                <input type="range" min={1} max={10} value={intv}
                  onChange={e => setIntensity(val, Number(e.target.value))}
                  className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
                  style={{
                    background: `linear-gradient(to right, ${em.color} ${intv * 10}%, rgba(233,188,185,0.12) ${intv * 10}%)`
                  }}
                />
              </div>
            );
          })}
        </div>
      )}

      {/* Blend preview */}
      {selected.length > 1 && (
        <div className="glass p-4 rounded-2xl mb-5 text-center">
          <p className="text-xs opacity-45 mb-1 uppercase tracking-widest" style={{ color: "var(--blush)" }}>
            Your blend
          </p>
          <p className="font-display text-xl font-semibold" style={{ color: "var(--amber)" }}>
            {blendLabel}
          </p>
          <div className="flex items-center justify-center gap-2 mt-2 flex-wrap">
            {selected.map(v => {
              const em = EMOTIONS.find(e => e.value === v);
              return (
                <span key={v} className="text-xs px-2.5 py-1 rounded-full font-medium"
                  style={{ background: `${em.color}22`, color: em.color, border: `1px solid ${em.color}44` }}>
                  {em.emoji} {em.label}
                </span>
              );
            })}
          </div>
          {dominant && (
            <p className="text-xs mt-2 opacity-40" style={{ color: "var(--blush)" }}>
              Dominant: {EMOTIONS.find(e => e.value === dominant)?.label}
            </p>
          )}
        </div>
      )}

      {selected.length === 1 && (
        <div className="glass p-3 rounded-2xl mb-5 text-center">
          <p className="text-xs opacity-40" style={{ color: "var(--blush)" }}>
            Add more emotions to create a blend, or submit as is
          </p>
        </div>
      )}

      <button className="btn-primary w-full py-3 text-sm"
        disabled={selected.length === 0 || loading}
        onClick={() => onSubmit(blendText)}>
        {loading ? "Analysing blend..." : `Blend & Discover ✦`}
      </button>
    </div>
  );
}