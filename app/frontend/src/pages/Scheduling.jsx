/**
 * Scheduling.jsx — Route scheduling management.
 */

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import api from "../api";

export default function Scheduling() {
  const [routes, setRoutes] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editRoute, setEditRoute] = useState(null);
  const [form, setForm] = useState({ name: "", description: "", assigned_driver_id: "", assigned_truck_id: "", date: "" });

  function loadAll() {
    Promise.all([
      api.get("/operations/routes"),
      api.get("/users"),
      api.get("/trucks"),
    ]).then(([rRes, uRes, tRes]) => {
      setRoutes(rRes.data);
      setDrivers(uRes.data.filter((u) => u.role === "driver"));
      setTrucks(tRes.data);
      setLoading(false);
    });
  }

  useEffect(() => { loadAll(); }, []);

  function openNew() {
    setEditRoute(null);
    setForm({ name: "", description: "", assigned_driver_id: "", assigned_truck_id: "", date: new Date().toISOString().split("T")[0] });
    setShowForm(true);
  }

  function openEdit(r) {
    setEditRoute(r);
    setForm({
      name: r.name,
      description: r.description || "",
      assigned_driver_id: r.assigned_driver_id || "",
      assigned_truck_id: r.assigned_truck_id || "",
      date: r.date,
    });
    setShowForm(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const payload = {
      name: form.name,
      description: form.description || null,
      assigned_driver_id: form.assigned_driver_id ? parseInt(form.assigned_driver_id) : null,
      assigned_truck_id: form.assigned_truck_id ? parseInt(form.assigned_truck_id) : null,
      date: form.date,
    };
    if (editRoute) {
      await api.put(`/operations/routes/${editRoute.id}`, payload);
    } else {
      await api.post("/operations/routes", payload);
    }
    setShowForm(false);
    loadAll();
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this route?")) return;
    await api.delete(`/operations/routes/${id}`);
    loadAll();
  }

  if (loading) return (
    <Layout>
      <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68ccd1]" /></div>
    </Layout>
  );

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Scheduling</h1>
            <p className="text-sm text-gray-500">Route assignments and planning</p>
          </div>
          <button
            onClick={openNew}
            className="bg-[#68ccd1] text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-[#3aa3a8]"
          >
            + New Route
          </button>
        </div>

        {/* Route form */}
        {showForm && (
          <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
            <h2 className="text-base font-semibold text-gray-900 mb-4">
              {editRoute ? "Edit Route" : "New Route"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-gray-600 mb-1">Route Name *</label>
                  <input
                    required
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    placeholder="e.g. Vernal North Route"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Date *</label>
                  <input
                    required
                    type="date"
                    value={form.date}
                    onChange={(e) => setForm({ ...form, date: e.target.value })}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
                  <input
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    placeholder="Optional notes"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Assigned Driver</label>
                  <select
                    value={form.assigned_driver_id}
                    onChange={(e) => setForm({ ...form, assigned_driver_id: e.target.value })}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="">Unassigned</option>
                    {drivers.map((d) => (
                      <option key={d.id} value={d.id}>{d.full_name || d.username}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Assigned Truck</label>
                  <select
                    value={form.assigned_truck_id}
                    onChange={(e) => setForm({ ...form, assigned_truck_id: e.target.value })}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="">Unassigned</option>
                    {trucks.map((t) => (
                      <option key={t.id} value={t.id}>{t.truck_number} — {t.make} {t.model}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex gap-2 pt-1">
                <button type="submit" className="bg-[#68ccd1] text-white text-sm px-4 py-2 rounded-lg hover:bg-[#3aa3a8]">
                  {editRoute ? "Save" : "Create Route"}
                </button>
                <button type="button" onClick={() => setShowForm(false)} className="text-sm text-gray-500 px-4 py-2">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Routes list */}
        {routes.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-10 text-center text-gray-400">
            No routes scheduled. Click "+ New Route" to add one.
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
            {routes.map((r) => (
              <div key={r.id} className="flex items-center justify-between px-4 py-3">
                <div>
                  <div className="text-sm font-semibold text-gray-900">{r.name}</div>
                  <div className="text-xs text-gray-400 mt-0.5">
                    {r.date}
                    {r.assigned_driver_id && <span className="ml-2">· {r.assigned_driver_name || "Driver #" + r.assigned_driver_id}</span>}
                    {r.assigned_truck_id && <span className="ml-2">· {r.assigned_truck_number || "Truck #" + r.assigned_truck_id}</span>}
                  </div>
                  {r.description && <p className="text-xs text-gray-500 mt-0.5">{r.description}</p>}
                </div>
                <div className="flex gap-2">
                  <button onClick={() => openEdit(r)} className="text-xs text-[#68ccd1] hover:text-[#3aa3a8]">Edit</button>
                  <button onClick={() => handleDelete(r.id)} className="text-xs text-red-400 hover:text-red-600">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
