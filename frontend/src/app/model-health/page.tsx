"use client";
import { useEffect, useState } from "react";
import { HeartPulse } from "lucide-react";
import DataTable, { ColumnDef } from "@/components/DataTable";

interface RollingMetric {
  model_name: string;
  last_100: number;
  last_500: number;
  last_1000: number;
}

interface SystemAlert {
  severity: "CRITICAL" | "WARNING" | "NOTICE" | "HEALTHY";
  model: string;
  trigger: string;
  description: string;
}

export default function ModelHealthPage() {
  const [metrics, setMetrics] = useState<RollingMetric[]>([]);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("${process.env.NEXT_PUBLIC_API_URL}/api/health-monitor")
      .then(res => res.json())
      .then(data => {
        setMetrics(data.metrics || []);
        setAlerts(data.alerts || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching health data:", err);
        setLoading(false);
      });
  }, []);

  // --- 1. Rolling Metrics Columns ---
  const metricsCols: ColumnDef<RollingMetric>[] = [
    {
      header: "Intelligence Engine",
      align: "left",
      render: (row) => {
        let color = "text-white";
        if (row.model_name === "Over 2.5") color = "text-emerald-400";
        if (row.model_name === "Home Win") color = "text-blue-400";
        if (row.model_name === "Away Win") color = "text-purple-400";
        return <span className={`font-bold uppercase tracking-wider text-xs ${color}`}>{row.model_name}</span>;
      }
    },
    {
      header: "Rolling 100",
      align: "center",
      render: (row) => <span className="font-mono text-sm font-bold text-slate-200">{row.last_100.toFixed(1)}%</span>
    },
    {
      header: "Rolling 500",
      align: "center",
      render: (row) => <span className="font-mono text-sm font-semibold text-slate-400">{row.last_500.toFixed(1)}%</span>
    },
    {
      header: "Rolling 1000",
      align: "center",
      render: (row) => <span className="font-mono text-sm font-semibold text-slate-500">{row.last_1000.toFixed(1)}%</span>
    },
    {
      header: "Recent Trend (100 vs 500)",
      align: "right",
      render: (row) => {
        if (row.last_100 === 0 || row.last_500 === 0) return <span className="text-slate-600">-</span>;
        
        const diff = row.last_100 - row.last_500;
        const isPositive = diff >= 0;
        
        return (
          <div className="flex items-center justify-end gap-2">
            <span className={`font-mono text-xs font-bold ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
              {isPositive ? '+' : ''}{diff.toFixed(1)}%
            </span>
            {isPositive ? (
              <div className="w-1.5 h-3 bg-emerald-500/20 rounded-sm border border-emerald-500/30"></div>
            ) : (
              <div className="w-1.5 h-3 bg-red-500/20 rounded-sm border border-red-500/30"></div>
            )}
          </div>
        );
      }
    }
  ];

  // --- 2. System Alerts Columns ---
  const alertCols: ColumnDef<SystemAlert>[] = [
    {
      header: "Severity",
      align: "left",
      render: (row) => {
        let badge = "bg-slate-800 text-slate-300 border-slate-700";
        if (row.severity === "CRITICAL") badge = "bg-red-500/20 text-red-400 border-red-500/30 animate-pulse";
        if (row.severity === "WARNING") badge = "bg-amber-500/20 text-amber-400 border-amber-500/30";
        if (row.severity === "NOTICE") badge = "bg-blue-500/20 text-blue-400 border-blue-500/30";
        if (row.severity === "HEALTHY") badge = "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
        
        return <span className={`px-2 py-1 rounded text-[9px] font-bold tracking-widest uppercase border ${badge}`}>{row.severity}</span>;
      }
    },
    {
      header: "Target Entity",
      align: "left",
      render: (row) => <span className="font-bold text-slate-200 text-xs uppercase">{row.model}</span>
    },
    {
      header: "Trigger Event",
      align: "left",
      render: (row) => <span className="text-xs text-slate-300 font-medium">{row.trigger}</span>
    },
    {
      header: "Diagnostic Description",
      align: "left",
      render: (row) => <span className="text-xs text-slate-500 truncate max-w-md block">{row.description}</span>
    }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <HeartPulse className="w-8 h-8 text-rose-500" /> Model Health Monitor
          </h1>
          <p className="text-slate-400 text-xs mt-1">Real-time monitoring of long-term AI performance, data drift, and algorithmic stability.</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono text-sm animate-pulse">Running system diagnostics...</div>
      ) : (
        <div className="space-y-8 pt-2">
          
          <DataTable 
            title="Active System Diagnostics" 
            subtitle="Automated alerts for performance drops and volume anomalies." 
            data={alerts} 
            columns={alertCols} 
            emptyMessage="No system alerts." 
          />

          <div className="border-t border-slate-800 pt-6">
            <DataTable 
              title="Rolling Performance Matrix" 
              subtitle="Comparing short-term volatility against long-term baselines." 
              data={metrics} 
              columns={metricsCols} 
              emptyMessage="No rolling metrics compiled." 
            />
          </div>

        </div>
      )}
    </div>
  );
}