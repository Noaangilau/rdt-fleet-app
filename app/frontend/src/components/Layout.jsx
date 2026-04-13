/**
 * Layout.jsx — Responsive sidebar shell for all manager pages.
 * Collapses to a bottom nav on mobile.
 */

import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/trucks", label: "Trucks", icon: "🚛" },
  { to: "/incidents", label: "Incidents", icon: "⚠️" },
  { to: "/drivers", label: "Drivers", icon: "👷" },
  { to: "/ai", label: "AI Assistant", icon: "🤖" },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar — hidden on mobile */}
      <aside className="hidden md:flex flex-col w-56 bg-white border-r border-gray-200 fixed h-full z-10">
        {/* Logo area */}
        <div className="flex items-center gap-2 px-4 py-5 border-b border-gray-200">
          <div className="w-8 h-8 rounded-full bg-[#68ccd1] flex items-center justify-center text-white text-xs font-bold">
            RDT
          </div>
          <div>
            <div className="text-sm font-bold text-gray-900">RDT Inc.</div>
            <div className="text-xs text-gray-400">Fleet Management</div>
          </div>
        </div>

        {/* Nav links */}
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-[#68ccd1]/15 text-[#3aa3a8]"
                    : "text-gray-600 hover:bg-gray-100"
                }`
              }
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* User footer */}
        <div className="px-4 py-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 mb-1">{user?.full_name || user?.username}</div>
          <div className="text-xs text-gray-400 mb-3 capitalize">{user?.role}</div>
          <button
            onClick={handleLogout}
            className="text-xs text-red-500 hover:text-red-700 transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 md:ml-56 pb-16 md:pb-0">
        {/* Mobile header */}
        <div className="md:hidden bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-[#68ccd1] flex items-center justify-center text-white text-xs font-bold">
              RDT
            </div>
            <span className="font-bold text-gray-900 text-sm">Fleet Management</span>
          </div>
          <button onClick={handleLogout} className="text-xs text-red-500">
            Sign out
          </button>
        </div>

        {/* Page content */}
        <div className="p-4 md:p-6">{children}</div>
      </main>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex z-10">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center py-2 text-xs transition-colors ${
                isActive ? "text-[#68ccd1]" : "text-gray-500"
              }`
            }
          >
            <span className="text-lg">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
