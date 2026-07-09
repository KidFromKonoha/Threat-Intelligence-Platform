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
    <div className="w-64 h-full border-r border-border bg-card flex flex-col">
      {/* Brand */}
      <div className="h-14 flex items-center px-2 border-b border-border gap-3">
        <img
          src="https://images.seeklogo.com/logo-png/28/2/maruti-suzuki-india-logo-png_seeklogo-289646.png"
          alt="Maruti Suzuki"
          className="h-30 w-auto object-contain"
        />
        <span className="font-semibold text-sm tracking-wide text-foreground"><b>THREATSTREAM</b></span>
      </div>

      {/* Main Nav */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {MAIN_NAVIGATION.map((item) => (
          <SidebarItem key={item.id} item={item} />
        ))}
      </div>

      {/* Bottom Nav */}
      <div className="px-3 py-2">
        {BOTTOM_NAVIGATION.map((item) => (
          <SidebarItem key={item.id} item={item} />
        ))}
      </div>

      {/* Footer */}
      <div className="border-t border-border p-4">
        <div className="flex items-center gap-3 text-sm text-muted-foreground mb-4">
          <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-foreground">
            <User className="w-4 h-4" />
          </div>
          <div className="flex flex-col overflow-hidden">
            <span className="font-medium text-foreground truncate">{user?.username || 'Current User'}</span>
            <span className="text-xs truncate">{user?.role === 'admin' ? 'Administrator' : 'SOC Analyst'}</span>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 w-full rounded-md text-sm font-medium text-muted-foreground hover:bg-secondary/50 hover:text-foreground transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};
