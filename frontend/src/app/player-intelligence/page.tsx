"use client";
import { useEffect, useState } from "react";
import DataTable, { ColumnDef } from "@/components/DataTable";
import { Users } from "lucide-react";

interface PlayerStat {
  player: string;
  total_matches: number;
  over_total: number;
  over_wins: number;
  home_total: number;
  home_wins: number;
  away_total: number;
  away_wins: number;
  total_decided: number;
  total_wins: number;
}

export default function PlayerIntelligencePage() {
  const [players, setPlayers] = useState<PlayerStat[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortConfig, setSortConfig] = useState<{ key: keyof PlayerStat | 'overall_rate' | 'over_rate', direction: 'asc' | 'desc' }>({ key: 'total_matches', direction: 'desc' });

  useEffect(() => {
    fetch("http://localhost:8000/api/player-intelligence")
      .then(res => res.json())
      .then(data => {
        setPlayers(data.players || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching player data:", err);
        setLoading(false);
      });
  }, []);

  const sortedPlayers = [...players].sort((a, b) => {
    let aValue = 0; let bValue = 0;
    if (sortConfig.key === 'overall_rate') {
      aValue = a.total_decided > 0 ? (a.total_wins / a.total_decided) : 0;
      bValue = b.total_decided > 0 ? (b.total_wins / b.total_decided) : 0;
    } else if (sortConfig.key === 'over_rate') {
      aValue = a.over_total > 0 ? (a.over_wins / a.over_total) : 0;
      bValue = b.over_total > 0 ? (b.over_wins / b.over_total) : 0;
    } else {
      aValue = a[sortConfig.key] as number;
      bValue = b[sortConfig.key] as number;
    }
    if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  const handleSort = (key: keyof PlayerStat | 'overall_rate' | 'over_rate') => {
    setSortConfig({
      key,
      direction: sortConfig.key === key && sortConfig.direction === 'desc' ? 'asc' : 'desc',
    });
  };

  const renderRate = (wins: number, total: number, colorClass: string) => {
    if (total === 0) return <span className="text-slate-600 text-xs">-</span>;
    const rate = ((wins / total) * 100).toFixed(1);
    return (
      <div className="flex flex-col items-center">
        <span className={`font-mono font-bold ${colorClass}`}>{rate}%</span>
        <span className="text-[9px] text-slate-500 uppercase">{wins}/{total} Won</span>
      </div>
    );
  };

  // Defining our columns for the Master Component
  const columns: ColumnDef<PlayerStat>[] = [
    {
      header: (
        <button onClick={() => handleSort('player')} className="hover:text-white transition-colors uppercase tracking-wider flex items-center gap-1">
          Player Name {sortConfig.key === 'player' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
        </button>
      ),
      align: "left",
      render: (p) => <span className="font-bold text-slate-200">{p.player}</span>
    },
    {
      header: (
        <button onClick={() => handleSort('total_matches')} className="hover:text-white transition-colors uppercase tracking-wider flex items-center gap-1 justify-center w-full">
          Signals {sortConfig.key === 'total_matches' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
        </button>
      ),
      align: "center",
      render: (p) => <span className="font-mono text-slate-400">{p.total_matches}</span>
    },
    {
      header: (
        <button onClick={() => handleSort('over_rate')} className="hover:text-emerald-400 transition-colors uppercase tracking-wider flex items-center gap-1 justify-center w-full">
          Over 2.5 Rate {sortConfig.key === 'over_rate' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
        </button>
      ),
      align: "center",
      render: (p) => renderRate(p.over_wins, p.over_total, "text-emerald-400")
    },
    {
      header: "Home Hit Rate",
      align: "center",
      render: (p) => renderRate(p.home_wins, p.home_total, "text-blue-400")
    },
    {
      header: "Away Hit Rate",
      align: "center",
      render: (p) => renderRate(p.away_wins, p.away_total, "text-purple-400")
    },
    {
      header: (
        <button onClick={() => handleSort('overall_rate')} className="hover:text-white transition-colors uppercase tracking-wider flex items-center gap-1 justify-end w-full">
          Predictability {sortConfig.key === 'overall_rate' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
        </button>
      ),
      align: "right",
      render: (p) => {
        const overallRate = p.total_decided > 0 ? (p.total_wins / p.total_decided) * 100 : 0;
        return (
          <div className="flex flex-col items-end">
            <span className={`font-mono font-bold text-lg ${overallRate >= 60 ? 'text-white' : 'text-slate-400'}`}>
                {overallRate.toFixed(1)}%
            </span>
            <span className="text-[9px] text-slate-500 uppercase">{p.total_wins}W - {p.total_decided - p.total_wins}L</span>
          </div>
        );
      }
    },
    {
      header: "Insights",
      align: "center",
      render: (p) => {
        const overallRate = p.total_decided > 0 ? (p.total_wins / p.total_decided) * 100 : 0;
        const overRate = p.over_total > 0 ? (p.over_wins / p.over_total) * 100 : 0;
        let tags = [];
        if (overallRate < 40 && p.total_decided >= 10) tags.push(<span key="killer" className="bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded text-[9px] font-bold tracking-wider">MODEL KILLER</span>);
        if (overallRate > 75 && p.total_decided >= 10) tags.push(<span key="safe" className="bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded text-[9px] font-bold tracking-wider">HIGH PREDICTABILITY</span>);
        if (overRate >= 80 && p.over_total >= 5) tags.push(<span key="over" className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded text-[9px] font-bold tracking-wider">OVER MACHINE</span>);

        return (
          <div className="flex flex-col gap-1 items-center justify-center">
              {tags.length > 0 ? tags : <span className="text-slate-600 text-[9px] font-mono">NEUTRAL</span>}
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
           <Users className="w-8 h-8 text-indigo-400" /> Player Intelligence Center
          </h1>
          <p className="text-slate-400 text-xs mt-1">Discovering behavioral anomalies, Over Machines, and Model Killers.</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono text-sm animate-pulse">Scanning player profiles...</div>
      ) : (
        <DataTable 
          data={sortedPlayers} 
          columns={columns} 
          emptyMessage="No player data accumulated yet." 
        />
      )}
    </div>
  );
}