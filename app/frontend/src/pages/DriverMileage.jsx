/**
 * DriverMileage.jsx — Mobile-first mileage reporting page for drivers.
 * Drivers select their truck and submit the current odometer reading.
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import api from "../api";

export default function DriverMileage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [trucks, setTrucks] = useState([]);
  const [truckId, setTruckId] = useState("");
  const [mileage, setMileage] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/trucks/summary").then((res) => setTrucks(res.data));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/mileage", {
        truck_id: parseInt(truckId),
        mileage: parseInt(mileage),
      });
      setSuccess(true);
      setMileage("");
      setTruckId("");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Failed to submit mileage.");
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
          <div className="text-5xl mb-4">🛣️</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Mileage Updated</h2>
          <p className="text-gray-500 text-sm mb-6">Your odometer reading has been recorded.</p>
          <button
            onClick={() => { setSuccess(false); setMileage(""); setTruckId(""); }}
            className="w-full bg-[#68ccd1] text-white font-semibold py-3 rounded-xl text-sm"
          >
            Log Another
          </button>
          <div className="mt-4">
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
        <h1 className="text-xl font-bold text-gray-900 mb-1">Log Mileage</h1>
        <p className="text-sm text-gray-500 mb-6">Enter your truck's current odometer reading.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Select Truck
            </label>
            <select
              value={truckId}
              onChange={(e) => setTruckId(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#68ccd1]"
            >
              <option value="">Choose your truck…</option>
              {trucks.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.truck_number} — {t.make} {t.model}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Current Odometer (miles)
            </label>
            <input
              type="number"
              value={mileage}
              onChange={(e) => setMileage(e.target.value)}
              required
              min="0"
              placeholder="e.g. 85400"
              className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#68ccd1]"
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
            className="w-full bg-[#68ccd1] hover:bg-[#4db8be] text-white font-bold py-4 rounded-xl text-base transition-colors disabled:opacity-60 mt-2"
          >
            {loading ? "Submitting…" : "Submit Mileage"}
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
