/**
 * Incidents.jsx — Incident list with manager status update + resolution modal.
 */

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import api from "../api";

const SEVERITY_COLOR = {
  high: "bg-red-100 text-red-700 border border-red-200",
  medium: "bg-yellow-100 text-yellow-700 border border-yellow-200",
  low: "bg-green-100 text-green-700 border border-green-200",
};
const STATUS_COLOR = {
  open: "bg-red-50 text-red-600",
  in_review: "bg-yellow-50 text-yellow-700",
  resolved: "bg-green-50 text-green-700",
};

export default function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [filter, setFilter] = useState("open");
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState({ status: "", resolution_notes: "" });
  const [saving, setSaving] = useState(false);

  useEffect(() => { load(); }, [filter]);

  async function load() {
    setLoading(true);
    const url = filter === "all" ? "/incidents" : `/incidents?status_filter=${filter}`;
    const res = await api.get(url);
    setIncidents(res.data);
    setLoading(false);
  }

  function openModal(inc) {
    setForm({ status: inc.status, resolution_notes: inc.resolution_notes || "" });
    setModal(inc);
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put(`/incidents/${modal.id}`, form);
      setModal(null);
      load();
    } finally {
      setSaving(false);
    }
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Incidents</h1>
            <p className="text-sm text-gray-500">Driver-submitted incident reports</p>
          </div>
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 mb-5">
          {["open", "in_review", "resolved", "all"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize transition-colors ${
                filter === f
                  ? "bg-[#68ccd1] text-white"
                  : "bg-white border border-gray-200 text-gray-600 hover:bg-gray-50"
              }`}
            >
              {f.replace("_", " ")}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68ccd1]" />
          </div>
        ) : incidents.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 text-center py-12 text-gray-400 text-sm">
            No {filter === "all" ? "" : filter} incidents found.
          </div>
        ) : (
          <div className="space-y-3">
            {incidents.map((inc) => (
              <div key={inc.id} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded-full capitalize ${SEVERITY_COLOR[inc.severity]}`}>
                        {inc.severity}
                      </span>
                      <span className="text-sm font-semibold text-gray-800">{inc.truck_number || `Truck #${inc.truck_id}`}</span>
                      <span className="text-xs text-gray-400">{inc.incident_date}</span>
                    </div>
                    <p className="text-sm text-gray-700 mb-1">{inc.description}</p>
                    <p className="text-xs text-gray-400">Reported by {inc.driver_name}</p>
                    {inc.resolution_notes && (
                      <p className="text-xs text-gray-500 mt-2 italic">Resolution: {inc.resolution_notes}</p>
                    )}
                  </div>
                  <div className="flex flex-col items-end gap-2 shrink-0">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${STATUS_COLOR[inc.status]}`}>
                      {inc.status.replace("_", " ")}
                    </span>
                    <button
                      onClick={() => openModal(inc)}
                      className="text-xs text-[#68ccd1] font-medium hover:underline"
                    >
                      Update
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Update Modal */}
      {modal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-sm">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="font-bold text-gray-900">Update Incident</h2>
              <button onClick={() => setModal(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <form onSubmit={handleSave} className="px-6 py-4 space-y-4">
              <div>
                <p className="text-xs text-gray-500 mb-3">{modal.truck_number} · {modal.incident_date} · {modal.driver_name}</p>
                <p className="text-sm text-gray-700 mb-4">{modal.description}</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Status</label>
                <div className="flex gap-2">
                  {["open", "in_review", "resolved"].map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setForm((f) => ({ ...f, status: s }))}
                      className={`flex-1 py-2 rounded-lg text-xs font-semibold capitalize border-2 transition-colors ${
                        form.status === s ? "bg-[#68ccd1] text-white border-[#68ccd1]" : "bg-white text-gray-500 border-gray-200"
                      }`}
                    >
                      {s.replace("_", " ")}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Resolution Notes</label>
                <textarea
                  value={form.resolution_notes}
                  onChange={(e) => setForm((f) => ({ ...f, resolution_notes: e.target.value }))}
                  rows={3}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none"
                  placeholder="Describe how this was resolved…"
                />
              </div>
              <div className="flex gap-2">
                <button type="button" onClick={() => setModal(null)} className="flex-1 border border-gray-300 text-gray-700 font-medium py-2 rounded-lg text-sm">Cancel</button>
                <button type="submit" disabled={saving} className="flex-1 bg-[#68ccd1] text-white font-semibold py-2 rounded-lg text-sm disabled:opacity-60">
                  {saving ? "Saving…" : "Save"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  );
}
