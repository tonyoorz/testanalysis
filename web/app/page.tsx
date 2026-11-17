"use client";

import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Bot,
  ChevronRight,
  CircleDot,
  Filter,
  LayoutDashboard,
  Search,
  Sparkles,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useMemo, useState } from "react";

import { navItems, pageCopy, type Metric, type NavKey } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

function toneClass(tone: Metric["tone"]) {
  if (tone === "up") return "text-emerald-300 bg-emerald-500/10";
  if (tone === "down") return "text-sky-300 bg-sky-500/10";
  return "text-slate-300 bg-white/5";
}

export default function Home() {
  const [active, setActive] = useState<NavKey>("overview");
  const data = pageCopy[active];

  const totalStatus = useMemo(
    () => data.statuses.reduce((sum, item) => sum + item.value, 0),
    [data.statuses]
  );

  return (
    <main className="grain min-h-screen text-[var(--text)]">
      <div className="mx-auto flex min-h-screen max-w-[1680px] gap-6 px-4 py-4 lg:px-6">
        <aside className="panel-strong hidden w-[284px] shrink-0 rounded-[28px] p-5 lg:flex lg:flex-col">
          <div className="flex items-center gap-3 border-b border-white/10 pb-5">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--brand-soft)] text-[var(--text)] ring-1 ring-white/10">
              <LayoutDashboard className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-[var(--muted)]">
                TestAnalysis
              </p>
              <h1 className="text-lg font-semibold">Quality Intelligence</h1>
            </div>
          </div>

          <div className="mt-6 space-y-2">
            {navItems.map((item) => {
              const isActive = item.key === active;
              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => setActive(item.key)}
                  className={cn(
                    "w-full rounded-2xl border px-4 py-3 text-left transition",
                    isActive
                      ? "border-[var(--line-strong)] bg-[linear-gradient(180deg,rgba(124,92,255,0.22),rgba(124,92,255,0.08))] shadow-[0_18px_40px_rgba(60,50,130,0.28)]"
                      : "border-transparent bg-white/[0.02] hover:border-white/10 hover:bg-white/[0.04]"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{item.label}</span>
                    <ChevronRight
                      className={cn(
                        "h-4 w-4 transition",
                        isActive ? "text-white" : "text-slate-500"
                      )}
                    />
                  </div>
                  <p className="mt-1 text-xs text-[var(--muted)]">{item.hint}</p>
                </button>
              );
            })}
          </div>

          <div className="panel mt-6 rounded-[24px] p-4">
            <div className="flex items-center gap-2 text-sm text-white/90">
              <Sparkles className="h-4 w-4 text-violet-300" />
              平台升级方向
            </div>
            <p className="mt-3 text-sm leading-6 text-[var(--muted)]">
              当前为平台版前端壳子，下一步可直接接入 Python
              数据接口，替换本页假数据。
            </p>
            <div className="mt-4 flex items-center gap-2 text-xs text-emerald-300">
              <CircleDot className="h-3.5 w-3.5" />
              接口层预留中
            </div>
          </div>

          <div className="mt-auto rounded-[24px] border border-white/8 bg-black/20 p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/5">
                <Bot className="h-5 w-5 text-sky-300" />
              </div>
              <div>
                <p className="text-sm font-medium">AI 分析助手</p>
                <p className="text-xs text-[var(--muted)]">后续可接告警摘要与问答</p>
              </div>
            </div>
          </div>
        </aside>

        <section className="flex min-w-0 flex-1 flex-col gap-6">
          <header className="panel rounded-[28px] px-5 py-4 lg:px-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-[var(--muted)]">
                  <span>Platform Dashboard</span>
                  <span className="h-1 w-1 rounded-full bg-[var(--info)]" />
                  <span>2026-05-21 22:00</span>
                </div>
                <h2 className="text-2xl font-semibold tracking-tight lg:text-[30px]">
                  {data.title}
                </h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-[var(--muted)]">
                  {data.subtitle}
                </p>
              </div>

              <div className="flex flex-col gap-3 lg:min-w-[430px]">
                <div className="flex items-center gap-3">
                  <label className="panel flex h-11 flex-1 items-center gap-3 rounded-2xl px-4">
                    <Search className="h-4 w-4 text-slate-400" />
                    <input
                      readOnly
                      value="搜索模块 / 项目 / Ticket"
                      className="w-full bg-transparent text-sm text-slate-400 outline-none"
                    />
                  </label>
                  <button
                    type="button"
                    className="panel flex h-11 items-center gap-2 rounded-2xl px-4 text-sm text-white/90"
                  >
                    <Filter className="h-4 w-4" />
                    筛选
                  </button>
                </div>
                <div className="flex flex-wrap gap-2 text-xs text-[var(--muted)]">
                  <span className="rounded-full border border-white/10 px-3 py-1.5">
                    China Specific
                  </span>
                  <span className="rounded-full border border-white/10 px-3 py-1.5">
                    P1 / P2
                  </span>
                  <span className="rounded-full border border-emerald-400/20 bg-emerald-500/10 px-3 py-1.5 text-emerald-300">
                    数据已同步
                  </span>
                </div>
              </div>
            </div>
          </header>

          <div className="grid gap-4 xl:grid-cols-4">
            {data.metrics.map((metric) => {
              const positive = metric.tone === "up";
              return (
                <div
                  key={metric.label}
                  className="panel metric-glow rounded-[24px] p-5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm text-[var(--muted)]">{metric.label}</p>
                      <p className="mt-4 text-3xl font-semibold tracking-tight">
                        {metric.value}
                      </p>
                    </div>
                    <div className={cn("rounded-full px-2.5 py-1 text-xs", toneClass(metric.tone))}>
                      <span className="inline-flex items-center gap-1">
                        {positive ? (
                          <ArrowUpRight className="h-3.5 w-3.5" />
                        ) : metric.tone === "down" ? (
                          <ArrowDownRight className="h-3.5 w-3.5" />
                        ) : (
                          <CircleDot className="h-3.5 w-3.5" />
                        )}
                        {metric.delta}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="grid gap-6 2xl:grid-cols-[minmax(0,1.3fr)_380px]">
            <div className="space-y-6">
              <section className="panel rounded-[28px] p-5 lg:p-6">
                <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                  <div>
                    <p className="text-sm font-medium text-white/90">缺陷流入与收敛趋势</p>
                    <p className="mt-1 text-sm text-[var(--muted)]">
                      用平台化图表区承接后续从 Python 数据层返回的时序数据。
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
                    <span className="rounded-full bg-white/5 px-3 py-1.5">近 6 周</span>
                    <span className="rounded-full bg-[var(--brand-soft)] px-3 py-1.5 text-violet-200">
                      当前静态壳子
                    </span>
                  </div>
                </div>

                <div className="h-[320px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data.trend} barGap={10}>
                      <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
                      <XAxis
                        dataKey="week"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: "#9fb2cf", fontSize: 12 }}
                      />
                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: "#9fb2cf", fontSize: 12 }}
                      />
                      <Tooltip
                        cursor={{ fill: "rgba(255,255,255,0.04)" }}
                        contentStyle={{
                          background: "rgba(11,19,35,0.95)",
                          border: "1px solid rgba(148,163,184,0.16)",
                          borderRadius: "16px",
                          color: "#eff6ff",
                        }}
                      />
                      <Bar dataKey="incoming" radius={[10, 10, 0, 0]} fill="#7c5cff" />
                      <Bar dataKey="resolved" radius={[10, 10, 0, 0]} fill="#4dd0a8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>

              <section className="panel rounded-[28px] p-5 lg:p-6">
                <div className="mb-5 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-white/90">问题明细优先级</p>
                    <p className="mt-1 text-sm text-[var(--muted)]">
                      这里后续可映射 `qgate.py` 的明细表、Top Issue 或 Octane 链接。
                    </p>
                  </div>
                  <div className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] px-3 py-1.5 text-xs text-amber-200">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    高风险优先
                  </div>
                </div>

                <div className="scrollbar-thin overflow-x-auto">
                  <table className="min-w-full border-separate border-spacing-y-2 text-sm">
                    <thead>
                      <tr className="text-left text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
                        <th className="px-4 py-2 font-medium">模块</th>
                        <th className="px-4 py-2 font-medium">Owner</th>
                        <th className="px-4 py-2 font-medium">Severity</th>
                        <th className="px-4 py-2 font-medium">Aging</th>
                        <th className="px-4 py-2 font-medium">状态</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.rows.map((row) => (
                        <tr key={`${row.module}-${row.owner}`} className="panel">
                          <td className="rounded-l-2xl px-4 py-4 font-medium text-white/95">
                            {row.module}
                          </td>
                          <td className="px-4 py-4 text-[var(--muted)]">{row.owner}</td>
                          <td className="px-4 py-4">
                            <span className="rounded-full bg-white/6 px-3 py-1 text-xs">
                              {row.severity}
                            </span>
                          </td>
                          <td className="px-4 py-4 text-[var(--muted)]">{row.aging}</td>
                          <td className="rounded-r-2xl px-4 py-4">
                            <span className="rounded-full bg-sky-500/10 px-3 py-1 text-xs text-sky-200">
                              {row.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </div>

            <div className="space-y-6">
              <section className="panel rounded-[28px] p-5 lg:p-6">
                <div className="flex items-end justify-between">
                  <div>
                    <p className="text-sm font-medium text-white/90">状态分布</p>
                    <p className="mt-1 text-sm text-[var(--muted)]">
                      总量 {totalStatus}，适合承接缺陷状态或测试状态占比。
                    </p>
                  </div>
                </div>

                <div className="mt-4 flex h-[240px] items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={data.statuses}
                        dataKey="value"
                        nameKey="name"
                        innerRadius={70}
                        outerRadius={96}
                        paddingAngle={3}
                      >
                        {data.statuses.map((entry) => (
                          <Cell key={entry.name} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          background: "rgba(11,19,35,0.95)",
                          border: "1px solid rgba(148,163,184,0.16)",
                          borderRadius: "16px",
                          color: "#eff6ff",
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="space-y-3">
                  {data.statuses.map((status) => (
                    <div
                      key={status.name}
                      className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/[0.02] px-4 py-3"
                    >
                      <div className="flex items-center gap-3">
                        <span
                          className="h-2.5 w-2.5 rounded-full"
                          style={{ backgroundColor: status.color }}
                        />
                        <span className="text-sm text-white/90">{status.name}</span>
                      </div>
                      <span className="text-sm text-[var(--muted)]">{status.value}</span>
                    </div>
                  ))}
                </div>
              </section>

              <section className="panel rounded-[28px] p-5 lg:p-6">
                <div className="flex items-center gap-2 text-sm font-medium text-white/90">
                  <Bot className="h-4 w-4 text-sky-300" />
                  AI Summary
                </div>
                <div className="mt-4 space-y-3 text-sm leading-6 text-[var(--muted)]">
                  <p className="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3">
                    本周收敛速度提升，`resolved` 已连续三周高于 `incoming`，说明问题清理节奏在改善。
                  </p>
                  <p className="rounded-2xl border border-violet-400/12 bg-violet-500/8 px-4 py-3">
                    建议先接入 `Top Issue` 与 `Long Runner` 两类真实数据，能最快体现平台价值。
                  </p>
                  <p className="rounded-2xl border border-emerald-400/12 bg-emerald-500/8 px-4 py-3">
                    后续接口层可从 Python 输出 JSON，再由 Next 前端按模块分别消费。
                  </p>
                </div>
              </section>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
