/**
 * Trucks.jsx — Truck list with add/edit/delete modal. Manager only.
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import StatusBadge from "../components/StatusBadge";
import api from "../api";

const TRUCK_TYPES = [
  "Automated Garbage Truck",
  "Roll-Off Truck",
  "Dumpster/Compactor Truck",
  "Rear-Load Truck",
  "Side-Load Truck",
  "Other",
];

const DEFAULT_FORM = {
  truck_number: "",
  make: "",
  model: "",
  year: new Date().getFullYear(),
  truck_type: "",
  current_mileage: 0,
  vin: "",
  notes: "",
};

export default function Trucks() {
  const navigate = useNavigate();
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null); // null | "add" | truck object
  const [form, setForm] = useState(DEFAULT_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => { load(); }, []);

  async function load() {
    const res = await api.get("/trucks");
    setTrucks(res.data);
    setLoading(false);
  }

  function openAdd() {
    setForm(DEFAULT_FORM);
    setError("");
    setModal("add");
  }

  function openEdit(truck) {
    setForm({
      truck_number: truck.truck_number,
      make: truck.make,
      model: truck.model,
      year: truck.year,
      truck_type: truck.truck_type || "",
      current_mileage: truck.current_mileage,
      vin: truck.vin || "",
      notes: truck.notes || "",
    });
    setError("");
    setModal(truck);
  }

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      if (modal === "add") {
        await api.post("/trucks", form);
      } else {
        await api.put(`/trucks/${modal.id}`, form);
      }
      setModal(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id) {
    try {
      await api.delete(`/trucks/${id}`);
      setDeleteConfirm(null);
      load();
    } catch {
      alert("Failed to delete truck.");
    }
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Trucks</h1>
            <p className="text-sm text-gray-500">{trucks.length} vehicles in fleet</p>
          </div>
          <button
            onClick={openAdd}
            className="bg-[#68ccd1] hover:bg-[#4db8be] text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
          >
            + Add Truck
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68ccd1]" />
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3 text-left">Truck</th>
                  <th className="px-4 py-3 text-left hidden sm:table-cell">Type</th>
                  <th className="px-4 py-3 text-left hidden md:table-cell">Mileage</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {trucks.map((truck) => (
                  <tr key={truck.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-semibold text-gray-900">{truck.truck_number}</div>
                      <div className="text-xs text-gray-400">{truck.year} {truck.make} {truck.model}</div>
                    </td>
                    <td className="px-4 py-3 text-gray-500 hidden sm:table-cell text-xs">
                      {truck.truck_type || "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-600 hidden md:table-cell">
                      {truck.current_mileage.toLocaleString()} mi
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={truck.overall_status} />
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => navigate(`/trucks/${truck.id}`)}
                          className="text-[#68ccd1] hover:underline text-xs font-medium"
                        >
                          View
                        </button>
                        <button
                          onClick={() => openEdit(truck)}
                          className="text-gray-500 hover:text-gray-700 text-xs"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(truck)}
                          className="text-red-400 hover:text-red-600 text-xs"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {trucks.length === 0 && (
              <div className="text-center py-12 text-gray-400 text-sm">
                No trucks yet. Add your first truck to get started.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Add / Edit Modal */}
      {modal !== null && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="font-bold text-gray-900">
                {modal === "add" ? "Add New Truck" : `Edit ${modal.truck_number}`}
              </h2>
              <button onClick={() => setModal(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <form onSubmit={handleSave} className="px-6 py-4 space-y-3">
              <Field label="Truck Number" value={form.truck_number} onChange={(v) => set("truck_number", v)} placeholder="e.g. T-01" required />
              <div className="grid grid-cols-2 gap-3">
                <Field label="Make" value={form.make} onChange={(v) => set("make", v)} placeholder="e.g. Mack" required />
                <Field label="Model" value={form.model} onChange={(v) => set("model", v)} placeholder="e.g. LR Series" required />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Field label="Year" type="number" value={form.year} onChange={(v) => set("year", parseInt(v))} required />
                <Field label="Current Mileage" type="number" value={form.current_mileage} onChange={(v) => set("current_mileage", parseInt(v))} required />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Truck Type</label>
                <select
                  value={form.truck_type}
                  onChange={(e) => set("truck_type", e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">Select type…</option>
                  {TRUCK_TYPES.map((t) => <option key={t}>{t}</option>)}
                </select>
              </div>
              <Field label="VIN (optional)" value={form.vin} onChange={(v) => set("vin", v)} />
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={form.notes}
                  onChange={(e) => set("notes", e.target.value)}
                  rows={2}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none"
                />
              </div>
              {error && <p className="text-red-600 text-xs">{error}</p>}
              <div className="flex gap-2 pt-2">
                <button type="button" onClick={() => setModal(null)} className="flex-1 border border-gray-300 text-gray-700 font-medium py-2 rounded-lg text-sm">Cancel</button>
                <button type="submit" disabled={saving} className="flex-1 bg-[#68ccd1] text-white font-semibold py-2 rounded-lg text-sm disabled:opacity-60">
                  {saving ? "Saving…" : "Save"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-sm p-6 text-center">
            <div className="text-4xl mb-3">🗑️</div>
            <h2 className="font-bold text-gray-900 mb-2">Delete {deleteConfirm.truck_number}?</h2>
            <p className="text-sm text-gray-500 mb-5">This will permanently delete the truck and all its maintenance history.</p>
            <div className="flex gap-2">
              <button onClick={() => setDeleteConfirm(null)} className="flex-1 border border-gray-300 text-gray-700 font-medium py-2 rounded-lg text-sm">Cancel</button>
              <button onClick={() => handleDelete(deleteConfirm.id)} className="flex-1 bg-red-500 text-white font-semibold py-2 rounded-lg text-sm">Delete</button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}

function Field({ label, value, onChange, type = "text", placeholder, required }) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#68ccd1]"
      />
    </div>
  );
}
