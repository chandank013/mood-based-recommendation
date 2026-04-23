import { useState } from "react";

export default function TextInput({ onSubmit, loading }) {
  const [text, setText] = useState("");

  return (
    <div className="w-full">
      <label className="block text-sm font-medium mb-2 opacity-60" style={{ color: "var(--blush)" }}>
        Express yourself freely...
      </label>
      <textarea
        className="mood-input w-full p-4 resize-none text-base leading-relaxed"
        rows={4}
        placeholder="e.g. I feel a little lost today, like nothing is going the way I planned..."
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={e => { if (e.key === "Enter" && e.ctrlKey && text.trim()) onSubmit(text); }}
      />
      <div className="flex justify-between items-center mt-3">
        <span className="text-xs opacity-30" style={{ color: "var(--blush)" }}>Ctrl + Enter to submit</span>
        <button className="btn-primary px-8 py-2.5 text-sm"
          onClick={() => text.trim() && onSubmit(text)}
          disabled={loading || !text.trim()}>
          {loading ? "Analysing..." : "Discover ✦"}
        </button>
      </div>
    </div>
  );
}