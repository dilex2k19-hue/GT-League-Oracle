"use client";
import { useEffect, useState } from "react";
import DataTable, { ColumnDef } from "@/components/DataTable";
import { Activity } from "lucide-react";

interface Scoreline {
  scoreline: string;
  count: number;
}

interface Saboteur {
  player: string;
  losses: number;
}

interface BlindSpot {
  model_name: string;
  total_failures: number;
  avg_losing_confidence: number;
}

export default function FailureAnalysisPage() {
  const [scorelines, setScorelines] = useState<Scoreline[]>([]);
  const [saboteurs, setSaboteurs] = useState<Saboteur[]>([]);
  const [blindSpots, setBlindSpots] = useState<BlindSpot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/failure-analysis")
      .then(res => res.json())
      .then(data => {
        setScorelines(data.scorelines || []);
        setSaboteurs(data.saboteurs || []);
        setBlindSpots(data.blind_spots || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching failure data:", err);
        setLoading(false);
      });
  }, []);

  // --- 1. Scoreline Columns ---
  const scorelineCols: ColumnDef<Scoreline>[] = [
    {
      header: "Final Score",
      align: "left",
      render: (row) => (
        <span className="font-mono text-sm font-bold text-slate-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
          {row.scoreline}
        </span>
      )
    },
    {
      header: "Losses",
      align: "right",
      render: (row) => <span className="text-sm font-bold text-red-400">{row.count}</span>
    }
  ];

  // --- 2. Saboteur Columns ---
  const saboteurCols: ColumnDef<Saboteur>[] = [
    {
      header: "#",
      align: "center",
      render: (_, idx) => <span className="text-slate-600 font-mono text-xs">{idx + 1}</span>
    },
    {
      header: "Player",
      align: "left",
      render: (row) => <span className="font-bold text-slate-200">{row.player}</span>
    },
    {
      header: "Losses",
      align: "right",
      render: (row) => <span className="text-sm font-bold text-red-400">{row.losses}</span>
    }
  ];

  // --- 3. Blind Spot Columns ---
  const blindSpotCols: ColumnDef<BlindSpot>[] = [
    {
      header: "Model",
      align: "left",
      render: (row) => {
        let badgeColor = "bg-slate-800 text-slate-300";
        if (row.model_name === "Over 2.5") badgeColor = "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
        if (row.model_name === "Home Win") badgeColor = "bg-blue-500/20 text-blue-400 border border-blue-500/30";
        if (row.model_name === "Away Win") badgeColor = "bg-purple-500/20 text-purple-400 border border-purple-500/30";
        return (
          <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wider uppercase ${badgeColor}`}>
            {row.model_name}
          </span>
        );
      }
    },
    {
      header: "Losses",
      align: "center",
      render: (row) => <span className="text-sm font-bold text-red-400">{row.total_failures}</span>
    },
    {
      header: "Avg Conf",
      align: "right",
      render: (row) => <span className="font-mono text-sm font-bold text-amber-400">{row.avg_losing_confidence}%</span>
    }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-red-400 flex items-center gap-3">
           <Activity className="w-8 h-8" /> Prediction Failure Analysis
          </h1>
          <p className="text-slate-400 text-xs mt-1">Diagnosing the root causes, scorelines, and actors behind algorithmic losses.</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono text-sm animate-pulse">Running post-mortem diagnostics...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
          <DataTable 
            title="Scoreline Graveyard" 
            subtitle="Common Loss Scores" 
            data={scorelines} 
            columns={scorelineCols} 
            emptyMessage="No scoreline data recorded." 
          />
          <DataTable 
            title="The Saboteurs" 
            subtitle="Most Frequent Losers" 
            data={saboteurs} 
            columns={saboteurCols} 
            emptyMessage="No player data recorded." 
          />
          <DataTable 
            title="Model Blind Spots" 
            subtitle="Failure Distributions" 
            data={blindSpots} 
            columns={blindSpotCols} 
            emptyMessage="No failure data recorded." 
          />
        </div>
      )}
    </div>
  );
}