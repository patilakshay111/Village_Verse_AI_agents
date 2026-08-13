import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { useTheme } from "../hooks/useTheme";

export function Layout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { dark, toggle } = useTheme();

  return (
    <div className="flex min-h-screen">
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />
      <div className="flex min-h-screen flex-1 flex-col lg:pl-0">
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-[var(--color-vv-border)] bg-[var(--color-vv-surface)]/95 px-4 py-3 backdrop-blur">
          <button
            type="button"
            className="rounded-lg p-2 lg:hidden"
            onClick={() => setMenuOpen(true)}
            aria-label="Open menu"
          >
            ☰
          </button>
          <span className="hidden text-sm text-[var(--color-vv-muted)] lg:block">
            Living simulation of an Indian village
          </span>
          <button
            type="button"
            onClick={toggle}
            className="rounded-lg border border-[var(--color-vv-border)] px-3 py-1.5 text-sm"
          >
            {dark ? "☀️ Light" : "🌙 Dark"}
          </button>
        </header>
        <main className="flex-1 p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
