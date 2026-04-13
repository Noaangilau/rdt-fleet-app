/**
 * TruckDetail.jsx — Per-truck maintenance table with "Record Service" action.
 */

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import StatusBadge from "../components/StatusBadge";
import api from "../api";

export default function TruckDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [truck, setTruck] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [serviceModal, setServiceModal] = useState(null);
  const [serviceForm, setServiceForm] = useState({ last_service_date: "", last_service_mileage: "", notes: "" });
  const [saving, setSaving] = useState(false);

  useEffect(() => { load(); }, [id]);

  async function load() {
    const [truckRes, maintRes] = await Promise.all([
      api.get(`/trucks/${id}`),
      api.get(`/trucks/${id}/maintenance`),
    ]);
    setTruck(truckRes.data);
    setItems(maintRes.data);
    setLoading(false);
  }

  function openService(item) {
    setServiceForm({
      last_service_date: new Date().toISOString().slice(0, 10),
      last_service_mileage: truck?.current_mileage || "",
      notes: "",
    });
    setServiceModal(item);
  }

  async function handleService(e) {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put(`/trucks/${id}/maintenance/${serviceModal.id}`, {
        last_service_date: serviceForm.last_service_date,
        last_service_mileage: parseInt(serviceForm.last_service_mileage) || null,
        notes: serviceForm.notes || null,
      });
      setServiceModal(null);
      load();
    } finally {
      setSaving(false);
    }
  }

  const statusRow = {
    red: "bg-red-50",
    yellow: "bg-yellow-50",
    green: "",
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68ccd1]" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Breadcrumb */}
        <button onClick={() => navigate("/trucks")} className="text-sm text-[#68ccd1] mb-4 hover:underline">
          ← All Trucks
        </button>

        {/* Truck header */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{truck.truck_number}</h1>
              <p className="text-gray-500">{truck.year} {truck.make} {truck.model}</p>
              {truck.truck_type && <p className="text-sm text-gray-400">{truck.truck_type}</p>}
            </div>
            <StatusBadge status={truck.overall_status} size="lg" />
          </div>
          <div className="mt-4 flex gap-6 text-sm">
            <div>
              <span className="text-gray-400">Mileage</span>
              <div className="font-semibold text-gray-900">{truck.current_mileage.toLocaleString()} mi</div>
            </div>
            {truck.vin && (
              <div>
                <span className="text-gray-400">VIN</span>
                <div className="font-mono text-gray-700 text-xs mt-0.5">{truck.vin}</div>
              </div>
            )}
            {truck.notes && (
              <div className="flex-1">
                <span className="text-gray-400">Notes</span>
                <div className="text-gray-700 text-sm mt-0.5">{truck.notes}</div>
              </div>
            )}
          </div>
        </div>

        {/* Maintenance table */}
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Maintenance Items</h2>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3 text-left">Item</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-left hidden md:table-cell">Last Service</th>
                  <th className="px-4 py-3 text-left hidden lg:table-cell">Next Due</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {items.map((item) => (
                  <tr key={item.id} className={statusRow[item.status]}>
                    <td className="px-4 py-3 font-medium text-gray-900">{item.item_label}</td>
                    <td className="px-4 py-3">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="px-4 py-3 text-gray-500 hidden md:table-cell">
                      {item.last_service_date ? (
                        <div>
                          <div>{item.last_service_date}</div>
                          {item.last_service_mileage && (
                            <div className="text-xs text-gray-400">{item.last_service_mileage.toLocaleString()} mi</div>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-300 italic">Never</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-500 hidden lg:table-cell">
                      <div className="space-y-0.5">
                        {item.next_due_mileage && (
                          <div className="text-xs">
                            {item.next_due_mileage.toLocaleString()} mi
                            {item.miles_remaining !== null && (
                              <span className={`ml-1 ${item.miles_remaining < 0 ? "text-red-500" : "text-gray-400"}`}>
                                ({item.miles_remaining > 0 ? "+" : ""}{item.miles_remaining.toLocaleString()})
                              </span>
                            )}
                          </div>
                        )}
                        {item.next_due_date && (
                          <div className="text-xs">
                            {item.next_due_date}
                            {item.days_remaining !== null && (
                              <span className={`ml-1 ${item.days_remaining < 0 ? "text-red-500" : "text-gray-400"}`}>
                                ({item.days_remaining > 0 ? "+" : ""}{item.days_remaining}d)
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => openService(item)}
                        className="text-xs bg-[#68ccd1]/10 text-[#3aa3a8] font-semibold px-3 py-1.5 rounded-lg hover:bg-[#68ccd1]/20 transition-colors"
                      >
                        Record Service
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Service Modal */}
      {serviceModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-sm">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="font-bold text-gray-900">Record Service — {serviceModal.item_label}</h2>
              <button onClick={() => setServiceModal(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <form onSubmit={handleService} className="px-6 py-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Service Date</label>
                <input
                  type="date"
                  value={serviceForm.last_service_date}
                  onChange={(e) => setServiceForm((f) => ({ ...f, last_service_date: e.target.value }))}
                  required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Mileage at Service</label>
                <input
                  type="number"
                  value={serviceForm.last_service_mileage}
                  onChange={(e) => setServiceForm((f) => ({ ...f, last_service_mileage: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  placeholder="optional"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={serviceForm.notes}
                  onChange={(e) => setServiceForm((f) => ({ ...f, notes: e.target.value }))}
                  rows={2}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none"
                  placeholder="optional"
                />
              </div>
              <div className="flex gap-2 pt-1">
                <button type="button" onClick={() => setServiceModal(null)} className="flex-1 border border-gray-300 text-gray-700 font-medium py-2 rounded-lg text-sm">Cancel</button>
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
