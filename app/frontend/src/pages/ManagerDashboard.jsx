/**
 * ManagerDashboard.jsx — Fleet overview: alert counts, truck grid, open incidents, mileage log.
 */

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import TruckCard from "../components/TruckCard";
import StatusBadge from "../components/StatusBadge";
import api from "../api";

export default function ManagerDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/dashboard").then((res) => {
      setData(res.data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68ccd1]" />
        </div>
      </Layout>
    );
  }

  const { total_trucks, trucks_needing_attention, total_red_items, total_yellow_items,
    total_green_items, truck_summaries, open_incidents, recent_mileage_logs } = data;

  const severityColor = { high: "text-red-600", medium: "text-yellow-600", low: "text-green-600" };
  const statusColor = { open: "bg-red-100 text-red-700", in_review: "bg-yellow-100 text-yellow-700", resolved: "bg-green-100 text-green-700" };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Dashboard</h1>
        <p className="text-sm text-gray-500 mb-6">Fleet status overview · RDT Inc.</p>

        {/* Alert banner */}
        {trucks_needing_attention > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 mb-6 flex items-center gap-3">
            <span className="text-red-500 text-xl">🚨</span>
            <div>
              <span className="font-semibold text-red-700">
                {trucks_needing_attention} truck{trucks_needing_attention !== 1 ? "s" : ""} need immediate attention
              </span>
              <span className="text-red-500 text-sm ml-2">— overdue maintenance items</span>
            </div>
          </div>
        )}

        {/* Stat cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Trucks" value={total_trucks} color="text-gray-900" />
          <StatCard label="Overdue Items" value={total_red_items} color="text-red-600" />
          <StatCard label="Due Soon" value={total_yellow_items} color="text-yellow-600" />
          <StatCard label="Good" value={total_green_items} color="text-green-600" />
        </div>

        {/* Truck grid */}
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Fleet Status</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 mb-8">
          {truck_summaries.map((truck) => (
            <TruckCard key={truck.id} truck={truck} />
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Open Incidents */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Open Incidents</h2>
            {open_incidents.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-200 px-4 py-6 text-center text-gray-400 text-sm">
                No open incidents
              </div>
            ) : (
              <div className="space-y-2">
                {open_incidents.map((inc) => (
                  <div key={inc.id} className="bg-white rounded-xl border border-gray-200 px-4 py-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className={`text-xs font-bold uppercase ${severityColor[inc.severity]}`}>
                          {inc.severity}
                        </span>
                        <span className="text-xs text-gray-400 ml-2">{inc.truck_number} · {inc.incident_date}</span>
                        <p className="text-sm text-gray-700 mt-1 line-clamp-2">{inc.description}</p>
                        <p className="text-xs text-gray-400 mt-0.5">{inc.driver_name}</p>
                      </div>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full whitespace-nowrap ${statusColor[inc.status]}`}>
                        {inc.status.replace("_", " ")}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Mileage */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Recent Mileage Updates</h2>
            {recent_mileage_logs.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-200 px-4 py-6 text-center text-gray-400 text-sm">
                No mileage logged yet
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
                {recent_mileage_logs.map((log) => (
                  <div key={log.id} className="flex items-center justify-between px-4 py-2.5">
                    <div>
                      <span className="text-sm font-medium text-gray-800">
                        {log.reported_mileage.toLocaleString()} mi
                      </span>
                      <span className="text-xs text-gray-400 ml-2">by {log.reported_by}</span>
                    </div>
                    <span className="text-xs text-gray-400">
                      {new Date(log.reported_at).toLocaleDateString()}
                    </span>
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

function StatCard({ label, value, color }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
      <div className={`text-3xl font-bold ${color}`}>{value}</div>
      <div className="text-xs text-gray-500 mt-1">{label}</div>
    </div>
  );
}
