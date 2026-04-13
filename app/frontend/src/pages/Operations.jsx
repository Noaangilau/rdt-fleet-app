/**
 * Operations.jsx — Driver availability and dispatch management.
 */

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import api from "../api";

const statusColor = {
  on_duty: "bg-green-100 text-green-700",
  available: "bg-blue-100 text-blue-700",
  off_duty: "bg-gray-100 text-gray-500",
};

const statusLabel = {
  on_duty: "On Duty",
  available: "Available",
  off_duty: "Off Duty",
};

export default function Operations() {
  const [availability, setAvailability] = useState([]);
  const [missedPickups, setMissedPickups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editId, setEditId] = useState(null);
  const [editStatus, setEditStatus] = useState("");

  function loadAll() {
    Promise.all([
      api.get("/operations/availability"),
      api.get("/operations/missed-pickups"),
    ]).then(([aRes, mRes]) => {
      setAvailability(aRes.data);
      setMissedPickups(mRes.data);
      setLoading(false);
    });
  }

  useEffect(() => { loadAll(); }, []);

  async function saveStatus(userId) {
    await api.put("/operations/availability", { status: editStatus, user_id: userId });
    setEditId(null);
    loadAll();
  }

  async function approvePickup(id) {
    await api.put(`/operations/missed-pickups/${id}/approve`);
    loadAll();
  }

  if (loading) return (
    <Layout>
      <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68ccd1]" /></div>
    </Layout>
  );

  return (
    <Layout>
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Operations</h1>
        <p className="text-sm text-gray-500 mb-6">Driver availability and dispatch</p>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Driver Availability */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Driver Availability</h2>
            {availability.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-200 p-6 text-center text-gray-400 text-sm">
                No drivers found. Add drivers in the Drivers section.
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
                {availability.map((d) => (
                  <div key={d.driver_id} className="flex items-center justify-between px-4 py-3">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {d.driver_name || d.username}
                      </div>
                      <div className="text-xs text-gray-400">{d.username}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      {editId === d.driver_id ? (
                        <div className="flex gap-1 items-center">
                          <select
                            value={editStatus}
                            onChange={(e) => setEditStatus(e.target.value)}
                            className="text-xs border border-gray-200 rounded px-2 py-1"
                          >
                            <option value="on_duty">On Duty</option>
                            <option value="available">Available</option>
                            <option value="off_duty">Off Duty</option>
                          </select>
                          <button onClick={() => saveStatus(d.driver_id)}
                            className="text-xs bg-[#68ccd1] text-white px-2 py-1 rounded">
                            Save
                          </button>
                          <button onClick={() => setEditId(null)}
                            className="text-xs text-gray-400">✕</button>
                        </div>
                      ) : (
                        <>
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColor[d.status]}`}>
                            {statusLabel[d.status] || d.status}
                          </span>
                          <button
                            onClick={() => { setEditId(d.driver_id); setEditStatus(d.status); }}
                            className="text-xs text-[#68ccd1] hover:text-[#3aa3a8]"
                          >
                            Edit
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Missed Pickups */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Missed Pickups</h2>
            {missedPickups.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-200 p-6 text-center text-gray-400 text-sm">
                No missed pickups reported
              </div>
            ) : (
              <div className="space-y-2">
                {missedPickups.map((p) => (
                  <div key={p.id} className="bg-white rounded-xl border border-gray-200 p-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {p.route_name || "Unknown route"}
                        </div>
                        {p.notes && <p className="text-xs text-gray-500 mt-0.5">{p.notes}</p>}
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(p.reported_at).toLocaleDateString()}
                        </p>
                      </div>
                      {!p.manager_approved ? (
                        <button
                          onClick={() => approvePickup(p.id)}
                          className="text-xs bg-green-600 text-white rounded px-2 py-1 shrink-0"
                        >
                          Approve
                        </button>
                      ) : (
                        <span className="text-xs text-green-600 font-medium shrink-0">Approved</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
