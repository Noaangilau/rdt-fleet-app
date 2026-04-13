/**
 * TruckCard.jsx — Compact truck summary card for the dashboard grid.
 */

import { useNavigate } from "react-router-dom";
import StatusBadge from "./StatusBadge";

const statusBorder = {
  red: "border-l-4 border-l-red-500",
  yellow: "border-l-4 border-l-yellow-400",
  green: "border-l-4 border-l-green-500",
};

export default function TruckCard({ truck }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/trucks/${truck.id}`)}
      className={`bg-white rounded-lg p-4 cursor-pointer shadow-sm hover:shadow-md transition-shadow ${statusBorder[truck.overall_status]}`}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="text-lg font-bold text-gray-900">{truck.truck_number}</span>
        <StatusBadge status={truck.overall_status} />
      </div>
      <div className="text-sm text-gray-600">
        {truck.year} {truck.make} {truck.model}
      </div>
      {truck.truck_type && (
        <div className="text-xs text-gray-400 mt-0.5">{truck.truck_type}</div>
      )}
      <div className="text-xs text-gray-500 mt-2">
        {truck.current_mileage.toLocaleString()} mi
      </div>
      <div className="flex gap-2 mt-2 text-xs">
        {truck.red_count > 0 && (
          <span className="text-red-600 font-medium">{truck.red_count} overdue</span>
        )}
        {truck.yellow_count > 0 && (
          <span className="text-yellow-600 font-medium">{truck.yellow_count} due soon</span>
        )}
        {truck.red_count === 0 && truck.yellow_count === 0 && (
          <span className="text-green-600 font-medium">All good</span>
        )}
      </div>
    </div>
  );
}
