"use client";
import { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";
import DataTable, { ColumnDef } from "@/components/DataTable";

interface QualityCheck {
  metric: string;
  value: string;
  threshold: string;
  status: string;
}

interface PipelineAlert {
  severity: "CRITICAL" | "WARNING" | "HEALTHY";
  issue: string;
  description: string;
}

export default function DataQualityPage() {
  const [checks, setChecks] = useState<QualityCheck[]>([]);
  const [alerts, setAlerts] = useState<PipelineAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("${process.env.NEXT_PUBLIC_API_URL}/api/data-quality")
      .then(res => res.json())
      .then(data => {
        setChecks(data.checks || []);
        setAlerts(data.alerts || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching data quality:", err);
        setLoading(false);
      });
  }, []);

  const checkCols: ColumnDef<QualityCheck>[] = [
    {
      header: "Validation Metric",
      align: "left",
      render: (row) => <span className="font-bold text-slate-200 text-sm">{row.metric}</span>
    },
    {
      header: "Current Value",
      align: "center",
      render: (row) => <span className="font-mono text-slate-300 font-semibold">{row.value}</span>
    },
    {
      header: "Allowed Threshold",
      align: "center",
      render: (row) => <span className="font-mono text-slate-500 text-xs">{row.threshold}</span>
    },
    {
      header: "Status",
      align: "right",
      render: (row) => {
        if (row.status === "Passed") return <span className="text-emerald-400 text-[10px] font-bold bg-emerald-400/10 px-2 py-1 rounded border border-emerald-400/20 uppercase tracking-widest">Passed</span>;
        if (row.status === "Warning") return <span className="text-amber-400 text-[10px] font-bold bg-amber-400/10 px-2 py-1 rounded border border-amber-400/20 uppercase tracking-widest">Warning</span>;
        return <span className="text-red-400 text-[10px] font-bold bg-red-400/10 px-2 py-1 rounded border border-red-400/20 uppercase tracking-widest">Failed</span>;
      }
    }
  ];

  const alertCols: ColumnDef<PipelineAlert>[] = [
    {
      header: "Severity",
      align: "left",
      render: (row) => {
        let badge = "bg-slate-800 text-slate-300 border-slate-700";
        if (row.severity === "CRITICAL") badge = "bg-red-500/20 text-red-400 border-red-500/30 animate-pulse";
        if (row.severity === "WARNING") badge = "bg-amber-500/20 text-amber-400 border-amber-500/30";
        if (row.severity === "HEALTHY") badge = "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
        
        return <span className={`px-2 py-1 rounded text-[9px] font-bold tracking-widest uppercase border ${badge}`}>{row.severity}</span>;
      }
    },
    {
      header: "Detected Issue",
      align: "left",
      render: (row) => <span className="font-bold text-slate-200 text-xs uppercase">{row.issue}</span>
    },
    {
      header: "Pipeline Diagnostics",
      align: "left",
      render: (row) => <span className="text-xs text-slate-400 block max-w-2xl">{row.description}</span>
    }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-emerald-500" /> Data Quality Monitor
          </h1>
          <p className="text-slate-400 text-xs mt-1">Isolating pipeline anomalies and verifying dataset integrity prior to model inference.</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono text-sm animate-pulse">Auditing database integrity...</div>
      ) : (
        <div className="space-y-8 pt-2">
          
          <DataTable 
            title="Pipeline Event Log" 
            subtitle="Real-time alerts for ingestion streams and missing data." 
            data={alerts} 
            columns={alertCols} 
            emptyMessage="No alerts logged." 
          />

          <div className="border-t border-slate-800 pt-6">
            <DataTable 
              title="Dataset Validation Matrix" 
              subtitle="Checking current database state against absolute thresholds." 
              data={checks} 
              columns={checkCols} 
              emptyMessage="No validation checks executed." 
            />
          </div>

        </div>
      )}
    </div>
  );
}