import { Home, Calendar, Users, Settings, FolderOpen, Plus, ShoppingCart, Package, BarChart3 } from 'lucide-react';

interface Project {
  id: string;
  name: string;
  color: string;
}

const projects: Project[] = [
  { id: '1', name: 'Website Redesign', color: '#8B5CF6' },
  { id: '2', name: 'Mobile App', color: '#EC4899' },
  { id: '3', name: 'Marketing Campaign', color: '#10B981' },
  { id: '4', name: 'Product Launch', color: '#F59E0B' },
];

const menuItems = [
  { icon: Home, label: 'Home', active: true },
  { icon: Calendar, label: 'Calendar', active: false },
  { icon: Users, label: 'Clients', active: false },
  { icon: ShoppingCart, label: 'Sales', active: false },
  { icon: Package, label: 'Products', active: false },
  { icon: BarChart3, label: 'Dashboard', active: false },
  { icon: FolderOpen, label: 'Projects', active: false },
  { icon: Settings, label: 'Settings', active: false },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-[#2D2D2D] h-screen flex flex-col p-6">
      {/* Logo */}
      <div className="mb-10">
        <div className="text-white font-semibold text-xl">ProjectHub</div>
      </div>

      {/* Navigation Menu */}
      <nav className="mb-8">
        <ul className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.label}>
                <button
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                    item.active
                      ? 'bg-white/10 text-white'
                      : 'text-gray-400 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-sm">{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Projects List */}
      <div className="flex-1 overflow-y-auto">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-gray-400 text-xs uppercase tracking-wider font-medium">
            Projects
          </h3>
          <button className="text-gray-400 hover:text-white transition-colors">
            <Plus className="w-4 h-4" />
          </button>
        </div>
        <ul className="space-y-1">
          {projects.map((project) => (
            <li key={project.id}>
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-white/5 transition-colors group">
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: project.color }}
                />
                <span className="text-sm truncate">{project.name}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* CTA Button */}
      <div className="mt-6">
        <button className="w-full bg-[#FF6B35] hover:bg-[#FF5722] text-white px-4 py-3 rounded-lg font-medium text-sm transition-colors shadow-lg">
          Add billing info
        </button>
      </div>
    </aside>
  );
}