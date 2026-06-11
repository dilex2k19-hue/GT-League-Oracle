"use client";
import { useEffect, useState } from "react";
import DataTable, { ColumnDef } from "@/components/DataTable";
import { Target } from "lucide-react";

interface CalibrationBucket {
  bucket: string;
  total_decided: number;
  wins: number;
  losses: number;
}

export default function ConfidenceAnalysisPage() {
  const [globalCal, setGlobalCal] = useState<CalibrationBucket[]>([]);
  const [overCal, setOverCal] = useState<CalibrationBucket[]>([]);
  const [homeCal, setHomeCal] = useState<CalibrationBucket[]>([]);
  const [awayCal, setAwayCal] = useState<CalibrationBucket[]>([]);
  const [loading, setLoading] = useState(true);

  const expectedRates: Record<string, number> = {
    "90-100%": 95, "80-89.9%": 85, "70-79.9%": 75, "60-69.9%": 65, "50-59.9%": 55, "< 50%": 45,
  };

  useEffect(() => {
    Promise.all([
      fetch("http://localhost:8000/api/calibration").then(res => res.json()),
      fetch("http://localhost:8000/api/calibration/Over%202.5").then(res => res.json()),
      fetch("http://localhost:8000/api/calibration/Home%20Win").then(res => res.json()),
      fetch("http://localhost:8000/api/calibration/Away%20Win").then(res => res.json())
    ])
    .then(([gData, oData, hData, aData]) => {
      setGlobalCal(gData.calibration || []);
      setOverCal(oData.calibration || []);
      setHomeCal(hData.calibration || []);
      setAwayCal(aData.calibration || []);
      setLoading(false);
    })
    .catch(err => {
      console.error("Error fetching calibration arrays:", err);
      setLoading(false);
    });
  }, []);

  // Columns for the Master Component
  const globalColumns: ColumnDef<CalibrationBucket>[] = [
    {
      header: "Confidence Range",
      align: "left",
      render: (row) => <span className="font-bold text-slate-200">{row.bucket.replace('%%', '%')}</span>
    },
    {
      header: "Total Matches",
      align: "center",
      render: (row) => <span className="font-semibold text-slate-300">{row.total_decided}</span>
    },
    {
      header: "Matches Won",
      align: "center",
      render: (row) => <span className="text-emerald-400">{row.wins}</span>
    },
    {
      header: "Matches Lost",
      align: "center",
      render: (row) => <span className="text-red-400">{row.losses}</span>
    },
    {
      header: "Actual Win Rate",
      align: "right",
      render: (row) => {
        const actualRate = row.total_decided > 0 ? ((row.wins / row.total_decided) * 100).toFixed(1) : "0.0";
        return <span className="text-white font-bold">{actualRate}%</span>;
      }
    }
  ];

  // Helper component for the sub-model progress bar cards (Since they aren't tables)
  const ModelCalibrationGrid = ({ title, data, themeColor }: { title: string, data: CalibrationBucket[], themeColor: string }) => (
    <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl p-5">
      <h3 className="text-sm font-semibold text-white mb-4 border-b border-slate-800 pb-2">{title}</h3>
      <div className="space-y-4">
        {data.length === 0 ? (
          <div className="text-center text-slate-500 font-mono text-xs py-4">No data available</div>
        ) : (
          data.map((row, idx) => {
            const actualRate = row.total_decided > 0 ? (row.wins / row.total_decided) * 100 : 0;
            const expectedRate = expectedRates[row.bucket.replace('%%', '%')] || 0;
            const difference = actualRate - expectedRate;
            let statusColor = "text-emerald-400";
            if (difference < -5) statusColor = "text-red-400";
            else if (difference < 0) statusColor = "text-amber-400";

            return (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-[9px] font-bold uppercase tracking-wider">
                  <span className="text-slate-300">{row.bucket.replace('%%', '%')}</span>
                  <span className={statusColor}>{difference > 0 ? '+' : ''}{difference.toFixed(1)}%</span>
                </div>
                <div className="relative w-full h-1.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                  <div className="absolute top-0 left-0 h-full bg-slate-600" style={{ width: `${expectedRate}%` }}></div>
                </div>
                <div className="relative w-full h-1.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                  <div className={`absolute top-0 left-0 h-full ${difference < -5 ? 'bg-red-500' : themeColor}`} style={{ width: `${actualRate}%` }}></div>
                </div>
                <div className="text-[9px] text-slate-500 font-mono text-right">
                  Act: {actualRate.toFixed(1)}% ({row.wins}W)
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
           <Target className="w-8 h-8 text-blue-400" /> Central Calibration
          </h1>
          <p className="text-slate-400 text-xs mt-1">Global and model-specific verification of confidence metrics.</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono text-sm animate-pulse">Computing data science metrics...</div>
      ) : (
        <div className="space-y-8">
          
          {/* Using our newly refactored Master Component here */}
          <DataTable 
            title="Global System Matrix"
            subtitle="Aggregated calibration across all running intelligence engines."
            data={globalCal}
            columns={globalColumns}
          />

          <div>
            <h2 className="text-lg font-bold text-slate-200 border-b border-slate-800 pb-2 mt-8 mb-4">Individual Intelligence Engines</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ModelCalibrationGrid title="⚽ Over 2.5 Goals" data={overCal} themeColor="bg-emerald-500" />
              <ModelCalibrationGrid title="🏠 Home Win Edge" data={homeCal} themeColor="bg-blue-500" />
              <ModelCalibrationGrid title="🚀 Away Win Exploits" data={awayCal} themeColor="bg-purple-500" />
            </div>
          </div>

        </div>
      )}
    </div>
  );
}