/**
 * Layout.jsx — Responsive sidebar shell for all manager pages.
 * Collapses to a bottom nav on mobile.
 */

import { useState, useEffect, useRef } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import api from "../api";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/trucks", label: "Trucks", icon: "🚛" },
  { to: "/incidents", label: "Incidents", icon: "⚠️" },
  { to: "/operations", label: "Operations", icon: "🗺️" },
  { to: "/scheduling", label: "Scheduling", icon: "📅" },
  { to: "/approvals", label: "Approvals", icon: "✅" },
  { to: "/hr", label: "HR", icon: "👷" },
  { to: "/financials", label: "Financials", icon: "💰" },
  { to: "/drivers", label: "Drivers", icon: "👥" },
  { to: "/ai", label: "AI Assistant", icon: "🤖" },
  { to: "/settings", label: "Settings", icon: "⚙️" },
];

const NOTIF_ICONS = {
  incident: "⚠️",
  missed_pickup: "📍",
  document_expiry: "📄",
  approval: "✅",
  checkin_reminder: "🕐",
};

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const notifRef = useRef(null);
  const mobileNotifRef = useRef(null);

  // Fetch unread count on mount and every 60 seconds
  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 60000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown when clicking outside either bell container
  useEffect(() => {
    function handleClickOutside(e) {
      const insideDesktop = notifRef.current?.contains(e.target);
      const insideMobile = mobileNotifRef.current?.contains(e.target);
      if (!insideDesktop && !insideMobile) {
        setShowNotifs(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function fetchUnreadCount() {
    try {
      const res = await api.get("/notifications/count");
      setUnreadCount(res.data.count);
    } catch {
      // silently ignore — user may not be authenticated yet
    }
  }

  async function openNotifications() {
    setShowNotifs((prev) => !prev);
    if (!showNotifs) {
      try {
        const res = await api.get("/notifications");
        setNotifications(res.data);
      } catch {
        setNotifications([]);
      }
    }
  }

  async function markAllRead() {
    await api.put("/notifications/read-all");
    setUnreadCount(0);
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }

  async function markRead(id) {
    await api.put(`/notifications/${id}/read`);
    setUnreadCount((c) => Math.max(0, c - 1));
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  }

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
          <div className="flex items-center justify-between mb-1">
            <div className="text-xs text-gray-500">{user?.full_name || user?.username}</div>
            {/* Bell icon */}
            <div className="relative" ref={notifRef}>
              <button
                onClick={openNotifications}
                className="relative text-gray-400 hover:text-gray-700 transition-colors"
                title="Notifications"
              >
                <span className="text-lg">🔔</span>
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[9px] font-bold rounded-full w-4 h-4 flex items-center justify-center">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </button>

              {/* Notifications dropdown */}
              {showNotifs && (
                <div className="absolute bottom-8 right-0 w-80 bg-white border border-gray-200 rounded-xl shadow-lg z-50 overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
                    <span className="text-sm font-semibold text-gray-800">Notifications</span>
                    {unreadCount > 0 && (
                      <button onClick={markAllRead} className="text-xs text-[#3aa3a8] hover:underline">
                        Mark all read
                      </button>
                    )}
                  </div>
                  <div className="max-h-72 overflow-y-auto divide-y divide-gray-50">
                    {notifications.length === 0 ? (
                      <div className="text-xs text-gray-400 text-center py-6">No notifications</div>
                    ) : (
                      notifications.map((n) => (
                        <div
                          key={n.id}
                          onClick={() => !n.read && markRead(n.id)}
                          className={`px-4 py-3 cursor-pointer transition-colors ${
                            n.read ? "bg-white" : "bg-blue-50 hover:bg-blue-100"
                          }`}
                        >
                          <div className="flex items-start gap-2">
                            <span className="text-base mt-0.5">{NOTIF_ICONS[n.type] || "🔔"}</span>
                            <div className="flex-1 min-w-0">
                              <p className={`text-xs leading-snug ${n.read ? "text-gray-500" : "text-gray-800 font-medium"}`}>
                                {n.message}
                              </p>
                              <p className="text-[10px] text-gray-400 mt-0.5">
                                {new Date(n.created_at).toLocaleString()}
                              </p>
                            </div>
                            {!n.read && (
                              <div className="w-2 h-2 rounded-full bg-blue-500 mt-1 flex-shrink-0" />
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
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
          <div className="flex items-center gap-3">
            {/* Mobile bell */}
            <div className="relative" ref={mobileNotifRef}>
              <button onClick={openNotifications} className="relative text-gray-400">
                <span className="text-lg">🔔</span>
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[9px] font-bold rounded-full w-4 h-4 flex items-center justify-center">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </button>
              {showNotifs && (
                <div className="absolute top-8 right-0 w-72 bg-white border border-gray-200 rounded-xl shadow-lg z-50 overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
                    <span className="text-sm font-semibold text-gray-800">Notifications</span>
                    {unreadCount > 0 && (
                      <button onClick={markAllRead} className="text-xs text-[#3aa3a8]">Mark all read</button>
                    )}
                  </div>
                  <div className="max-h-64 overflow-y-auto divide-y divide-gray-50">
                    {notifications.length === 0 ? (
                      <div className="text-xs text-gray-400 text-center py-6">No notifications</div>
                    ) : (
                      notifications.map((n) => (
                        <div
                          key={n.id}
                          onClick={() => !n.read && markRead(n.id)}
                          className={`px-4 py-3 cursor-pointer ${n.read ? "bg-white" : "bg-blue-50"}`}
                        >
                          <div className="flex items-start gap-2">
                            <span className="text-base mt-0.5">{NOTIF_ICONS[n.type] || "🔔"}</span>
                            <div className="flex-1">
                              <p className={`text-xs leading-snug ${n.read ? "text-gray-500" : "text-gray-800 font-medium"}`}>
                                {n.message}
                              </p>
                              <p className="text-[10px] text-gray-400 mt-0.5">
                                {new Date(n.created_at).toLocaleString()}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
            <button onClick={handleLogout} className="text-xs text-red-500">
              Sign out
            </button>
          </div>
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
