import { Link, useLocation } from "react-router-dom";

const NAV = [
  { path: "/",        label: "Discover",  icon: "✦" },
  { path: "/journey", label: "Journey",   icon: "◈" },
];

export default function Navbar() {
  const { pathname } = useLocation();
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-4 py-3">
      <div className="max-w-5xl mx-auto glass flex items-center justify-between px-6 py-3">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-2xl animate-float inline-block">🎭</span>
          <span className="text-xl font-display font-semibold" style={{ color: "var(--blush)" }}>
            Moodly
          </span>
        </Link>
        <div className="flex items-center gap-1">
          {NAV.map(({ path, label, icon }) => (
            <Link key={path} to={path}
              className={`px-5 py-2 text-sm font-medium transition-all duration-300 ${
                pathname === path ? "tab-active" : "btn-ghost"
              }`}>
              <span className="mr-1">{icon}</span>{label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}