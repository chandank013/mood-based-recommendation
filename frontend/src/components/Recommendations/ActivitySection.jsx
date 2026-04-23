const ACTIVITY_ICONS = [
  "🧘", "🏃", "🥊", "💃", "🚴", "🏋️", "🎨", "📝", "🧗", "🏊",
];

export default function ActivitySection({ activities = [], loading }) {
  if (!loading && activities.length === 0) return null;
  return (
    <section className="mb-10 animate-fade-up delay-400">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-2xl">⚡</span>
        <h3 className="font-display text-xl font-semibold" style={{ color: "var(--blush)" }}>
          Activities
        </h3>
        {!loading && (
          <span className="text-xs px-2 py-0.5 rounded-full ml-auto"
            style={{ background: "rgba(237,158,89,0.12)", color: "var(--amber)" }}>
            {activities.length} ideas
          </span>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {loading
          ? [...Array(4)].map((_, i) => (
              <div key={i} className="rec-card h-16 shimmer" style={{ animationDelay: `${i * 0.08}s` }} />
            ))
          : activities.map((act, i) => (
              <div key={i}
                className="rec-card p-4 flex items-center gap-4 group cursor-default"
                style={{ animationDelay: `${i * 0.06}s` }}>
                {/* Number badge */}
                <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 font-bold text-sm"
                  style={{ background: "linear-gradient(135deg,var(--amber),var(--rose))", color: "var(--night)" }}>
                  {i + 1}
                </div>
                {/* Icon */}
                <span className="text-xl flex-shrink-0">{ACTIVITY_ICONS[i % ACTIVITY_ICONS.length]}</span>
                {/* Text */}
                <p className="text-sm leading-snug" style={{ color: "var(--blush)" }}>{act}</p>
              </div>
            ))
        }
      </div>
    </section>
  );
}