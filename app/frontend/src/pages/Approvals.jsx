/**
 * Approvals.jsx — Manager approval queue.
 */

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import api from "../api";

const statusColor = {
  pending: "bg-yellow-100 text-yellow-700",
  approved: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
};

export default function Approvals() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("pending");
  const [actionId, setActionId] = useState(null);
  const [notes, setNotes] = useState("");

  function load() {
    setLoading(true);
    api.get(`/operations/approvals?status_filter=${filter}`).then((res) => {
      setItems(res.data);
      setLoading(false);
    });
  }

  useEffect(() => { load(); }, [filter]);

  async function handleAction(id, action) {
    await api.put(`/operations/approvals/${id}`, { action, manager_notes: notes });
    setActionId(null);
    setNotes("");
    load();
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Approval Queue</h1>
        <p className="text-sm text-gray-500 mb-6">Review and act on pending requests</p>

        {/* Filter tabs */}
        <div className="flex gap-2 mb-6">
          {["pending", "approved", "rejected"].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors capitalize ${
                filter === s ? "bg-[#68ccd1] text-white" : "bg-white border border-gray-200 text-gray-600 hover:bg-gray-50"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68ccd1]" /></div>
        ) : items.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 px-4 py-10 text-center text-gray-400">
            No {filter} items
          </div>
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <div key={item.id} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-semibold text-gray-900 capitalize">
                        {item.type.replace(/_/g, " ")}
                      </span>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${statusColor[item.status]}`}>
                        {item.status}
                      </span>
                    </div>
                    {item.details && (
                      <p className="text-sm text-gray-600 mb-1">{item.details}</p>
                    )}
                    {item.manager_notes && (
                      <p className="text-xs text-gray-400 italic">Note: {item.manager_notes}</p>
                    )}
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(item.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  {item.status === "pending" && (
                    <div className="flex gap-2 shrink-0">
                      {actionId === item.id ? (
                        <div className="flex flex-col gap-2 w-48">
                          <input
                            type="text"
                            placeholder="Notes (optional)"
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            className="text-xs border border-gray-200 rounded px-2 py-1 w-full"
                          />
                          <div className="flex gap-1">
                            <button
                              onClick={() => handleAction(item.id, "approved")}
                              className="flex-1 bg-green-600 text-white text-xs rounded px-2 py-1"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => handleAction(item.id, "rejected")}
                              className="flex-1 bg-red-600 text-white text-xs rounded px-2 py-1"
                            >
                              Reject
                            </button>
                            <button
                              onClick={() => setActionId(null)}
                              className="text-gray-400 text-xs px-1"
                            >
                              ✕
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={() => setActionId(item.id)}
                          className="text-xs bg-[#68ccd1] text-white rounded-lg px-3 py-1.5 hover:bg-[#3aa3a8]"
                        >
                          Review
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
