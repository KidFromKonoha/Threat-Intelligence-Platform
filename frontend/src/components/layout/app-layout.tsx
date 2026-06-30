import { Outlet, Link } from "react-router-dom";
import { Moon, Sun, ShieldAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/use-theme";

export function AppLayout() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="flex items-center justify-between border-b border-border px-6 py-3">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <ShieldAlert className="h-5 w-5" />
          Threat Intelligence Platform
        </Link>
        <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle dark mode">
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
