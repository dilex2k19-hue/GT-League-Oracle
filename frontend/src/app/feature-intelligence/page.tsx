"use client";
import { useEffect, useState } from "react";
import { BrainCircuit } from "lucide-react";
import DataTable, { ColumnDef } from "@/components/DataTable";

interface FeatureData {
  feature: string;
  category: string;
  importance: number;
  correlation: number;
}

export default function FeatureIntelligencePage() {
  const [features, setFeatures] = useState<FeatureData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/feature-intelligence")
      .then(res => res.json())
      .then(data => {
        setFeatures(data.features || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching feature data:", err);
        setLoading(false);
      });
  }, []);

  const featureCols: ColumnDef<FeatureData>[] = [
    {
      header: "Data Feature",
      align: "left",
      render: (row) => (
        <div className="flex flex-col">
          <span className="font-bold text-slate-200 text-sm">{row.feature}</span>
        </div>
      )
    },
    {
      header: "Category",
      align: "center",
      render: (row) => {
        let badgeColor = "bg-slate-800 text-slate-300 border-slate-700";
        if (row.category === "Historical") badgeColor = "bg-indigo-500/20 text-indigo-400 border-indigo-500/30";
        if (row.category === "Form") badgeColor = "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
        if (row.category === "Matchup") badgeColor = "bg-purple-500/20 text-purple-400 border-purple-500/30";
        if (row.category === "Venue") badgeColor = "bg-blue-500/20 text-blue-400 border-blue-500/30";
        if (row.category === "Momentum") badgeColor = "bg-amber-500/20 text-amber-400 border-amber-500/30";
        
        return <span className={`px-2 py-1 rounded text-[9px] font-bold tracking-widest uppercase border ${badgeColor}`}>{row.category}</span>;
      }
    },
    {
      header: "Algorithm Importance",
      align: "center",
      render: (row) => (
        <div className="flex flex-col items-center gap-1 w-full max-w-[150px] mx-auto">
          <div className="flex justify-between w-full text-[10px] font-mono font-bold text-slate-300">
            <span>Weight</span>
            <span className="text-emerald-400">{row.importance.toFixed(1)}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
            <div className="h-full bg-emerald-500" style={{ width: `${row.importance}%` }}></div>
          </div>
        </div>
      )
    },
    {
      header: "Pearson Correlation (R)",
      align: "right",
      render: (row) => {
        const isPositive = row.correlation > 0;
        const colorClass = isPositive ? "text-blue-400" : "text-red-400";
        const barColor = isPositive ? "bg-blue-500" : "bg-red-500";
        const absWidth = Math.abs(row.correlation) * 100;

        return (
          <div className="flex flex-col items-end gap-1 w-full max-w-[150px] ml-auto">
            <div className={`text-[10px] font-mono font-bold ${colorClass}`}>
              {row.correlation > 0 ? '+' : ''}{row.correlation.toFixed(2)}
            </div>
            <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800 flex">
              {/* Center aligned progress bar logic for positive/negative correlation */}
              <div className="w-1/2 flex justify-end">
                {!isPositive && <div className={`h-full ${barColor}`} style={{ width: `${absWidth}%` }}></div>}
              </div>
              <div className="w-px h-full bg-slate-600"></div>
              <div className="w-1/2 flex justify-start">
                {isPositive && <div className={`h-full ${barColor}`} style={{ width: `${absWidth}%` }}></div>}
              </div>
            </div>
          </div>
        );
      }
    }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <BrainCircuit className="w-8 h-8 text-indigo-400" /> Feature Intelligence
          </h1>
          <p className="text-slate-400 text-xs mt-1">Deconstructing the neural pathways: analyzing which data points drive predictions.</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono text-sm animate-pulse">Extracting SHAP values from neural net...</div>
      ) : (
        <div className="space-y-8 pt-2">
          <DataTable 
            title="Global Feature Importance Weights" 
            subtitle="Top predictive indicators across all active models." 
            data={features} 
            columns={featureCols} 
            emptyMessage="No feature data extracted." 
          />
        </div>
      )}
    </div>
  );
}