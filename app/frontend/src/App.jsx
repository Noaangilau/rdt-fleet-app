/**
 * App.jsx — Root router. Redirects by role after login.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

// Pages
import Login from "./pages/Login";
import DriverMileage from "./pages/DriverMileage";
import DriverIncident from "./pages/DriverIncident";
import ManagerDashboard from "./pages/ManagerDashboard";
import Trucks from "./pages/Trucks";
import TruckDetail from "./pages/TruckDetail";
import Incidents from "./pages/Incidents";
import Drivers from "./pages/Drivers";
import AIAssistant from "./pages/AIAssistant";

function RoleRedirect() {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === "manager" ? "/dashboard" : "/mileage"} replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          {/* Driver routes */}
          <Route path="/mileage" element={
            <ProtectedRoute role="driver"><DriverMileage /></ProtectedRoute>
          } />
          <Route path="/incident" element={
            <ProtectedRoute role="driver"><DriverIncident /></ProtectedRoute>
          } />

          {/* Manager routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute role="manager"><ManagerDashboard /></ProtectedRoute>
          } />
          <Route path="/trucks" element={
            <ProtectedRoute role="manager"><Trucks /></ProtectedRoute>
          } />
          <Route path="/trucks/:id" element={
            <ProtectedRoute role="manager"><TruckDetail /></ProtectedRoute>
          } />
          <Route path="/incidents" element={
            <ProtectedRoute role="manager"><Incidents /></ProtectedRoute>
          } />
          <Route path="/drivers" element={
            <ProtectedRoute role="manager"><Drivers /></ProtectedRoute>
          } />
          <Route path="/ai" element={
            <ProtectedRoute role="manager"><AIAssistant /></ProtectedRoute>
          } />

          {/* Default redirect */}
          <Route path="*" element={<RoleRedirect />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
