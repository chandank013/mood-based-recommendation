import { useEffect, useState } from "react";
import { useSocket } from "../../hooks/useSocket";
import { getSocialPulse } from "../../services/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid
} from "recharts";

const EMOJI  = { sadness:"😢", joy:"😊", anger:"😠", fear:"😨", love:"🥰", surprise:"😲" };
const COLORS = {
  sadness:"var(--velvet)", joy:"var(--amber)", anger:"var(--rose)",
  fear:"var(--wine)", love:"#c084fc", surprise:"var(--blush)",
};

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="glass px-3 py-2 text-xs">
      <p className="font-semibold capitalize" style={{ color: "var(--amber)" }}>{d.emotion}</p>
      <p style={{ color: "var(--blush)", opacity: 0.7 }}>{d.hour} · {d.total} entries</p>
    </div>
  );
};

export default function MoodPulse() {
  const { connected, moodUpdates } = useSocket();
  const [pulseData, setPulseData]  = useState([]);
  const [loadingPulse, setLoading] = useState(true);

  useEffect(() => {
    getSocialPulse()
      .then(r => {
        // Group by hour for chart
        const raw = r.data.pulse || [];
        const grouped = {};
        raw.forEach(p => {
          const h = p.hour_slot?.slice(11, 16) || "00:00";
          if (!grouped[h]) grouped[h] = { hour: h };
          grouped[h][p.emotion] = (grouped[h][p.emotion] || 0) + (p.total || 0);
        });
        setPulseData(Object.values(grouped).slice(-12));
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="glass p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <h3 className="font-display text-lg font-semibold" style={{ color: "var(--blush)" }}>
          Live Mood Pulse
        </h3>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full transition-colors ${connected ? "animate-pulse" : ""}`}
            style={{ background: connected ? "#4ade80" : "rgba(233,188,185,0.3)" }} />
          <span className="text-xs opacity-40" style={{ color: "var(--blush)" }}>
            {connected ? "Live" : "Offline"}
          </span>
        </div>
      </div>

      {/* 24hr chart */}
      <div className="mb-6">
        <p className="text-xs opacity-40 mb-3" style={{ color: "var(--blush)" }}>
          Community mood — last 24 hours
        </p>
        {loadingPulse ? (
          <div className="h-36 shimmer rounded-xl" />
        ) : pulseData.length === 0 ? (
          <p className="text-xs opacity-25 text-center py-6" style={{ color: "var(--blush)" }}>
            No pulse data available yet
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={pulseData} barSize={8}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(233,188,185,0.05)" />
              <XAxis dataKey="hour"
                tick={{ fill: "var(--blush)", fontSize: 10, opacity: 0.4 }}
                axisLine={false} tickLine={false} />
              <YAxis hide />
              <Tooltip content={<CustomTooltip />} />
              {Object.keys(COLORS).map(em => (
                <Bar key={em} dataKey={em} stackId="a"
                  fill={COLORS[em]} radius={em === "joy" ? [4, 4, 0, 0] : [0, 0, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Live feed */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs opacity-40 uppercase tracking-widest" style={{ color: "var(--blush)" }}>
            Recent activity
          </p>
          {moodUpdates.length > 0 && (
            <span className="text-xs px-2 py-0.5 rounded-full"
              style={{ background: "rgba(74,222,128,0.12)", color: "#4ade80" }}>
              {moodUpdates.length} updates
            </span>
          )}
        </div>

        <div className="space-y-1.5 max-h-52 overflow-y-auto pr-1">
          {moodUpdates.length === 0 ? (
            <div className="text-center py-8">
              <span className="text-3xl block mb-2 opacity-20">📡</span>
              <p className="text-xs opacity-25" style={{ color: "var(--blush)" }}>
                {connected ? "Waiting for mood updates..." : "Connect to see live updates"}
              </p>
            </div>
          ) : (
            moodUpdates.map((u, i) => {
              const color = COLORS[u.emotion] || "var(--rose)";
              return (
                <div key={i}
                  className="flex items-center gap-3 py-2 px-3 rounded-xl animate-fade-in"
                  style={{ background: `${color}0e` }}>
                  <span className="text-base flex-shrink-0">{EMOJI[u.emotion] || "✦"}</span>
                  <div className="flex-1 min-w-0">
                    <span className="text-xs font-medium capitalize" style={{ color }}>
                      {u.emotion}
                    </span>
                    {u.context_who && (
                      <span className="text-xs opacity-40 ml-2" style={{ color: "var(--blush)" }}>
                        · {u.context_who}
                      </span>
                    )}
                  </div>
                  <span className="text-xs opacity-25 flex-shrink-0" style={{ color: "var(--blush)" }}>
                    just now
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}