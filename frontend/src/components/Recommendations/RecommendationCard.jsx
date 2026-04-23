const ICONS  = { music:"🎵", movie:"🎬", food:"🍽️", activity:"⚡", book:"📖", podcast:"🎙️" };
const COLORS = {
  music:    "linear-gradient(135deg, #44174E, #662249)",
  movie:    "linear-gradient(135deg, #662249, #A34054)",
  book:     "linear-gradient(135deg, #1B1931, #44174E)",
  food:     "linear-gradient(135deg, #A34054, #ED9E59)",
  podcast:  "linear-gradient(135deg, #44174E, #A34054)",
  activity: "linear-gradient(135deg, #ED9E59, #A34054)",
};

export default function RecommendationCard({ item, category }) {
  const hasImage = item.thumbnail && item.thumbnail !== "None" && item.thumbnail !== null;

  return (
    <a
      href={item.url || "#"}
      target="_blank"
      rel="noopener noreferrer"
      className="rec-card flex flex-col group cursor-pointer"
      style={{ textDecoration: "none" }}
    >
      {/* Thumbnail or placeholder */}
      <div
        className="w-full flex items-center justify-center flex-shrink-0"
        style={{
          height: 130,
          borderRadius: "12px 12px 0 0",
          background: hasImage ? "transparent" : COLORS[category] || COLORS.music,
          overflow: "hidden",
        }}
      >
        {hasImage ? (
          <img
            src={item.thumbnail}
            alt={item.title || ""}
            onError={e => {
              e.target.style.display = "none";
              e.target.parentNode.style.background = COLORS[category] || COLORS.music;
              e.target.parentNode.innerHTML = `<span style="font-size:44px">${ICONS[category] || "✦"}</span>`;
            }}
            className="w-full h-full group-hover:scale-105 transition-transform duration-500"
            style={{ objectFit: "cover" }}
          />
        ) : (
          <span style={{ fontSize: 44 }}>{ICONS[category] || "✦"}</span>
        )}
      </div>

      {/* Content */}
      <div style={{ padding: "12px 14px", flex: 1, display: "flex", flexDirection: "column" }}>
        {/* Category badge */}
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
          <span style={{ fontSize: 13 }}>{ICONS[category] || "✦"}</span>
          <span style={{ fontSize: 11, opacity: 0.4, textTransform: "capitalize", color: "var(--blush)" }}>
            {category}
          </span>
        </div>

        {/* Title */}
        <h4 style={{
          fontWeight: 600, fontSize: 13, lineHeight: 1.4,
          color: "var(--blush)", flex: 1,
          display: "-webkit-box", WebkitLineClamp: 2,
          WebkitBoxOrient: "vertical", overflow: "hidden",
        }}>
          {item.title || "Untitled"}
        </h4>

        {/* Meta */}
        <div style={{ marginTop: 6 }}>
          {item.authors   && <p style={{ fontSize: 11, opacity: 0.5, color: "var(--blush)", marginBottom: 2 }}>by {item.authors}</p>}
          {item.podcast   && <p style={{ fontSize: 11, opacity: 0.5, color: "var(--blush)", marginBottom: 2 }}>{item.podcast}</p>}
          {item.year      && <p style={{ fontSize: 11, opacity: 0.35, color: "var(--blush)" }}>{item.year}</p>}
          {item.ready_in  && <p style={{ fontSize: 11, opacity: 0.35, color: "var(--blush)" }}>⏱ {item.ready_in} min</p>}
          {item.tracks    && <p style={{ fontSize: 11, opacity: 0.35, color: "var(--blush)" }}>🎵 {item.tracks} tracks</p>}
          {item.duration  && <p style={{ fontSize: 11, opacity: 0.35, color: "var(--blush)" }}>⏱ {Math.round(item.duration / 60)} min</p>}
          {item.pages     && <p style={{ fontSize: 11, opacity: 0.35, color: "var(--blush)" }}>📄 {item.pages} pages</p>}
          {item.rating    && (
            <p style={{ fontSize: 12, fontWeight: 700, color: "var(--amber)", marginTop: 4 }}>
              ★ {item.rating}
            </p>
          )}
        </div>

        {/* Source badge */}
        {item.source && item.source !== "fallback" && (
          <div style={{ marginTop: 8 }}>
            <span style={{
              fontSize: 10, padding: "2px 8px", borderRadius: 50,
              background: "rgba(233,188,185,0.07)", color: "var(--blush)", opacity: 0.5,
            }}>
              {item.source}
            </span>
          </div>
        )}
      </div>
    </a>
  );
}