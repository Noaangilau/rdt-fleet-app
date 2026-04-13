/**
 * DriverCheckin.jsx — Driver availability check-in page.
 * Drivers update their duty status (on_duty, available, off_duty).
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import api from "../api";

const STATUS_OPTIONS = [
  {
    value: "on_duty",
    label: "On Duty",
    colorClass: "bg-green-500",
    desc: "Currently driving / working a route",
  },
  {
    value: "available",
    label: "Available",
    colorClass: "bg-blue-500",
    desc: "Ready to be dispatched",
  },
  {
    value: "off_duty",
    label: "Off Duty",
    colorClass: "bg-gray-400",
    desc: "Not available today",
  },
];

export default function DriverCheckin() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [currentRoute, setCurrentRoute] = useState("");
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [savedStatus, setSavedStatus] = useState(null);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!selectedStatus) return;

    setError("");
    setSaving(true);
    try {
      const res = await api.put("/operations/availability", {
        status: selectedStatus,
        current_route: currentRoute || null,
      });
      setSavedStatus(res.data.status);
      setSuccess(true);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Failed to update status.");
    } finally {
      setSaving(false);
    }
  }

  function handleLogout() {
    logout();
    navigate("/login");
  }

  if (success) {
    const opt = STATUS_OPTIONS.find((o) => o.value === savedStatus);
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
        <div className="text-center max-w-sm">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Status Updated</h2>
          <p className="text-gray-500 text-sm mb-2">
            You are now marked as{" "}
            <span className="font-semibold text-gray-800">{opt?.label || savedStatus}</span>.
          </p>
          <p className="text-xs text-gray-400 mb-6">{opt?.desc}</p>
          <button
            onClick={() => navigate("/driver-home")}
            className="w-full bg-[#68ccd1] text-white font-semibold py-3 rounded-xl text-sm"
          >
            Back to Home
          </button>
          <div className="mt-4">
            <button
              onClick={() => {
                setSuccess(false);
                setSelectedStatus(null);
                setCurrentRoute("");
              }}
              className="text-sm text-gray-500 underline"
            >
              Update Again
            </button>
          </div>
        </div>
      </div>
    );
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
            <div className="text-xs text-gray-400">
              Hi, {user?.full_name?.split(" ")[0] || user?.username}
            </div>
          </div>
        </div>
        <button onClick={handleLogout} className="text-xs text-red-500">
          Sign out
        </button>
      </div>

      {/* Form */}
      <div className="flex-1 px-4 py-6 max-w-md mx-auto w-full">
        <h1 className="text-xl font-bold text-gray-900 mb-1">Check In</h1>
        <p className="text-sm text-gray-500 mb-6">Update your duty status for today.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Status selection */}
          <div className="space-y-3">
            {STATUS_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setSelectedStatus(opt.value)}
                className={`w-full flex items-center gap-4 px-4 py-4 rounded-xl border-2 transition-colors text-left ${
                  selectedStatus === opt.value
                    ? "border-[#68ccd1] bg-[#68ccd1]/10"
                    : "border-gray-200 bg-white"
                }`}
              >
                <div className={`w-3 h-3 rounded-full ${opt.colorClass} flex-shrink-0`} />
                <div className="flex-1">
                  <div className="font-semibold text-gray-900 text-sm">{opt.label}</div>
                  <div className="text-xs text-gray-500">{opt.desc}</div>
                </div>
                {selectedStatus === opt.value && (
                  <div className="text-[#68ccd1] font-bold text-lg">✓</div>
                )}
              </button>
            ))}
          </div>

          {/* Route field — only shown when On Duty */}
          {selectedStatus === "on_duty" && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Route / Area{" "}
                <span className="text-gray-400 font-normal">(optional)</span>
              </label>
              <input
                type="text"
                value={currentRoute}
                onChange={(e) => setCurrentRoute(e.target.value)}
                placeholder="e.g. North Basin Residential"
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#68ccd1]"
              />
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={saving || !selectedStatus}
            className="w-full bg-[#68ccd1] hover:bg-[#4db8be] text-white font-bold py-4 rounded-xl text-base transition-colors disabled:opacity-60 mt-2"
          >
            {saving ? "Saving…" : "Update Status"}
          </button>
        </form>

        <div className="mt-8 text-center">
          <button
            onClick={() => navigate("/driver-home")}
            className="text-sm text-gray-500 underline"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
