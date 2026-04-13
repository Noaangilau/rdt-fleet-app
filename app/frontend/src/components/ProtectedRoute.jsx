/**
 * ProtectedRoute.jsx — Redirects unauthenticated users to /login.
 * Optionally restricts to a specific role.
 */

import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function ProtectedRoute({ children, role }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#68ccd1]" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  if (role && user.role !== role && !(role === "driver" && user.role === "manager")) {
    // Managers can access driver routes too; drivers cannot access manager routes
    return <Navigate to="/login" replace />;
  }

  return children;
}
