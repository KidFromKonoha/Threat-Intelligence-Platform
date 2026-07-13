import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MAIN_NAVIGATION, BOTTOM_NAVIGATION } from '../../config/navigation';
import { SidebarItem } from './sidebar-item';
import { LogOut, User } from 'lucide-react';
import { useAuth } from '../../hooks/use-auth';

export const Sidebar: React.FC = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="w-64 h-full border-r border-border/40 bg-background/95 flex flex-col">
      {/* Brand */}
      <div className="h-14 flex items-center px-5 border-b border-border/40">
        <div className="flex items-center gap-2.5">
          <svg role="img" viewBox="0 0 24 24" className="w-6 h-6 text-slate-400 flex-shrink-0" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.369 19.995C13.51 22.39 12 24 12 24L.105 15.705s5.003-3.715 9.186-.87l5.61 3.882.683-.453L.106 7.321s2.226-.65 6.524-3.315C10.49 1.609 12 0 12 0l11.895 8.296s-5.003 3.715-9.187.87L9.1 5.281l-.683.454L23.893 16.68s-2.224.649-6.524 3.315Z"/>
          </svg>
          <span className="font-bold text-[13px] tracking-[0.1em] text-foreground uppercase opacity-90">
            Maruti Suzuki
          </span>
        </div>
      </div>

      {/* Main Nav */}
      <div className="flex-1 overflow-y-auto py-6 px-3 space-y-1">
        {MAIN_NAVIGATION.map((item) => (
          <SidebarItem key={item.id} item={item} />
        ))}
      </div>

      {/* Bottom Nav */}
      <div className="px-3 py-2 space-y-1">
        {BOTTOM_NAVIGATION.map((item) => (
          <SidebarItem key={item.id} item={item} />
        ))}
      </div>

      {/* Footer */}
      <div className="border-t border-border/40 p-4">
        <div className="flex items-center gap-3 text-sm text-muted-foreground mb-4 px-2">
          <div className="w-8 h-8 rounded-full bg-secondary border border-border/50 flex items-center justify-center text-foreground shadow-sm">
            <User className="w-4 h-4 opacity-70" />
          </div>
          <div className="flex flex-col overflow-hidden">
            <span className="font-medium text-foreground truncate">{user?.username || 'Current User'}</span>
            <span className="text-[11px] uppercase tracking-wider text-muted-foreground truncate">{user?.role === 'admin' ? 'Administrator' : 'SOC Analyst'}</span>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-md text-sm font-medium text-muted-foreground hover:bg-secondary/40 hover:text-foreground transition-all active:scale-[0.98]"
        >
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};
