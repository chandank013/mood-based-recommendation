const WHO = [
  { value: "alone",   icon: "🧘" },
  { value: "family",  icon: "👨‍👩‍👧" },
  { value: "friends", icon: "👥" },
  { value: "partner", icon: "💑" },
];

export default function ContextPanel({ contextWho, setContextWho }) {
  return (
    <div className="glass p-4 rounded-2xl">
      <p className="text-xs font-medium mb-3 opacity-50 uppercase tracking-widest" style={{ color: "var(--blush)" }}>
        Who are you with?
      </p>
      <div className="flex gap-2 flex-wrap">
        {WHO.map(({ value, icon }) => (
          <button key={value}
            onClick={() => setContextWho(contextWho === value ? null : value)}
            className={`px-4 py-2 text-sm rounded-full capitalize transition-all duration-300 flex items-center gap-1.5 ${
              contextWho === value ? "tab-active" : "btn-ghost"
            }`}>
            <span>{icon}</span>{value}
          </button>
        ))}
      </div>
    </div>
  );
}