import RecommendationCard from "./RecommendationCard.jsx";

export default function MovieSection({ movies = [], tvShows = [], loading }) {
  const all = [...(movies || []), ...(tvShows || [])];
  if (!loading && all.length === 0) return null;
  return (
    <section className="mb-10 animate-fade-up delay-100">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-2xl">🎬</span>
        <h3 className="font-display text-xl font-semibold" style={{ color: "var(--blush)" }}>
          Movies &amp; TV Shows
        </h3>
        {!loading && (
          <span className="text-xs px-2 py-0.5 rounded-full ml-auto"
            style={{ background: "rgba(237,158,89,0.12)", color: "var(--amber)" }}>
            {all.length} picks
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {loading
          ? [...Array(4)].map((_, i) => (
              <div key={i} className="rec-card h-52 shimmer" style={{ animationDelay: `${i * 0.1}s` }} />
            ))
          : all.map((item, i) => (
              <RecommendationCard key={i} item={item} category="movie" />
            ))
        }
      </div>
    </section>
  );
}