/**
 * DriverIncident.jsx — Mobile-first incident report form for drivers.
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import api from "../api";

export default function DriverIncident() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [trucks, setTrucks] = useState([]);
  const [form, setForm] = useState({
    truck_id: "",
    incident_date: new Date().toISOString().slice(0, 10),
    description: "",
    severity: "medium",
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/trucks/summary").then((res) => setTrucks(res.data));
  }, []);

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/incidents", {
        ...form,
        truck_id: parseInt(form.truck_id),
      });
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to submit report.");
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    logout();
    navigate("/login");
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
        <div className="text-center max-w-sm">
          <div className="text-5xl mb-4">📋</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Report Submitted</h2>
          <p className="text-gray-500 text-sm mb-6">Your incident report has been sent to the manager.</p>
          <button
            onClick={() => { setSuccess(false); setForm({ truck_id: "", incident_date: new Date().toISOString().slice(0, 10), description: "", severity: "medium" }); }}
            className="w-full bg-[#68ccd1] text-white font-semibold py-3 rounded-xl text-sm"
          >
            Submit Another
          </button>
          <button
            onClick={() => navigate("/driver-home")}
            className="w-full mt-3 border border-gray-300 text-gray-700 font-medium py-3 rounded-xl text-sm"
          >
            Back to Home
          </button>
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
            <div className="text-xs text-gray-400">Hi, {user?.full_name?.split(" ")[0]}</div>
          </div>
        </div>
        <button onClick={handleLogout} className="text-xs text-red-500">Sign out</button>
      </div>

      {/* Form */}
      <div className="flex-1 px-4 py-6 max-w-md mx-auto w-full">
        <h1 className="text-xl font-bold text-gray-900 mb-1">Report Incident</h1>
        <p className="text-sm text-gray-500 mb-6">Fill out all fields and submit to the manager.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Truck</label>
            <select
              value={form.truck_id}
              onChange={(e) => set("truck_id", e.target.value)}
              required
              className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#68ccd1]"
            >
              <option value="">Choose your truck…</option>
              {trucks.map((t) => (
                <option key={t.id} value={t.id}>{t.truck_number} — {t.make} {t.model}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Date of Incident</label>
            <input
              type="date"
              value={form.incident_date}
              onChange={(e) => set("incident_date", e.target.value)}
              required
              className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#68ccd1]"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Severity</label>
            <div className="flex gap-2">
              {["low", "medium", "high"].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => set("severity", s)}
                  className={`flex-1 py-3 rounded-xl text-sm font-semibold capitalize border-2 transition-colors ${
                    form.severity === s
                      ? s === "high"
                        ? "bg-red-500 text-white border-red-500"
                        : s === "medium"
                        ? "bg-yellow-400 text-white border-yellow-400"
                        : "bg-green-500 text-white border-green-500"
                      : "bg-white text-gray-500 border-gray-200"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Description</label>
            <textarea
              value={form.description}
              onChange={(e) => set("description", e.target.value)}
              required
              rows={5}
              placeholder="Describe what happened…"
              className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#68ccd1] resize-none"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#68ccd1] hover:bg-[#4db8be] text-white font-bold py-4 rounded-xl text-base transition-colors disabled:opacity-60"
          >
            {loading ? "Submitting…" : "Submit Report"}
          </button>
        </form>

        <div className="mt-8 text-center">
          <button onClick={() => navigate("/driver-home")} className="text-sm text-gray-500 underline">
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
