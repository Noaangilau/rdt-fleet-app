/**
 * HR.jsx — Driver HR management: documents, attendance, notes.
 */

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import api from "../api";

export default function HR() {
  const [drivers, setDrivers] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [profile, setProfile] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("documents");
  const [showDocForm, setShowDocForm] = useState(false);
  const [showNoteForm, setShowNoteForm] = useState(false);
  const [docForm, setDocForm] = useState({ document_type: "cdl_license", expiry_date: "", document_number: "", notes: "" });
  const [noteText, setNoteText] = useState("");

  useEffect(() => {
    api.get("/users").then((res) => {
      const d = res.data.filter((u) => u.role === "driver");
      setDrivers(d);
      if (d.length > 0) selectDriver(d[0].id);
      else setLoading(false);
    });
  }, []);

  function selectDriver(id) {
    setSelectedDriver(id);
    setLoading(true);
    Promise.all([
      api.get(`/hr/drivers/${id}/profile`),
      api.get(`/hr/documents?user_id=${id}`),
    ]).then(([pRes, dRes]) => {
      setProfile(pRes.data);
      setDocuments(dRes.data);
      setLoading(false);
    });
  }

  async function addDocument(e) {
    e.preventDefault();
    await api.post("/hr/documents", {
      user_id: selectedDriver,
      ...docForm,
      expiry_date: docForm.expiry_date || null,
    });
    setShowDocForm(false);
    setDocForm({ document_type: "cdl_license", expiry_date: "", document_number: "", notes: "" });
    selectDriver(selectedDriver);
  }

  async function deleteDocument(id) {
    if (!window.confirm("Delete this document?")) return;
    await api.delete(`/hr/documents/${id}`);
    selectDriver(selectedDriver);
  }

  async function addNote(e) {
    e.preventDefault();
    await api.post("/hr/notes", { user_id: selectedDriver, note_text: noteText });
    setNoteText("");
    setShowNoteForm(false);
    selectDriver(selectedDriver);
  }

  const docTypeLabel = { cdl_license: "CDL License", medical_card: "Medical Card", other: "Other" };

  function daysUntil(dateStr) {
    if (!dateStr) return null;
    return Math.ceil((new Date(dateStr) - new Date()) / 86400000);
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">HR Management</h1>
        <p className="text-sm text-gray-500 mb-6">Driver documents, attendance, and notes</p>

        <div className="grid md:grid-cols-4 gap-6">
          {/* Driver list */}
          <div className="md:col-span-1">
            <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-2">Drivers</h2>
            <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
              {drivers.map((d) => (
                <button
                  key={d.id}
                  onClick={() => selectDriver(d.id)}
                  className={`w-full text-left px-3 py-2.5 transition-colors ${
                    selectedDriver === d.id ? "bg-[#68ccd1]/10 text-[#3aa3a8]" : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <div className="text-sm font-medium">{d.full_name || d.username}</div>
                  <div className="text-xs text-gray-400">{d.username}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Profile panel */}
          <div className="md:col-span-3">
            {loading ? (
              <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68ccd1]" /></div>
            ) : !profile ? (
              <div className="text-gray-400 text-sm text-center py-10">Select a driver</div>
            ) : (
              <>
                {/* Profile header */}
                <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-[#68ccd1] flex items-center justify-center text-white font-bold text-lg">
                    {(profile.full_name || profile.username)[0].toUpperCase()}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{profile.full_name || profile.username}</div>
                    <div className="text-xs text-gray-500">{profile.username} · Driver since {new Date(profile.created_at).getFullYear()}</div>
                  </div>
                  <div className="ml-auto">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      profile.availability_status === "on_duty" ? "bg-green-100 text-green-700"
                      : profile.availability_status === "available" ? "bg-blue-100 text-blue-700"
                      : "bg-gray-100 text-gray-500"
                    }`}>
                      {profile.availability_status?.replace("_", " ") || "off duty"}
                    </span>
                  </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-2 mb-4">
                  {["documents", "notes"].map((t) => (
                    <button key={t} onClick={() => setTab(t)}
                      className={`text-sm px-4 py-1.5 rounded-full font-medium capitalize transition-colors ${
                        tab === t ? "bg-[#68ccd1] text-white" : "bg-white border border-gray-200 text-gray-600"
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>

                {/* Documents */}
                {tab === "documents" && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-semibold text-gray-700">Documents</h3>
                      <button onClick={() => setShowDocForm(!showDocForm)}
                        className="text-xs bg-[#68ccd1] text-white px-3 py-1 rounded-lg">
                        + Add
                      </button>
                    </div>

                    {showDocForm && (
                      <form onSubmit={addDocument} className="bg-gray-50 rounded-xl p-4 mb-3 space-y-2">
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="text-xs text-gray-500 mb-1 block">Type</label>
                            <select value={docForm.document_type}
                              onChange={(e) => setDocForm({ ...docForm, document_type: e.target.value })}
                              className="w-full text-sm border border-gray-200 rounded px-2 py-1.5">
                              <option value="cdl_license">CDL License</option>
                              <option value="medical_card">Medical Card</option>
                              <option value="other">Other</option>
                            </select>
                          </div>
                          <div>
                            <label className="text-xs text-gray-500 mb-1 block">Expiry Date</label>
                            <input type="date" value={docForm.expiry_date}
                              onChange={(e) => setDocForm({ ...docForm, expiry_date: e.target.value })}
                              className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                          </div>
                          <div className="col-span-2">
                            <label className="text-xs text-gray-500 mb-1 block">Doc Number</label>
                            <input value={docForm.document_number}
                              onChange={(e) => setDocForm({ ...docForm, document_number: e.target.value })}
                              placeholder="Optional"
                              className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button type="submit" className="text-xs bg-[#68ccd1] text-white px-3 py-1.5 rounded">Save</button>
                          <button type="button" onClick={() => setShowDocForm(false)} className="text-xs text-gray-400">Cancel</button>
                        </div>
                      </form>
                    )}

                    {documents.length === 0 ? (
                      <div className="text-gray-400 text-sm text-center py-6 bg-white rounded-xl border border-gray-200">
                        No documents on file
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {documents.map((doc) => {
                          const days = daysUntil(doc.expiry_date);
                          const expColor = days === null ? "text-gray-400" : days < 0 ? "text-red-600" : days <= 30 ? "text-yellow-600" : "text-green-600";
                          return (
                            <div key={doc.id} className="bg-white rounded-xl border border-gray-200 px-4 py-3 flex items-center justify-between">
                              <div>
                                <div className="text-sm font-medium text-gray-900">{docTypeLabel[doc.document_type] || doc.document_type}</div>
                                {doc.document_number && <div className="text-xs text-gray-400"># {doc.document_number}</div>}
                                {doc.expiry_date && (
                                  <div className={`text-xs font-medium ${expColor}`}>
                                    {days === null ? "" : days < 0 ? "Expired " + Math.abs(days) + " days ago"
                                      : days === 0 ? "Expires today"
                                      : "Expires in " + days + " days"} · {doc.expiry_date}
                                  </div>
                                )}
                              </div>
                              <button onClick={() => deleteDocument(doc.id)}
                                className="text-xs text-red-400 hover:text-red-600">Delete</button>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}

                {/* Notes */}
                {tab === "notes" && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-semibold text-gray-700">Manager Notes</h3>
                      <button onClick={() => setShowNoteForm(!showNoteForm)}
                        className="text-xs bg-[#68ccd1] text-white px-3 py-1 rounded-lg">
                        + Add Note
                      </button>
                    </div>

                    {showNoteForm && (
                      <form onSubmit={addNote} className="bg-gray-50 rounded-xl p-4 mb-3">
                        <textarea
                          required
                          value={noteText}
                          onChange={(e) => setNoteText(e.target.value)}
                          placeholder="Write a note about this driver..."
                          rows={3}
                          className="w-full text-sm border border-gray-200 rounded px-3 py-2 resize-none"
                        />
                        <div className="flex gap-2 mt-2">
                          <button type="submit" className="text-xs bg-[#68ccd1] text-white px-3 py-1.5 rounded">Save</button>
                          <button type="button" onClick={() => setShowNoteForm(false)} className="text-xs text-gray-400">Cancel</button>
                        </div>
                      </form>
                    )}

                    {profile.notes.length === 0 ? (
                      <div className="text-gray-400 text-sm text-center py-6 bg-white rounded-xl border border-gray-200">
                        No notes yet
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {profile.notes.map((n) => (
                          <div key={n.id} className="bg-white rounded-xl border border-gray-200 px-4 py-3">
                            <p className="text-sm text-gray-700">{n.note_text}</p>
                            <p className="text-xs text-gray-400 mt-1">
                              {new Date(n.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
