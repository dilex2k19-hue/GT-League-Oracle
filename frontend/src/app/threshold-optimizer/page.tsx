"use client";
import { useEffect, useState } from "react";
// Import our new Master Component
import DataTable, { ColumnDef } from "@/components/DataTable";
import { Scale } from "lucide-react";

interface ThresholdData {
  threshold: string;
  total_decided: number;
  wins: number;
  losses: number;
}

export default function ThresholdOptimizerPage() {
  const [globalData, setGlobalData] = useState<ThresholdData[]>([]);
  const [overData, setOverData] = useState<ThresholdData[]>([]);
  const [homeData, setHomeData] = useState<ThresholdData[]>([]);
  const [awayData, setAwayData] = useState<ThresholdData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("${process.env.NEXT_PUBLIC_API_URL}/api/threshold-optimizer").then(res => res.json()),
      fetch("${process.env.NEXT_PUBLIC_API_URL}/api/threshold-optimizer/Over%202.5").then(res => res.json()),
      fetch("${process.env.NEXT_PUBLIC_API_URL}/api/threshold-optimizer/Home%20Win").then(res => res.json()),
      fetch("${process.env.NEXT_PUBLIC_API_URL}/api/threshold-optimizer/Away%20Win").then(res => res.json())
    ])
    .then(([gData, oData, hData, aData]) => {
      setGlobalData(gData.thresholds || []);
      setOverData(oData.thresholds || []);
      setHomeData(hData.thresholds || []);
      setAwayData(aData.thresholds || []);
      setLoading(false);
    })
    .catch(err => {
      console.error("Error fetching thresholds:", err);
      setLoading(false);
    });
  }, []);

  // Configuration block for how the data should be injected into our Master Table
  const ThresholdTable = ({ title, data, themeColor }: { title: string, data: ThresholdData[], themeColor: string }) => {
    const baseVolume = data.length > 0 ? data[0].total_decided : 0;

    const columns: ColumnDef<ThresholdData>[] = [
      {
        header: "Min Confidence",
        align: "left",
        render: (row) => (
          <div className="font-bold text-slate-200">
            {row.threshold}
            {row.threshold === '80%+' && <span className="ml-2 text-[8px] uppercase tracking-wider text-amber-400 font-bold bg-amber-400/10 px-1 py-0.5 rounded">Std</span>}
          </div>
        )
      },
      {
        header: "Matches",
        align: "center",
        render: (row) => (
          <div className="flex flex-col items-center leading-tight">
            <span className="font-semibold text-slate-300 text-sm">{row.total_decided}</span>
            <span className="text-[8px] text-slate-500 uppercase">{row.wins}W - {row.losses}L</span>
          </div>
        )
      },
      {
        header: "Win Rate",
        align: "center",
        render: (row) => {
          const winRate = row.total_decided > 0 ? ((row.wins / row.total_decided) * 100).toFixed(1) : "0.0";
          return <span className={`text-base font-bold ${themeColor}`}>{winRate}%</span>;
        }
      },
      {
        header: "Volume Retained",
        align: "right",
        render: (row) => {
          const volumeRetained = baseVolume > 0 ? ((row.total_decided / baseVolume) * 100).toFixed(1) : "0.0";
          return (
            <div className="flex items-center justify-end gap-2">
              <div className="w-16 h-1 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                 <div className="h-full bg-slate-500" style={{ width: `${volumeRetained}%` }}></div>
              </div>
              <span className="text-[10px] font-semibold text-slate-400 w-8">{volumeRetained}%</span>
            </div>
          );
        }
      }
    ];

    // Calling the Master Component!
    return (
      <DataTable 
        title={title} 
        subtitle="Accuracy vs Volume" 
        data={data} 
        columns={columns} 
        emptyMessage="No threshold data calculated." 
      />
    );
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
           <Scale className="w-8 h-8 text-amber-400" /> Threshold Optimizer
          </h1>
          <p className="text-slate-400 text-xs mt-1">Discovering optimal cutoffs to maximize win rate without starving volume.</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono text-sm animate-pulse">Calculating cumulative algorithm thresholds...</div>
      ) : (
        <div className="space-y-6 pt-2 w-full">
          <div className="w-full">
             <ThresholdTable title="Global System Cutoffs" data={globalData} themeColor="text-white" />
          </div>

          <div className="border-t border-slate-800 pt-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4">Sub-Model Cutoffs</h2>
            <div className="flex flex-col gap-4">
              <ThresholdTable title="⚽ Over 2.5 Goals" data={overData} themeColor="text-emerald-400" />
              <ThresholdTable title="🏠 Home Win Edge" data={homeData} themeColor="text-blue-400" />
              <ThresholdTable title="🚀 Away Win Exploits" data={awayData} themeColor="text-purple-400" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}