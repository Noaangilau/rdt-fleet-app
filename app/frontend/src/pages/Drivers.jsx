/**
 * Drivers.jsx — Manager creates/manages driver accounts.
 */

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import api from "../api";

export default function Drivers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null); // null | "add" | user object
  const [form, setForm] = useState({ username: "", full_name: "", password: "", role: "driver", is_active: true });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => { load(); }, []);

  async function load() {
    const res = await api.get("/users");
    setUsers(res.data);
    setLoading(false);
  }

  function openAdd() {
    setForm({ username: "", full_name: "", password: "", role: "driver", is_active: true });
    setError("");
    setModal("add");
  }

  function openEdit(user) {
    setForm({ username: user.username, full_name: user.full_name, password: "", role: user.role, is_active: user.is_active });
    setError("");
    setModal(user);
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
        await api.post("/users", form);
      } else {
        const payload = {};
        if (form.full_name !== modal.full_name) payload.full_name = form.full_name;
        if (form.password) payload.password = form.password;
        if (form.is_active !== modal.is_active) payload.is_active = form.is_active;
        await api.put(`/users/${modal.id}`, payload);
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
      await api.delete(`/users/${id}`);
      setDeleteConfirm(null);
      load();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete.");
    }
  }

  return (
    <Layout>
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Drivers & Users</h1>
            <p className="text-sm text-gray-500">{users.length} accounts</p>
          </div>
          <button
            onClick={openAdd}
            className="bg-[#68ccd1] hover:bg-[#4db8be] text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
          >
            + Add Driver
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
                  <th className="px-4 py-3 text-left">Name</th>
                  <th className="px-4 py-3 text-left hidden sm:table-cell">Username</th>
                  <th className="px-4 py-3 text-left">Role</th>
                  <th className="px-4 py-3 text-left hidden sm:table-cell">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {users.map((u) => (
                  <tr key={u.id} className={!u.is_active ? "opacity-50" : ""}>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{u.full_name}</div>
                    </td>
                    <td className="px-4 py-3 text-gray-500 hidden sm:table-cell font-mono text-xs">{u.username}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full capitalize ${
                        u.role === "manager" ? "bg-[#68ccd1]/15 text-[#3aa3a8]" : "bg-gray-100 text-gray-600"
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="px-4 py-3 hidden sm:table-cell">
                      <span className={`text-xs ${u.is_active ? "text-green-600" : "text-gray-400"}`}>
                        {u.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => openEdit(u)} className="text-xs text-gray-500 hover:text-gray-700">Edit</button>
                        <button onClick={() => setDeleteConfirm(u)} className="text-xs text-red-400 hover:text-red-600">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add / Edit Modal */}
      {modal !== null && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-sm">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="font-bold text-gray-900">{modal === "add" ? "Add Driver" : `Edit ${modal.full_name}`}</h2>
              <button onClick={() => setModal(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <form onSubmit={handleSave} className="px-6 py-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Full Name</label>
                <input type="text" value={form.full_name} onChange={(e) => set("full_name", e.target.value)} required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="First Last" />
              </div>
              {modal === "add" && (
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Username</label>
                  <input type="text" value={form.username} onChange={(e) => set("username", e.target.value)} required
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="jsmith" />
                </div>
              )}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  {modal === "add" ? "Password" : "New Password (leave blank to keep)"}
                </label>
                <input type="password" value={form.password} onChange={(e) => set("password", e.target.value)}
                  required={modal === "add"}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
              </div>
              {modal === "add" && (
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Role</label>
                  <select value={form.role} onChange={(e) => set("role", e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                    <option value="driver">Driver</option>
                    <option value="manager">Manager</option>
                  </select>
                </div>
              )}
              {modal !== "add" && (
                <div className="flex items-center gap-2">
                  <input type="checkbox" id="active" checked={form.is_active} onChange={(e) => set("is_active", e.target.checked)} />
                  <label htmlFor="active" className="text-sm text-gray-700">Account active</label>
                </div>
              )}
              {error && <p className="text-red-600 text-xs">{error}</p>}
              <div className="flex gap-2 pt-1">
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
            <div className="text-4xl mb-3">👤</div>
            <h2 className="font-bold text-gray-900 mb-2">Delete {deleteConfirm.full_name}?</h2>
            <p className="text-sm text-gray-500 mb-5">This account will be permanently removed.</p>
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
