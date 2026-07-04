"use client";

import ThemeToggle from "./ThemeToggle";

export default function AuthLayout({
  children,
  title,
  subtitle,
}: {
  children: React.ReactNode;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="min-h-screen flex">
      {/* ── Left panel 65% ─────────────────────────────────────── */}
      <div className="hidden lg:flex lg:w-[60%] relative overflow-hidden bg-[#050e08] flex-col">
        {/* Aurora blobs */}
        <div className="absolute -top-[15%] -left-[10%] w-[55%] h-[55%] bg-emerald-500/25 rounded-full blur-[130px] pointer-events-none" />
        <div className="absolute top-[25%] -right-[12%] w-[45%] h-[50%] bg-teal-400/15 rounded-full blur-[110px] pointer-events-none" />
        <div className="absolute -bottom-[10%] left-[25%] w-[40%] h-[40%] bg-cyan-500/12 rounded-full blur-[90px] pointer-events-none" />

        <div className="relative z-10 flex flex-col h-full p-12 xl:p-16">
          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center shrink-0">
              <span className="text-white font-bold text-[11px] tracking-tight">CW</span>
            </div>
            <span className="text-white font-semibold text-sm tracking-tight">ClimaWatch</span>
          </div>

          {/* Headline — vertically centred */}
          <div className="flex-1 flex items-center">
            <h1 className="text-[42px] xl:text-[52px] font-bold text-white leading-[1.08] tracking-tight max-w-lg">
              Climate-health intelligence for Nigeria
            </h1>
          </div>

          {/* Floating risk card */}
          <div className="w-72 bg-white/[0.06] backdrop-blur-sm border border-white/[0.08] rounded-2xl p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-white/50 text-[11px] font-medium uppercase tracking-widest">
                Live Risk
              </span>
              <span className="px-2 py-0.5 bg-orange-500/20 text-orange-300 text-[11px] font-semibold rounded-full">
                HIGH
              </span>
            </div>
            <div className="text-white font-semibold text-lg leading-tight mb-0.5">Lagos State</div>
            <div className="text-white/35 text-xs mb-4">Overall risk score</div>
            <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full w-[81%] bg-gradient-to-r from-orange-400 to-orange-500 rounded-full" />
            </div>
            <div className="flex justify-between mt-1.5">
              <span className="text-white/25 text-[11px]">0</span>
              <span className="text-orange-300 text-[11px] font-medium">81.4 / 100</span>
              <span className="text-white/25 text-[11px]">100</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Right panel 35% ─────────────────────────────────────── */}
      <div className="flex-1 relative bg-white dark:bg-zinc-950 flex flex-col">
        <div className="absolute top-5 right-5 z-10">
          <ThemeToggle />
        </div>

        <div className="flex-1 flex items-center justify-center px-8 py-16">
          <div className="w-full max-w-[320px]">
            {/* Mobile logo */}
            <div className="flex items-center gap-2 mb-8 lg:hidden">
              <div className="w-7 h-7 bg-emerald-500 rounded-lg flex items-center justify-center shrink-0">
                <span className="text-white font-bold text-[10px] tracking-tight">CW</span>
              </div>
              <span className="font-semibold text-slate-900 dark:text-white text-sm tracking-tight">
                ClimaWatch
              </span>
            </div>

            <div className="mb-7">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight mb-1.5">
                {title}
              </h2>
              <p className="text-sm text-slate-500 dark:text-zinc-400">{subtitle}</p>
            </div>

            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
