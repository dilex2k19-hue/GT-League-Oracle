"use client";
import { useEffect, useState } from "react";
import DataTable, { ColumnDef } from "@/components/DataTable";
import { Home } from "lucide-react";

interface Prediction {
  id: number;
  home_player: string;
  away_player: string;
  kickoff_utc: string;
  confidence: number;
  status: string;
  score?: string;
}

interface ModelStat {
  total_picks: number;
  wins: number;
  losses: number;
  pending: number;
}

export default function HomeWinPage() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [stats, setStats] = useState<ModelStat>({ total_picks: 0, wins: 0, losses: 0, pending: 0 });
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState<string>("");

  useEffect(() => {
    setLoading(true);
    const targetModel = encodeURIComponent("Home Win");
    const dateQuery = selectedDate ? `?date=${selectedDate}` : "";

    Promise.all([
      fetch(`http://localhost:8000/api/predictions/${targetModel}${dateQuery}`).then(res => res.json()),
      fetch(`http://localhost:8000/api/stats/${targetModel}${dateQuery}`).then(res => res.json())
    ])
    .then(([predData, statData]) => {
      setPredictions(predData.predictions || []);
      setStats(statData.stats || { total_picks: 0, wins: 0, losses: 0, pending: 0 });
      setLoading(false);
    })
    .catch(err => {
      console.error("Error fetching data:", err);
      setLoading(false);
    });
  }, [selectedDate]);

  const totalDecided = Number(stats.wins) + Number(stats.losses);
  const winRate = totalDecided > 0 ? ((Number(stats.wins) / totalDecided) * 100).toFixed(1) : "0.0";

  const formatTime = (utcString: string) => {
    try {
      const dateObj = new Date(utcString);
      return dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return "00:00";
    }
  };

  const columns: ColumnDef<Prediction>[] = [
    {
      header: "Kickoff",
      align: "left",
      render: (row) => (
        <div className="flex flex-col">
          <span className="font-bold text-slate-300">{formatTime(row.kickoff_utc)}</span>
        </div>
      )
    },
    {
      header: "Match Setup",
      align: "left",
      render: (row) => (
        <div className="flex flex-col justify-center">
          <div className="font-medium text-slate-200 truncate">
            {row.home_player} <span className="text-slate-500 text-[10px] mx-1">vs</span> {row.away_player}
          </div>
          {row.score && row.status !== 'Pending' && (
            <span className="text-[10px] text-slate-400 font-mono mt-0.5">
              FT: <span className="text-white font-bold bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">{row.score}</span>
            </span>
          )}
        </div>
      )
    },
    {
      header: "Confidence",
      align: "center",
      render: (row) => (
        <span className="font-mono font-semibold text-blue-400/80 bg-slate-950 px-2 py-1 border border-slate-800 rounded text-xs">
          {Number(row.confidence).toFixed(1)}%
        </span>
      )
    },
    {
      header: "Status",
      align: "right",
      render: (row) => {
        if (row.status === 'Won') return <span className="text-emerald-400 font-bold bg-emerald-400/10 px-2 py-1 rounded border border-emerald-400/20 text-[9px] uppercase tracking-wider">Won</span>;
        if (row.status === 'Lost') return <span className="text-red-400 font-bold bg-red-400/10 px-2 py-1 rounded border border-red-400/20 text-[9px] uppercase tracking-wider">Lost</span>;
        return <span className="text-amber-400 font-bold bg-amber-400/10 px-2 py-1 rounded border border-amber-400/20 text-[9px] uppercase tracking-wider">Pending</span>;
      }
    }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <header className="border-b border-slate-800 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-blue-400 flex items-center gap-3">
           <Home className="w-8 h-8" /> Home Win Edge Model
          </h1>
          <p className="text-slate-400 text-xs mt-1">Tracking the performance of home-advantage setups.</p>
        </div>
        
        <div className="flex flex-col items-end gap-2">
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Historical Date Filter</span>
            <div className="flex items-center gap-3">
                {selectedDate && (
                    <button onClick={() => setSelectedDate("")} className="text-xs text-slate-400 hover:text-white transition-colors">
                        Clear Filter
                    </button>
                )}
                <input 
                    type="date" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)}
                    className="bg-slate-900 border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-1.5 outline-none focus:border-blue-500 transition-colors [color-scheme:dark]"
                />
            </div>
        </div>
      </header>

      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono text-sm animate-pulse">Syncing chronological database...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
          
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-slate-900 p-5 rounded-xl border border-slate-800 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-blue-500"></div>
                <h2 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-4">
                  {selectedDate ? `Accuracy on ${selectedDate}` : "All-Time Accuracy"}
                </h2>
                <div className="flex items-end gap-2 mb-6">
                    <span className="text-4xl font-mono font-bold text-blue-400">{winRate}%</span>
                    <span className="text-xs text-slate-500 mb-1 font-medium">Win Rate</span>
                </div>
                <div className="space-y-2">
                    <div className="flex justify-between items-center text-xs border-b border-slate-800 pb-2">
                        <span className="text-slate-400">Signals Sent</span>
                        <span className="font-mono font-semibold text-slate-200">{stats.total_picks}</span>
                    </div>
                    <div className="flex justify-between items-center text-xs border-b border-slate-800 pb-2">
                        <span className="text-slate-400">Matches Won</span>
                        <span className="font-mono font-semibold text-emerald-400">{stats.wins}</span>
                    </div>
                    <div className="flex justify-between items-center text-xs border-b border-slate-800 pb-2">
                        <span className="text-slate-400">Matches Lost</span>
                        <span className="font-mono font-semibold text-red-400">{stats.losses}</span>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-400">Pending</span>
                        <span className="font-mono font-semibold text-amber-400">{stats.pending}</span>
                    </div>
                </div>
            </div>
          </div>

          <div className="lg:col-span-2 flex">
            <DataTable 
              title={selectedDate ? `Activity Log: ${selectedDate}` : "Recent Model Activity"} 
              subtitle={selectedDate ? `All Matches` : `Latest 15`} 
              data={predictions} 
              columns={columns} 
              emptyMessage="No predictions recorded." 
            />
          </div>
        </div>
      )}
    </div>
  );
}