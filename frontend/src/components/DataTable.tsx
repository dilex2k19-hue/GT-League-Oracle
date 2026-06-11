import React from "react";

// This tells TypeScript exactly how to structure our dynamic columns
export interface ColumnDef<T> {
  header: string | React.ReactNode;
  align?: "left" | "center" | "right";
  render: (row: T, index: number) => React.ReactNode;
}

interface DataTableProps<T> {
  title?: string;
  subtitle?: string;
  data: T[];
  columns: ColumnDef<T>[];
  emptyMessage?: string;
}

export default function DataTable<T>({ title, subtitle, data, columns, emptyMessage = "No data available." }: DataTableProps<T>) {
  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden w-full">
      
      {/* --- MASTER HEADER STYLE --- */}
      {(title || subtitle) && (
        <div className="px-5 py-3 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center">
          <div>{title && <h2 className="text-sm font-semibold text-white">{title}</h2>}</div>
          {subtitle && <span className="text-[9px] uppercase tracking-wider text-slate-500">{subtitle}</span>}
        </div>
      )}

      <div className="overflow-x-auto no-scrollbar">
        {/* --- MASTER TABLE STYLE (Edit text-xs here to scale the whole table!) --- */}
        <table className="w-full text-left text-xs text-slate-300">
          
          {/* --- MASTER COLUMN HEADER STYLE --- */}
          <thead className="bg-slate-950/50 text-[9px] uppercase font-semibold text-slate-500 border-b border-slate-800/60">
            <tr>
              {columns.map((col, idx) => (
                <th key={idx} className={`px-5 py-2 ${col.align === 'center' ? 'text-center' : col.align === 'right' ? 'text-right' : 'text-left'}`}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>

          {/* --- MASTER ROW STYLE --- */}
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-5 py-4 text-center text-slate-500">{emptyMessage}</td>
              </tr>
            ) : (
              data.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-slate-850 transition-colors">
                  {columns.map((col, colIndex) => (
                    <td key={colIndex} className={`px-5 py-2 ${col.align === 'center' ? 'text-center' : col.align === 'right' ? 'text-right' : 'text-left'}`}>
                      {col.render(row, rowIndex)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>

        </table>
      </div>
    </div>
  );
}