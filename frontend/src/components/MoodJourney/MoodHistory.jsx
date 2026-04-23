import { useState } from "react";

const EMOJI  = { sadness:"😢", joy:"😊", anger:"😠", fear:"😨", love:"🥰", surprise:"😲" };
const COLORS = {
  sadness: "var(--velvet)", joy: "var(--amber)", anger: "var(--rose)",
  fear: "var(--wine)", love: "#c084fc", surprise: "var(--blush)",
};
const INPUT_ICONS = {
  text:"✍️", emoji:"😊", slider:"🎚️", face:"📷", voice:"🎙️", webcam:"📷",
};

export default function MoodHistory({ history }) {
  const [expanded, setExpanded] = useState(null);

  if (!history?.length) return (
    <div className="glass p-12 text-center">
      <span className="text-5xl block mb-3 opacity-20">◈</span>
      <p className="opacity-35 text-sm" style={{ color: "var(--blush)" }}>
        No mood entries yet. Start by sharing how you feel.
      </p>
    </div>
  );

  return (
    <div className="space-y-2">
      {history.map((h, i) => {
        const color   = COLORS[h.emotion] || "var(--rose)";
        const isOpen  = expanded === (h.id || i);
        const hasRecs = h.recommendations?.length > 0;

        return (
          <div key={h.id || i}
            className="glass animate-fade-up overflow-hidden transition-all duration-300"
            style={{ animationDelay: `${i * 0.04}s`, opacity: 0 }}>

            {/* Main row */}
            <div
              className="p-4 flex items-center gap-4 cursor-pointer"
              onClick={() => setExpanded(isOpen ? null : (h.id || i))}>

              {/* Emotion icon */}
              <div className="w-11 h-11 rounded-full flex items-center justify-center text-xl flex-shrink-0"
                style={{ background: `${color}22`, border: `1px solid ${color}44` }}>
                {EMOJI[h.emotion] || "✦"}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="capitalize font-semibold text-sm" style={{ color: "var(--blush)" }}>
                    {h.emotion}
                  </span>
                  {h.input_type && (
                    <span className="text-xs px-2 py-0.5 rounded-full"
                      style={{ background: "rgba(233,188,185,0.08)", color: "var(--blush)", opacity: 0.6 }}>
                      {INPUT_ICONS[h.input_type] || "✦"} {h.input_type}
                    </span>
                  )}
                  {h.mode === "contrast" && (
                    <span className="text-xs px-2 py-0.5 rounded-full"
                      style={{ background: "rgba(237,158,89,0.12)", color: "var(--amber)" }}>
                      ↭ shift
                    </span>
                  )}
                  {h.context_who && (
                    <span className="text-xs px-2 py-0.5 rounded-full opacity-50"
                      style={{ background: "rgba(233,188,185,0.08)", color: "var(--blush)" }}>
                      {h.context_who}
                    </span>
                  )}
                </div>
                {h.raw_input && h.input_type === "text" && (
                  <p className="text-xs mt-0.5 opacity-35 truncate" style={{ color: "var(--blush)" }}>
                    "{h.raw_input}"
                  </p>
                )}
              </div>

              {/* Right side */}
              <div className="text-right flex-shrink-0 flex flex-col items-end gap-1">
                {h.confidence != null && (
                  <span className="text-xs font-bold" style={{ color: color }}>
                    {Math.round(h.confidence * 100)}%
                  </span>
                )}
                <span className="text-xs opacity-30" style={{ color: "var(--blush)" }}>
                  {new Date(h.created_at).toLocaleTimeString("en-IN", {
                    hour: "2-digit", minute: "2-digit",
                  })}
                </span>
                {hasRecs && (
                  <span className="text-xs" style={{ color: "var(--amber)", opacity: 0.6 }}>
                    {isOpen ? "▲" : "▼"} {h.recommendations.length} recs
                  </span>
                )}
              </div>
            </div>

            {/* Expanded recommendations */}
            {isOpen && hasRecs && (
              <div className="px-4 pb-4 border-t" style={{ borderColor: "rgba(233,188,185,0.07)" }}>
                <p className="text-xs uppercase tracking-widest opacity-40 my-3" style={{ color: "var(--blush)" }}>
                  Recommendations
                </p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {h.recommendations.map((r, j) => (
                    <a key={j} href={r.url || "#"} target="_blank" rel="noopener noreferrer"
                      className="rec-card p-3 block">
                      <div className="flex items-center gap-2">
                        <span className="text-base">
                          {{ music:"🎵", movie:"🎬", food:"🍽️", book:"📖", activity:"⚡" }[r.category] || "✦"}
                        </span>
                        <div className="min-w-0">
                          <p className="text-xs font-medium truncate" style={{ color: "var(--blush)" }}>
                            {r.title}
                          </p>
                          <p className="text-xs opacity-40 capitalize" style={{ color: "var(--blush)" }}>
                            {r.category}
                          </p>
                        </div>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}