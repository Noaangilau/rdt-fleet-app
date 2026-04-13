/**
 * Settings.jsx — Manager configuration page.
 * Currently houses the Morning Ops Briefing agent settings and send history.
 */

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import api from "../api";

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [history, setHistory] = useState([]);
  const [saving, setSaving] = useState(false);
  const [sending, setSending] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchAll();
  }, []);

  async function fetchAll() {
    try {
      const [s, h] = await Promise.all([
        api.get("/briefings/settings"),
        api.get("/briefings/history"),
      ]);
      setSettings(s.data);
      setHistory(h.data);
    } catch {
      showToast("Failed to load settings", "error");
    }
  }

  async function saveSettings() {
    setSaving(true);
    try {
      const res = await api.put("/briefings/settings", settings);
      setSettings(res.data);
      showToast("Settings saved", "success");
    } catch {
      showToast("Failed to save settings", "error");
    } finally {
      setSaving(false);
    }
  }

  async function sendNow() {
    setSending(true);
    try {
      await api.post("/briefings/send-now");
      showToast("Briefing sent!", "success");
      const res = await api.get("/briefings/history");
      setHistory(res.data);
    } catch {
      showToast("Failed to send briefing", "error");
    } finally {
      setSending(false);
    }
  }

  function showToast(msg, type) {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }

  if (!settings) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68ccd1]" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium transition-all ${
          toast.type === "success" ? "bg-green-500 text-white" : "bg-red-500 text-white"
        }`}>
          {toast.msg}
        </div>
      )}

      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Settings</h1>
        <p className="text-sm text-gray-500 mb-6">Configure automated features · RDT Inc.</p>

        {/* Morning Briefing Config */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex items-center gap-3 mb-5">
            <span className="text-2xl">☀️</span>
            <div>
              <h2 className="text-lg font-semibold text-gray-800">Morning Ops Briefing</h2>
              <p className="text-xs text-gray-500">Daily AI-generated fleet summary delivered to your inbox</p>
            </div>
          </div>

          <div className="space-y-5">
            {/* Enable toggle */}
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-700">Enable daily briefing</div>
                <div className="text-xs text-gray-400 mt-0.5">FleetBot generates a morning summary of fleet status</div>
              </div>
              <button
                onClick={() => setSettings((s) => ({ ...s, enabled: !s.enabled }))}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 items-center rounded-full transition-colors focus:outline-none ${
                  settings.enabled ? "bg-[#68ccd1]" : "bg-gray-200"
                }`}
              >
                <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                  settings.enabled ? "translate-x-6" : "translate-x-1"
                }`} />
              </button>
            </div>

            {/* Send time */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Send time</label>
              <input
                type="time"
                value={settings.send_time}
                onChange={(e) => setSettings((s) => ({ ...s, send_time: e.target.value }))}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#68ccd1]"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Recipient email</label>
              <input
                type="email"
                value={settings.email_address}
                onChange={(e) => setSettings((s) => ({ ...s, email_address: e.target.value }))}
                placeholder="manager@rdtinc.com"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#68ccd1]"
              />
            </div>

            <button
              onClick={saveSettings}
              disabled={saving}
              className="bg-[#68ccd1] hover:bg-[#3aa3a8] text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
              {saving ? "Saving…" : "Save Settings"}
            </button>
          </div>
        </div>

        {/* Briefing History */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-800">Recent Briefings</h2>
            <button
              onClick={sendNow}
              disabled={sending}
              className="text-sm text-[#3aa3a8] border border-[#68ccd1] hover:bg-[#68ccd1]/10 px-4 py-1.5 rounded-lg transition-colors disabled:opacity-50"
            >
              {sending ? "Sending…" : "Send Now"}
            </button>
          </div>

          {history.length === 0 ? (
            <div className="text-center py-10">
              <div className="text-4xl mb-2">📭</div>
              <p className="text-sm text-gray-500">No briefings sent yet.</p>
              <p className="text-xs text-gray-400 mt-1">
                Add your email above and click "Send Now" to test.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((entry) => (
                <BriefingEntry key={entry.id} entry={entry} />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

function BriefingEntry({ entry }) {
  const [expanded, setExpanded] = useState(false);
  const lines = entry.briefing_text.split("\n").filter(Boolean);
  const preview = lines.slice(0, 2).join(" ");
  const hasMore = lines.length > 2 || entry.briefing_text.length > preview.length + 5;

  return (
    <div className="border border-gray-100 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400">
          {new Date(entry.sent_at).toLocaleString()}
        </span>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
          entry.success ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
        }`}>
          {entry.success ? "Sent" : "Failed"}
        </span>
      </div>
      <p className="text-sm text-gray-700 leading-relaxed">
        {expanded ? entry.briefing_text : preview}
      </p>
      {hasMore && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-[#3aa3a8] mt-1.5 hover:underline"
        >
          {expanded ? "Show less" : "Show more"}
        </button>
      )}
      {!entry.success && entry.error_message && (
        <p className="text-xs text-red-500 mt-1.5">{entry.error_message}</p>
      )}
    </div>
  );
}
