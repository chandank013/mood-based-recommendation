import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, ReferenceLine, Area, AreaChart
} from "recharts";

const EMOTION_SCORE = {
  sadness: 1, fear: 2, anger: 3, surprise: 4, love: 5, joy: 6,
};
const EMOTION_EMOJI = {
  sadness:"😢", fear:"😨", anger:"😠", surprise:"😲", love:"🥰", joy:"😊",
};

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="glass px-4 py-3 text-sm shadow-lg">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xl">{EMOTION_EMOJI[d.emotion] || "✦"}</span>
        <p className="font-semibold capitalize" style={{ color: "var(--amber)" }}>{d.emotion}</p>
      </div>
      <p className="text-xs opacity-50" style={{ color: "var(--blush)" }}>{d.date}</p>
      {d.confidence && (
        <p className="text-xs mt-1" style={{ color: "var(--blush)" }}>
          Confidence: <span style={{ color: "var(--amber)" }}>{Math.round(d.confidence * 100)}%</span>
        </p>
      )}
    </div>
  );
};

const CustomDot = ({ cx, cy, payload }) => {
  const em = EMOTION_EMOJI[payload.emotion] || "✦";
  return (
    <text x={cx} y={cy - 10} textAnchor="middle" fontSize={14}>{em}</text>
  );
};

export default function JourneyChart({ history }) {
  if (!history?.length) return null;

  const data = [...history].reverse().map(h => ({
    emotion:    h.emotion,
    score:      EMOTION_SCORE[h.emotion] || 3,
    confidence: h.confidence,
    date:       new Date(h.created_at).toLocaleDateString("en-IN", {
      month: "short", day: "numeric",
    }),
  }));

  const avg = data.reduce((s, d) => s + d.score, 0) / data.length;

  return (
    <div className="glass p-6 mb-6">
      <div className="flex items-center justify-between mb-5">
        <h3 className="font-display text-lg font-semibold" style={{ color: "var(--blush)" }}>
          Mood Timeline
        </h3>
        <div className="text-xs px-3 py-1 rounded-full" style={{ background: "rgba(237,158,89,0.15)", color: "var(--amber)" }}>
          avg: {Object.keys(EMOTION_SCORE).find(k => Math.abs(EMOTION_SCORE[k] - avg) < 0.8) || "mixed"}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 24, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="moodGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="var(--amber)" stopOpacity={0.25} />
              <stop offset="95%" stopColor="var(--amber)" stopOpacity={0}    />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(233,188,185,0.06)" />
          <XAxis dataKey="date"
            tick={{ fill: "var(--blush)", fontSize: 11, opacity: 0.45 }}
            axisLine={false} tickLine={false} />
          <YAxis hide domain={[0, 7]} />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={avg} stroke="rgba(233,188,185,0.15)" strokeDasharray="4 4" />
          <Area
            type="monotone" dataKey="score"
            stroke="var(--amber)" strokeWidth={2.5}
            fill="url(#moodGrad)"
            dot={<CustomDot />}
            activeDot={{ fill: "var(--blush)", r: 6, strokeWidth: 0 }}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-3 flex-wrap">
        {Object.entries(EMOTION_EMOJI).map(([em, emoji]) => (
          <span key={em} className="flex items-center gap-1 text-xs opacity-45" style={{ color: "var(--blush)" }}>
            {emoji} <span className="capitalize">{em}</span>
          </span>
        ))}
      </div>
    </div>
  );
}