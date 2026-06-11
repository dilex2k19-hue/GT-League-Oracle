"use client";
import { useEffect, useState } from "react";
import DataTable, { ColumnDef } from "@/components/DataTable";

interface Prediction {
  id: number;
  home_player: string;
  away_player: string;
  kickoff_utc: string;
  prediction: string;
  confidence: number;
  status: string;
}

interface ModelStat {
  model_name: string;
  total_picks: number;
  wins: number;
  losses: number;
  pending: number;
}

export default function GlobalOverview() {
  const [stats, setStats] = useState({ status: "Connecting...", total_predictions: 0 });
  const [globalPredictions, setGlobalPredictions] = useState<Prediction[]>([]);
  const [modelAnalytics, setModelAnalytics] = useState<ModelStat[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("http://localhost:8000/api/system-stats").then(res => res.json()),
      fetch("http://localhost:8000/api/recent-predictions").then(res => res.json()),
      fetch("http://localhost:8000/api/model-analytics").then(res => res.json())
    ])
    .then(([systemData, predData, analyticsData]) => {
      setStats(systemData || { status: "Error", total_predictions: 0 });
      setGlobalPredictions(predData.predictions || []);
      setModelAnalytics(analyticsData.models || []);
      setLoading(false);
    })
    .catch(err => {
      console.error("Global Dashboard Sync Error:", err);
      setStats({ status: "Offline", total_predictions: 0 });
      setLoading(false);
    });
  }, []);

  const formatTime = (utcString: string) => {
    try {
      const dateObj = new Date(utcString);
      return dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return "00:00";
    }
  };

  // --- 1. Network Stream Columns ---
  const networkCols: ColumnDef<Prediction>[] = [
    {
      header: "Time",
      align: "left",
      render: (row) => <span className="font-mono text-slate-300">{formatTime(row.kickoff_utc)}</span>
    },
    {
      header: "Match",
      align: "left",
      render: (row) => <span className="font-medium text-slate-200">{row.home_player} <span className="text-slate-500 text-[10px] mx-1">vs</span> {row.away_player}</span>
    },
    {
      header: "Model",
      align: "center",
      render: (row) => {
        let badgeColor = "bg-slate-800 text-slate-300";
        if (row.prediction === "Over 2.5") badgeColor = "text-emerald-400";
        if (row.prediction === "Home Win") badgeColor = "text-blue-400";
        if (row.prediction === "Away Win") badgeColor = "text-purple-400";
        return <span className={`font-bold text-[10px] uppercase tracking-wider ${badgeColor}`}>{row.prediction}</span>;
      }
    },
    {
      header: "Conf",
      align: "center",
      render: (row) => <span className="font-mono font-bold text-slate-300">{Number(row.confidence || 0).toFixed(1)}%</span>
    },
    {
      header: "Status",
      align: "right",
      render: (row) => {
        if (row.status === 'Won') return <span className="text-emerald-400 text-[9px] font-bold bg-emerald-400/10 px-1.5 py-0.5 rounded border border-emerald-400/20 uppercase">Won</span>;
        if (row.status === 'Lost') return <span className="text-red-400 text-[9px] font-bold bg-red-400/10 px-1.5 py-0.5 rounded border border-red-400/20 uppercase">Lost</span>;
        return <span className="text-amber-400 text-[9px] font-bold bg-amber-400/10 px-1.5 py-0.5 rounded border border-amber-400/20 uppercase">Pend</span>;
      }
    }
  ];

  // --- 2. All-Time Performance Matrix Columns ---
  const analyticsCols: ColumnDef<ModelStat>[] = [
    {
      header: "Model Engine",
      align: "left",
      render: (row) => {
        let color = "text-slate-200";
        if (row.model_name === "Over 2.5") color = "text-emerald-400";
        if (row.model_name === "Home Win") color = "text-blue-400";
        if (row.model_name === "Away Win") color = "text-purple-400";
        return <span className={`font-bold ${color}`}>{row.model_name}</span>;
      }
    },
    {
      header: "Signals",
      align: "center",
      render: (row) => <span className="font-mono text-slate-300">{row.total_picks}</span>
    },
    {
      header: "W-L-P",
      align: "center",
      render: (row) => (
        <div className="text-[10px] uppercase font-mono tracking-wide">
          <span className="text-emerald-400">{row.wins}W</span><span className="text-slate-600 mx-1">-</span>
          <span className="text-red-400">{row.losses}L</span><span className="text-slate-600 mx-1">-</span>
          <span className="text-amber-400">{row.pending}P</span>
        </div>
      )
    },
    {
      header: "All-Time Win Rate",
      align: "right",
      render: (row) => {
        const totalDecided = Number(row.wins) + Number(row.losses);
        const winRate = totalDecided > 0 ? ((Number(row.wins) / totalDecided) * 100).toFixed(1) : "0.0";
        return (
          <div className="flex items-center justify-end gap-2">
            <div className="w-12 h-1 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
               <div className="h-full bg-slate-500" style={{ width: `${winRate}%` }}></div>
            </div>
            <span className="font-mono text-sm font-bold text-white w-10">{winRate}%</span>
          </div>
        );
      }
    }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      
      {/* Global Header Module */}
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Global Command Center</h1>
          <p className="text-slate-400 text-xs mt-1">All-time aggregate metrics and live network status.</p>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-right">
            <span className="text-[9px] uppercase text-slate-500 font-bold block tracking-wider">Total Ingested Patterns</span>
            <span className="text-lg font-mono text-emerald-300 font-semibold">
              {(stats?.total_predictions ?? 0).toLocaleString()} Rows
            </span>
          </div>
          <div className="px-3 py-1.5 bg-slate-900 rounded border border-slate-800 flex items-center shadow-inner">
            <span className={`inline-block w-2 h-2 rounded-full mr-2 ${stats.status === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></span>
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              {stats.status === 'online' ? 'System Live' : 'Offline'}
            </span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono text-sm animate-pulse">Aggregating global cloud metrics...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-2 items-start">
          
          {/* Left: Global Aggregated Live Feed */}
          <DataTable 
            title="Network Stream" 
            subtitle="Latest predictions across all active sub-models." 
            data={globalPredictions} 
            columns={networkCols} 
            emptyMessage="Awaiting network traffic..." 
          />

          {/* Right: All-Time Model Matrix */}
          <DataTable 
            title="All-Time Performance Matrix" 
            subtitle="Macro comparison of intelligence engines." 
            data={modelAnalytics} 
            columns={analyticsCols} 
            emptyMessage="Awaiting analytic compilation..." 
          />

        </div>
      )}
    </div>
  );
}