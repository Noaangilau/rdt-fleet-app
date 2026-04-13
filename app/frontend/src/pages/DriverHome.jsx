/**
 * DriverHome.jsx — Landing page for drivers. Shows two main actions.
 */

import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function DriverHome() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-[#68ccd1] flex items-center justify-center text-white text-xs font-bold">
            RDT
          </div>
          <div>
            <div className="text-sm font-bold text-gray-900">RDT Inc.</div>
            <div className="text-xs text-gray-400">Hi, {user?.full_name?.split(" ")[0] || user?.username}</div>
          </div>
        </div>
        <button onClick={handleLogout} className="text-xs text-red-500">Sign out</button>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="w-full max-w-sm">
          <h1 className="text-2xl font-bold text-gray-900 mb-1 text-center">Welcome back</h1>
          <p className="text-sm text-gray-500 mb-8 text-center">What would you like to do today?</p>

          <button
            onClick={() => navigate("/mileage")}
            className="w-full bg-[#68ccd1] hover:bg-[#4db8be] text-white font-bold py-5 rounded-2xl text-base mb-4 transition-colors"
          >
            Log Mileage
          </button>

          <button
            onClick={() => navigate("/incident")}
            className="w-full bg-white border-2 border-gray-200 text-gray-800 font-bold py-5 rounded-2xl text-base transition-colors hover:border-[#68ccd1]"
          >
            Report an Incident
          </button>

          <button
            onClick={() => navigate("/checkin")}
            className="w-full bg-white border-2 border-gray-200 text-gray-800 font-bold py-5 rounded-2xl text-base transition-colors hover:border-[#68ccd1]"
          >
            Update My Status
          </button>
        </div>
      </div>
    </div>
  );
}
