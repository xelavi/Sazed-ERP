import { Menu, Search, Globe, Bell, HelpCircle, User } from 'lucide-react';
import { useState } from 'react';

interface TopBarProps {
  onToggleSidebar: () => void;
}

export function TopBar({ onToggleSidebar }: TopBarProps) {
  const [language, setLanguage] = useState('EN');

  const toggleLanguage = () => {
    setLanguage(language === 'EN' ? 'ES' : 'EN');
  };

  return (
    <header className="h-14 bg-[#1F1F1F] text-white flex items-center justify-between px-4 flex-shrink-0">
      {/* Left Section */}
      <div className="flex items-center gap-4 flex-1">
        <button
          onClick={onToggleSidebar}
          className="p-1.5 hover:bg-white/10 rounded transition-colors"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Search */}
        <div className="relative max-w-md w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search"
            className="w-full pl-10 pr-4 py-1.5 bg-[#2D2D2D] border border-transparent rounded text-sm text-white placeholder:text-gray-400 focus:outline-none focus:border-gray-600 focus:bg-[#3D3D3D]"
          />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        <button className="p-1.5 hover:bg-white/10 rounded transition-colors">
          <HelpCircle className="w-5 h-5" />
        </button>
        <button className="p-1.5 hover:bg-white/10 rounded transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-[#FF6B35] rounded-full"></span>
        </button>
        <button
          onClick={toggleLanguage}
          className="p-1.5 hover:bg-white/10 rounded transition-colors flex items-center gap-1.5"
        >
          <Globe className="w-4 h-4" />
          <span className="text-xs font-medium">{language}</span>
        </button>
        <div className="w-px h-6 bg-white/20 mx-1"></div>
        <button className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <div className="w-7 h-7 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
            <User className="w-4 h-4" />
          </div>
        </button>
      </div>
    </header>
  );
}
