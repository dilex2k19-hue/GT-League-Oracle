import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { 
  LayoutDashboard, 
  Target, 
  Users, 
  Activity, 
  Scale, 
  Zap, 
  Home, 
  Rocket,
  HeartPulse,
  BrainCircuit,
  ShieldCheck
} from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "GT Oracle v2.0",
  description: "Autonomous Intelligence Agent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} flex h-screen bg-slate-950 text-white overflow-hidden`}>
        
        {/* THE AUTO-COLLAPSING SIDEBAR 
          w-20 (collapsed) -> hover:w-64 (expanded)
          overflow-hidden ensures text doesn't wrap when shrunk
        */}
        <aside className="w-20 hover:w-64 transition-all duration-300 ease-in-out bg-slate-950 border-r border-slate-800 flex flex-col group z-50 flex-shrink-0 overflow-hidden relative">
          
          {/* Logo Section */}
          <div className="h-20 flex items-center px-6 border-b border-slate-800">
            <div className="flex items-center min-w-max gap-4">
              <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center font-bold text-slate-950 shadow-[0_0_15px_rgba(16,185,129,0.3)] shrink-0">
                GT
              </div>
              <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="font-bold tracking-wide text-sm text-slate-200">ORACLE v2.0</div>
                <div className="text-[9px] text-emerald-400 font-bold tracking-widest mt-0.5">AUTONOMOUS AGENT</div>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex-1 py-8 overflow-y-auto overflow-x-hidden flex flex-col gap-2 no-scrollbar">
            
            <div className="px-6 mb-2 min-w-max">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                Core Hub
              </span>
            </div>

            <Link href="/" className="flex items-center px-6 py-3 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
              <LayoutDashboard size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Overview Dashboard
              </span>
            </Link>

            <Link href="/confidence-analysis" className="flex items-center px-6 py-3 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
              <Target size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Confidence Analysis
              </span>
            </Link>

            <Link href="/player-intelligence" className="flex items-center px-6 py-3 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
              <Users size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Player Intelligence
              </span>
            </Link>

            <Link href="/failure-analysis" className="flex items-center px-6 py-3 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
              <Activity size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Failure Analysis
              </span>
            </Link>

            <Link href="/threshold-optimizer" className="flex items-center px-6 py-3 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
              <Scale size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Threshold Optimizer
              </span>
            </Link>

            <Link href="/model-health" className="flex items-center px-6 py-3 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
              <HeartPulse size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Model Health Monitor
              </span>
            </Link>

            <Link href="/feature-intelligence" className="flex items-center px-6 py-3 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
              <BrainCircuit size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Feature Intelligence
              </span>
            </Link>

            <Link href="/data-quality" className="flex items-center px-6 py-3 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
              <ShieldCheck size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Data Quality Monitor
              </span>
            </Link>

            <div className="px-6 mt-6 mb-2 min-w-max">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                AI Sub-Models
              </span>
            </div>

            <Link href="/models/over25" className="flex items-center px-6 py-3 text-emerald-500/80 hover:text-emerald-400 hover:bg-slate-800 transition-colors">
              <Zap size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Over 2.5 Goals
              </span>
            </Link>

            <Link href="/models/home-win" className="flex items-center px-6 py-3 text-blue-500/80 hover:text-blue-400 hover:bg-slate-800 transition-colors">
              <Home size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Home Win Edge
              </span>
            </Link>

            <Link href="/models/away-win" className="flex items-center px-6 py-3 text-purple-500/80 hover:text-purple-400 hover:bg-slate-800 transition-colors">
              <Rocket size={20} className="shrink-0" />
              <span className="ml-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
                Away Win Exploits
              </span>
            </Link>

          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto bg-[#0a0f1a] no-scrollbar">
          {children}
        </main>

      </body>
    </html>
  );
}