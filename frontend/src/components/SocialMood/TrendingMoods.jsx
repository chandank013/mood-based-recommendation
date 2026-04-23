import { useEffect, useState } from "react";
import { getTrending } from "../../services/api";

const EMOJI  = { sadness:"😢", joy:"😊", anger:"😠", fear:"😨", love:"🥰", surprise:"😲" };
const COLORS = {
  sadness: "var(--velvet)", joy: "var(--amber)", anger: "var(--rose)",
  fear: "var(--wine)", love: "#c084fc", surprise: "var(--blush)",
};
const LABELS = {
  sadness: "People are feeling down",
  joy:     "Good vibes all around",
  anger:   "Tensions are high",
  fear:    "Anxiety in the air",
  love:    "Love is everywhere",
  surprise:"Full of surprises today",
};

export default function TrendingMoods() {
  const [data,    setData]    = useState([]);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(false);

  useEffect(() => {
    getTrending()
      .then(r => setData(r.data.trending || []))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  const total = data.reduce((s, d) => s + (d.total || d.count || 0), 0) || 1;
  const max   = Math.max(...data.map(d => d.total || d.count || 0), 1);
  const top   = data[0];

  return (
    <div className="glass p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <h3 className="font-display text-lg font-semibold" style={{ color: "var(--blush)" }}>
          ❋ Community Mood
        </h3>
        <span className="text-xs opacity-40" style={{ color: "var(--blush)" }}>Last hour</span>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-10 rounded-xl shimmer" style={{ animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>

      ) : error || data.length === 0 ? (
        <div className="text-center py-8">
          <span className="text-4xl block mb-2 opacity-20">❋</span>
          <p className="text-sm opacity-30" style={{ color: "var(--blush)" }}>
            No community data yet
          </p>
        </div>

      ) : (
        <>
          {/* Top mood banner */}
          {top && (
            <div className="p-3 rounded-2xl mb-5 flex items-center gap-3"
              style={{ background: `${COLORS[top.emotion]}18`, border: `1px solid ${COLORS[top.emotion]}33` }}>
              <span className="text-3xl">{EMOJI[top.emotion]}</span>
              <div>
                <p className="text-xs opacity-50 mb-0.5" style={{ color: "var(--blush)" }}>Dominant right now</p>
                <p className="font-semibold capitalize" style={{ color: COLORS[top.emotion] }}>{top.emotion}</p>
                <p className="text-xs opacity-40" style={{ color: "var(--blush)" }}>
                  {LABELS[top.emotion] || ""}
                </p>
              </div>
              <div className="ml-auto text-right">
                <p className="font-display text-2xl font-bold" style={{ color: COLORS[top.emotion] }}>
                  {Math.round(((top.total || top.count || 0) / total) * 100)}%
                </p>
              </div>
            </div>
          )}

          {/* Bar chart */}
          <div className="space-y-3">
            {data.map((d, i) => {
              const count = d.total || d.count || 0;
              const pct   = Math.round((count / max) * 100);
              const color = COLORS[d.emotion] || "var(--rose)";
              return (
                <div key={d.emotion}
                  className="animate-fade-up"
                  style={{ animationDelay: `${i * 0.07}s`, opacity: 0 }}>
                  <div className="flex items-center gap-3">
                    <span className="text-xl w-7 text-center flex-shrink-0">{EMOJI[d.emotion] || "✦"}</span>
                    <div className="flex-1">
                      <div className="flex justify-between items-center mb-1.5">
                        <span className="text-xs font-medium capitalize" style={{ color: "var(--blush)" }}>
                          {d.emotion}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold" style={{ color }}>
                            {Math.round((count / total) * 100)}%
                          </span>
                          <span className="text-xs opacity-35" style={{ color: "var(--blush)" }}>
                            ({count})
                          </span>
                        </div>
                      </div>
                      <div className="h-2 rounded-full overflow-hidden"
                        style={{ background: "rgba(233,188,185,0.07)" }}>
                        <div className="h-full rounded-full transition-all duration-700"
                          style={{ width: `${pct}%`, background: color }} />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <p className="text-xs text-center mt-4 opacity-25" style={{ color: "var(--blush)" }}>
            Based on {total} mood entries
          </p>
        </>
      )}
    </div>
  );
}