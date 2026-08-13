import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Village Overview", icon: "🏘️" },
  { to: "/civilization", label: "Civilization", icon: "🏛️" },
  { to: "/economy", label: "Economy", icon: "📈" },
  { to: "/assets", label: "Assets", icon: "🏠" },
  { to: "/businesses", label: "Businesses", icon: "🏪" },
  { to: "/organizations", label: "Organizations", icon: "🏢" },
  { to: "/families", label: "Families", icon: "👨‍👩‍👧‍👦" },
  { to: "/villagers", label: "Villagers", icon: "🧑" },
  { to: "/locations", label: "Locations", icon: "📍" },
  { to: "/feed", label: "Story Feed", icon: "📰" },
  { to: "/conversations", label: "Conversations", icon: "💬" },
  { to: "/search", label: "Search", icon: "🔍" },
];

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={onClose}
          aria-hidden
        />
      )}
      <aside
        className={`fixed left-0 top-0 z-50 flex h-full w-64 flex-col border-r border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] transition-transform lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="border-b border-[var(--color-vv-border)] px-5 py-6">
          <h1 className="font-[family-name:var(--font-display)] text-xl font-bold text-[var(--color-vv-accent)]">
            VillageVerse
          </h1>
          <p className="mt-1 text-sm text-[var(--color-vv-muted)]">Anandgaon</p>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === "/"}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-[var(--color-vv-accent)]/15 text-[var(--color-vv-accent)]"
                    : "text-[var(--color-vv-muted)] hover:bg-[var(--color-vv-surface-2)] hover:text-[var(--color-vv-text)]"
                }`
              }
            >
              <span>{l.icon}</span>
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
}
