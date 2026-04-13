/**
 * Financials.jsx — Fleet financials: repair costs, fuel logs, and cost summaries.
 */

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import api from "../api";

export default function Financials() {
  const [summaries, setSummaries] = useState([]);
  const [trucks, setTrucks] = useState([]);
  const [selectedTruck, setSelectedTruck] = useState(null);
  const [costs, setCosts] = useState([]);
  const [fuel, setFuel] = useState([]);
  const [repairs, setRepairs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("costs");
  const [showCostForm, setShowCostForm] = useState(false);
  const [showFuelForm, setShowFuelForm] = useState(false);
  const [showRepairForm, setShowRepairForm] = useState(false);
  const [costForm, setCostForm] = useState({ date: "", description: "", cost: "", vendor: "", notes: "" });
  const [fuelForm, setFuelForm] = useState({ date: "", gallons: "", cost_per_gallon: "", odometer_at_fillup: "", notes: "" });
  const [repairForm, setRepairForm] = useState({ scheduled_date: "", mechanic_name: "", mechanic_phone: "", location: "", notes: "" });

  function loadSummaries() {
    api.get("/fleet/cost-summary").then((res) => setSummaries(res.data));
  }

  useEffect(() => {
    Promise.all([
      api.get("/fleet/cost-summary"),
      api.get("/trucks"),
    ]).then(([sRes, tRes]) => {
      setSummaries(sRes.data);
      setTrucks(tRes.data);
      if (tRes.data.length > 0) selectTruck(tRes.data[0].id);
      else setLoading(false);
    });
  }, []);

  function selectTruck(id) {
    setSelectedTruck(id);
    setLoading(true);
    Promise.all([
      api.get(`/fleet/trucks/${id}/costs`),
      api.get(`/fleet/trucks/${id}/fuel`),
      api.get(`/fleet/trucks/${id}/repairs`),
    ]).then(([cRes, fRes, rRes]) => {
      setCosts(cRes.data);
      setFuel(fRes.data);
      setRepairs(rRes.data);
      setLoading(false);
    });
  }

  async function addCost(e) {
    e.preventDefault();
    await api.post(`/fleet/trucks/${selectedTruck}/costs`, {
      ...costForm,
      cost: parseFloat(costForm.cost),
    });
    setShowCostForm(false);
    setCostForm({ date: "", description: "", cost: "", vendor: "", notes: "" });
    selectTruck(selectedTruck);
    loadSummaries();
  }

  async function addFuel(e) {
    e.preventDefault();
    await api.post(`/fleet/trucks/${selectedTruck}/fuel`, {
      date: fuelForm.date,
      gallons: parseFloat(fuelForm.gallons),
      cost_per_gallon: parseFloat(fuelForm.cost_per_gallon),
      odometer_at_fillup: fuelForm.odometer_at_fillup ? parseInt(fuelForm.odometer_at_fillup) : null,
      notes: fuelForm.notes || null,
    });
    setShowFuelForm(false);
    setFuelForm({ date: "", gallons: "", cost_per_gallon: "", odometer_at_fillup: "", notes: "" });
    selectTruck(selectedTruck);
    loadSummaries();
  }

  async function addRepair(e) {
    e.preventDefault();
    await api.post(`/fleet/trucks/${selectedTruck}/repairs`, repairForm);
    setShowRepairForm(false);
    setRepairForm({ scheduled_date: "", mechanic_name: "", mechanic_phone: "", location: "", notes: "" });
    selectTruck(selectedTruck);
  }

  const selectedSummary = summaries.find((s) => s.truck_id === selectedTruck);
  const selectedTruckInfo = trucks.find((t) => t.id === selectedTruck);

  const statusColor = {
    pending_approval: "bg-yellow-100 text-yellow-700",
    scheduled: "bg-blue-100 text-blue-700",
    completed: "bg-green-100 text-green-700",
    cancelled: "bg-gray-100 text-gray-500",
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Financials</h1>
        <p className="text-sm text-gray-500 mb-6">Repair costs, fuel, and fleet-wide spending</p>

        {/* Fleet summary cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 mb-8">
          {summaries.map((s) => (
            <button
              key={s.truck_id}
              onClick={() => selectTruck(s.truck_id)}
              className={`p-3 rounded-xl border text-left transition-colors ${
                selectedTruck === s.truck_id
                  ? "border-[#68ccd1] bg-[#68ccd1]/5"
                  : "border-gray-200 bg-white hover:bg-gray-50"
              }`}
            >
              <div className="text-sm font-bold text-gray-900">{s.truck_number}</div>
              <div className="text-xs text-gray-500 mt-1">Total: <span className="font-medium text-gray-800">${s.total_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>
            </button>
          ))}
        </div>

        {!selectedTruck ? null : (
          <div>
            {/* Selected truck header */}
            {selectedSummary && (
              <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6 grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">${selectedSummary.total_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                  <div className="text-xs text-gray-500 mt-0.5">Total Cost</div>
                </div>
                <div className="text-center border-x border-gray-100">
                  <div className="text-2xl font-bold text-red-600">${selectedSummary.total_repair_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                  <div className="text-xs text-gray-500 mt-0.5">Repairs ({selectedSummary.repair_entries})</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">${selectedSummary.total_fuel_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                  <div className="text-xs text-gray-500 mt-0.5">Fuel ({selectedSummary.fuel_entries} fill-ups)</div>
                </div>
              </div>
            )}

            {/* Tabs */}
            <div className="flex gap-2 mb-4">
              {["costs", "fuel", "repairs"].map((t) => (
                <button key={t} onClick={() => setTab(t)}
                  className={`text-sm px-4 py-1.5 rounded-full font-medium capitalize transition-colors ${
                    tab === t ? "bg-[#68ccd1] text-white" : "bg-white border border-gray-200 text-gray-600"
                  }`}>
                  {t === "costs" ? "Repair Costs" : t === "fuel" ? "Fuel Log" : "Appointments"}
                </button>
              ))}
            </div>

            {loading ? (
              <div className="flex justify-center py-10"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[#68ccd1]" /></div>
            ) : (
              <>
                {/* Repair Costs */}
                {tab === "costs" && (
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-sm font-semibold text-gray-700">Repair Cost Log</h3>
                      <button onClick={() => setShowCostForm(!showCostForm)}
                        className="text-xs bg-[#68ccd1] text-white px-3 py-1 rounded-lg">+ Add</button>
                    </div>
                    {showCostForm && (
                      <form onSubmit={addCost} className="bg-gray-50 rounded-xl p-4 mb-3 grid grid-cols-2 gap-3">
                        <div className="col-span-2">
                          <label className="text-xs text-gray-500 mb-1 block">Description *</label>
                          <input required value={costForm.description} onChange={(e) => setCostForm({ ...costForm, description: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" placeholder="e.g. Brake replacement" />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Date *</label>
                          <input required type="date" value={costForm.date} onChange={(e) => setCostForm({ ...costForm, date: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Cost ($) *</label>
                          <input required type="number" step="0.01" value={costForm.cost} onChange={(e) => setCostForm({ ...costForm, cost: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" placeholder="0.00" />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Vendor</label>
                          <input value={costForm.vendor} onChange={(e) => setCostForm({ ...costForm, vendor: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                        </div>
                        <div className="col-span-2 flex gap-2">
                          <button type="submit" className="text-xs bg-[#68ccd1] text-white px-3 py-1.5 rounded">Save</button>
                          <button type="button" onClick={() => setShowCostForm(false)} className="text-xs text-gray-400">Cancel</button>
                        </div>
                      </form>
                    )}
                    {costs.length === 0 ? (
                      <div className="text-gray-400 text-sm text-center py-6 bg-white rounded-xl border border-gray-200">No repair costs recorded</div>
                    ) : (
                      <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
                        {costs.map((c) => (
                          <div key={c.id} className="flex items-center justify-between px-4 py-3">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{c.description}</div>
                              <div className="text-xs text-gray-400">{c.date}{c.vendor && ` · ${c.vendor}`}</div>
                            </div>
                            <div className="text-sm font-bold text-red-600">${c.cost.toFixed(2)}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Fuel Log */}
                {tab === "fuel" && (
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-sm font-semibold text-gray-700">Fuel Log</h3>
                      <button onClick={() => setShowFuelForm(!showFuelForm)}
                        className="text-xs bg-[#68ccd1] text-white px-3 py-1 rounded-lg">+ Log Fill-Up</button>
                    </div>
                    {showFuelForm && (
                      <form onSubmit={addFuel} className="bg-gray-50 rounded-xl p-4 mb-3 grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Date *</label>
                          <input required type="date" value={fuelForm.date} onChange={(e) => setFuelForm({ ...fuelForm, date: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Gallons *</label>
                          <input required type="number" step="0.01" value={fuelForm.gallons} onChange={(e) => setFuelForm({ ...fuelForm, gallons: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" placeholder="0.0" />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">$/Gallon *</label>
                          <input required type="number" step="0.001" value={fuelForm.cost_per_gallon} onChange={(e) => setFuelForm({ ...fuelForm, cost_per_gallon: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" placeholder="3.999" />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Odometer</label>
                          <input type="number" value={fuelForm.odometer_at_fillup} onChange={(e) => setFuelForm({ ...fuelForm, odometer_at_fillup: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                        </div>
                        {fuelForm.gallons && fuelForm.cost_per_gallon && (
                          <div className="col-span-2 text-sm text-gray-600">
                            Total: <span className="font-bold text-blue-600">${(parseFloat(fuelForm.gallons || 0) * parseFloat(fuelForm.cost_per_gallon || 0)).toFixed(2)}</span>
                          </div>
                        )}
                        <div className="col-span-2 flex gap-2">
                          <button type="submit" className="text-xs bg-[#68ccd1] text-white px-3 py-1.5 rounded">Save</button>
                          <button type="button" onClick={() => setShowFuelForm(false)} className="text-xs text-gray-400">Cancel</button>
                        </div>
                      </form>
                    )}
                    {fuel.length === 0 ? (
                      <div className="text-gray-400 text-sm text-center py-6 bg-white rounded-xl border border-gray-200">No fuel logged</div>
                    ) : (
                      <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
                        {fuel.map((f) => (
                          <div key={f.id} className="flex items-center justify-between px-4 py-3">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{f.gallons.toFixed(1)} gal @ ${f.cost_per_gallon.toFixed(3)}/gal</div>
                              <div className="text-xs text-gray-400">{f.date}{f.odometer_at_fillup && ` · ${f.odometer_at_fillup.toLocaleString()} mi`}</div>
                            </div>
                            <div className="text-sm font-bold text-blue-600">${f.total_cost.toFixed(2)}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Repair Appointments */}
                {tab === "repairs" && (
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-sm font-semibold text-gray-700">Repair Appointments</h3>
                      <button onClick={() => setShowRepairForm(!showRepairForm)}
                        className="text-xs bg-[#68ccd1] text-white px-3 py-1 rounded-lg">+ Schedule</button>
                    </div>
                    {showRepairForm && (
                      <form onSubmit={addRepair} className="bg-gray-50 rounded-xl p-4 mb-3 grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Date *</label>
                          <input required type="date" value={repairForm.scheduled_date} onChange={(e) => setRepairForm({ ...repairForm, scheduled_date: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Mechanic</label>
                          <input value={repairForm.mechanic_name} onChange={(e) => setRepairForm({ ...repairForm, mechanic_name: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Phone</label>
                          <input value={repairForm.mechanic_phone} onChange={(e) => setRepairForm({ ...repairForm, mechanic_phone: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Location</label>
                          <input value={repairForm.location} onChange={(e) => setRepairForm({ ...repairForm, location: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                        </div>
                        <div className="col-span-2">
                          <label className="text-xs text-gray-500 mb-1 block">Notes</label>
                          <input value={repairForm.notes} onChange={(e) => setRepairForm({ ...repairForm, notes: e.target.value })}
                            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                        </div>
                        <div className="col-span-2 flex gap-2">
                          <button type="submit" className="text-xs bg-[#68ccd1] text-white px-3 py-1.5 rounded">Save</button>
                          <button type="button" onClick={() => setShowRepairForm(false)} className="text-xs text-gray-400">Cancel</button>
                        </div>
                      </form>
                    )}
                    {repairs.length === 0 ? (
                      <div className="text-gray-400 text-sm text-center py-6 bg-white rounded-xl border border-gray-200">No appointments scheduled</div>
                    ) : (
                      <div className="space-y-2">
                        {repairs.map((r) => (
                          <div key={r.id} className="bg-white rounded-xl border border-gray-200 px-4 py-3">
                            <div className="flex items-start justify-between">
                              <div>
                                <div className="text-sm font-medium text-gray-900">{r.scheduled_date}</div>
                                {r.mechanic_name && <div className="text-xs text-gray-500">{r.mechanic_name}{r.mechanic_phone && ` · ${r.mechanic_phone}`}</div>}
                                {r.location && <div className="text-xs text-gray-400">{r.location}</div>}
                                {r.notes && <div className="text-xs text-gray-500 mt-1">{r.notes}</div>}
                              </div>
                              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColor[r.status] || "bg-gray-100 text-gray-500"}`}>
                                {r.status?.replace(/_/g, " ")}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
