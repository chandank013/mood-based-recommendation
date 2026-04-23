export default function ContrastToggle({ mode, onChange }) {
  return (
    <div className="glass p-1 inline-flex rounded-full gap-1">
      {[
        { value: "amplify",  label: "✦ Match Mood"  },
        { value: "contrast", label: "↭ Shift Mood"  },
      ].map(({ value, label }) => (
        <button key={value} onClick={() => onChange(value)}
          className={`px-5 py-2 text-sm font-medium rounded-full transition-all duration-300 ${
            mode === value ? "tab-active" : ""
          }`}
          style={mode !== value ? { color: "var(--blush)", opacity: 0.55 } : {}}>
          {label}
        </button>
      ))}
    </div>
  );
}