export type NavKey =
  | "overview"
  | "project"
  | "defect-high"
  | "long-runner"
  | "coverage"
  | "test-status";

export type NavItem = {
  key: NavKey;
  label: string;
  hint: string;
};

export type Metric = {
  label: string;
  value: string;
  delta: string;
  tone: "up" | "down" | "neutral";
};

export type TrendPoint = {
  week: string;
  incoming: number;
  resolved: number;
};

export type StatusPoint = {
  name: string;
  value: number;
  color: string;
};

export type TableRow = {
  module: string;
  owner: string;
  severity: string;
  aging: string;
  status: string;
};

export const navItems: NavItem[] = [
  { key: "overview", label: "Top Issue", hint: "总体风险和趋势" },
  { key: "project", label: "项目分析", hint: "项目和版本横向对比" },
  { key: "defect-high", label: "高频缺陷", hint: "高频模块定位" },
  { key: "long-runner", label: "长周期分析", hint: "超期问题收敛" },
  { key: "coverage", label: "覆盖率", hint: "覆盖缺口和趋势" },
  { key: "test-status", label: "测试状态", hint: "执行状态和通过率" },
];

export const pageCopy: Record<
  NavKey,
  {
    title: string;
    subtitle: string;
    metrics: Metric[];
    trend: TrendPoint[];
    statuses: StatusPoint[];
    rows: TableRow[];
  }
> = {
  overview: {
    title: "Top Issue 分析",
    subtitle: "聚焦关键风险、缺陷堆积模块和收敛速度，适合作为首页总览。",
    metrics: [
      { label: "活跃缺陷", value: "184", delta: "+12.4%", tone: "up" },
      { label: "平均关闭周期", value: "6.8 天", delta: "-1.1 天", tone: "down" },
      { label: "高风险模块", value: "7", delta: "2 个待关注", tone: "neutral" },
      { label: "覆盖率达标", value: "82%", delta: "+4.6%", tone: "up" },
    ],
    trend: [
      { week: "W18", incoming: 31, resolved: 24 },
      { week: "W19", incoming: 28, resolved: 26 },
      { week: "W20", incoming: 36, resolved: 29 },
      { week: "W21", incoming: 24, resolved: 33 },
      { week: "W22", incoming: 18, resolved: 27 },
      { week: "W23", incoming: 22, resolved: 31 },
    ],
    statuses: [
      { name: "Open", value: 68, color: "#6ea8fe" },
      { name: "In Progress", value: 42, color: "#7c5cff" },
      { name: "Blocked", value: 19, color: "#ff8a65" },
      { name: "Ready To Verify", value: 26, color: "#4dd0a8" },
      { name: "Closed", value: 29, color: "#8bc34a" },
    ],
    rows: [
      { module: "Headunit Voice", owner: "DTSV China", severity: "P1", aging: "14 天", status: "处理中" },
      { module: "App Center CN", owner: "Integration", severity: "P1", aging: "11 天", status: "待验证" },
      { module: "Navigation Lane", owner: "FIT China", severity: "P2", aging: "8 天", status: "处理中" },
      { module: "Wechat VoIP", owner: "Cockpit", severity: "P2", aging: "7 天", status: "待分派" },
      { module: "Music Streaming", owner: "Vendor", severity: "P3", aging: "5 天", status: "已收敛" },
    ],
  },
  project: {
    title: "项目分析",
    subtitle: "对比不同项目在缺陷密度、关闭周期和交付风险上的表现差异。",
    metrics: [
      { label: "项目数", value: "5", delta: "含 2 个关键项目", tone: "neutral" },
      { label: "平均风险指数", value: "73", delta: "+5", tone: "up" },
      { label: "超期项目", value: "2", delta: "-1", tone: "down" },
      { label: "版本稳定度", value: "86%", delta: "+2.3%", tone: "up" },
    ],
    trend: [
      { week: "W18", incoming: 16, resolved: 11 },
      { week: "W19", incoming: 18, resolved: 14 },
      { week: "W20", incoming: 22, resolved: 15 },
      { week: "W21", incoming: 14, resolved: 19 },
      { week: "W22", incoming: 12, resolved: 18 },
      { week: "W23", incoming: 10, resolved: 17 },
    ],
    statuses: [
      { name: "Alpha", value: 23, color: "#6ea8fe" },
      { name: "Beta", value: 28, color: "#7c5cff" },
      { name: "SOP", value: 18, color: "#4dd0a8" },
      { name: "Hold", value: 8, color: "#ff8a65" },
    ],
    rows: [
      { module: "Project Atlas", owner: "Platform", severity: "High", aging: "9 天", status: "风险升高" },
      { module: "Project Vega", owner: "IVI", severity: "Medium", aging: "6 天", status: "可控" },
      { module: "Project Neo", owner: "EE", severity: "High", aging: "12 天", status: "需加速" },
      { module: "Project Iris", owner: "ADAS", severity: "Low", aging: "4 天", status: "稳定" },
      { module: "Project Luna", owner: "App", severity: "Medium", aging: "7 天", status: "观察中" },
    ],
  },
  "defect-high": {
    title: "缺陷高频分析",
    subtitle: "识别重复出现的问题域，帮助团队优先做根因治理。",
    metrics: [
      { label: "重复缺陷簇", value: "14", delta: "+3", tone: "up" },
      { label: "主要来源模块", value: "Voice / App", delta: "Top 2", tone: "neutral" },
      { label: "复发率", value: "28%", delta: "-3.2%", tone: "down" },
      { label: "根因已定位", value: "10", delta: "71%", tone: "up" },
    ],
    trend: [
      { week: "W18", incoming: 19, resolved: 10 },
      { week: "W19", incoming: 21, resolved: 12 },
      { week: "W20", incoming: 24, resolved: 14 },
      { week: "W21", incoming: 16, resolved: 18 },
      { week: "W22", incoming: 13, resolved: 20 },
      { week: "W23", incoming: 15, resolved: 19 },
    ],
    statuses: [
      { name: "Voice", value: 36, color: "#7c5cff" },
      { name: "App Center", value: 25, color: "#6ea8fe" },
      { name: "Navigation", value: 18, color: "#4dd0a8" },
      { name: "Account", value: 12, color: "#ff8a65" },
    ],
    rows: [
      { module: "Voice Intent", owner: "AI Team", severity: "P1", aging: "10 天", status: "根因分析中" },
      { module: "Mini Program", owner: "Tencent", severity: "P2", aging: "8 天", status: "待修复" },
      { module: "Account Login", owner: "SSO", severity: "P2", aging: "6 天", status: "复发" },
      { module: "Route Search", owner: "Map", severity: "P3", aging: "5 天", status: "待验证" },
      { module: "Media Resume", owner: "Audio", severity: "P3", aging: "3 天", status: "处理中" },
    ],
  },
  "long-runner": {
    title: "长周期分析",
    subtitle: "追踪长期未关闭问题，优先打通阻塞流程和跨团队依赖。",
    metrics: [
      { label: "长周期缺陷", value: "32", delta: "-6", tone: "down" },
      { label: "平均停留时长", value: "18.4 天", delta: "-2.1 天", tone: "down" },
      { label: "阻塞单量", value: "9", delta: "3 个需升级", tone: "neutral" },
      { label: "超时占比", value: "17%", delta: "-1.4%", tone: "down" },
    ],
    trend: [
      { week: "W18", incoming: 12, resolved: 8 },
      { week: "W19", incoming: 11, resolved: 9 },
      { week: "W20", incoming: 14, resolved: 8 },
      { week: "W21", incoming: 9, resolved: 12 },
      { week: "W22", incoming: 7, resolved: 13 },
      { week: "W23", incoming: 8, resolved: 14 },
    ],
    statuses: [
      { name: "External Dependency", value: 14, color: "#ff8a65" },
      { name: "Need Reproduce", value: 9, color: "#7c5cff" },
      { name: "Waiting Patch", value: 6, color: "#6ea8fe" },
      { name: "Ready Close", value: 3, color: "#4dd0a8" },
    ],
    rows: [
      { module: "Speech Engine", owner: "Vendor", severity: "P1", aging: "28 天", status: "外部依赖" },
      { module: "Digital Key", owner: "Mobile", severity: "P1", aging: "21 天", status: "需升级" },
      { module: "Karaoke", owner: "3rd Party", severity: "P2", aging: "18 天", status: "等待补丁" },
      { module: "Festival Mode", owner: "Feature Team", severity: "P2", aging: "17 天", status: "重现中" },
      { module: "Map OTA", owner: "OTA", severity: "P3", aging: "15 天", status: "待验证" },
    ],
  },
  coverage: {
    title: "测试覆盖率分析",
    subtitle: "观察模块覆盖缺口、关键路径覆盖率和新增能力的测试准备度。",
    metrics: [
      { label: "总覆盖率", value: "82%", delta: "+4.6%", tone: "up" },
      { label: "关键路径覆盖", value: "91%", delta: "+1.8%", tone: "up" },
      { label: "低覆盖模块", value: "4", delta: "-2", tone: "down" },
      { label: "新增需求待补测", value: "13", delta: "需跟进", tone: "neutral" },
    ],
    trend: [
      { week: "W18", incoming: 58, resolved: 44 },
      { week: "W19", incoming: 64, resolved: 51 },
      { week: "W20", incoming: 72, resolved: 55 },
      { week: "W21", incoming: 68, resolved: 63 },
      { week: "W22", incoming: 74, resolved: 69 },
      { week: "W23", incoming: 79, resolved: 72 },
    ],
    statuses: [
      { name: "Core Flow", value: 91, color: "#4dd0a8" },
      { name: "Regression", value: 84, color: "#6ea8fe" },
      { name: "China Specific", value: 78, color: "#7c5cff" },
      { name: "Edge Cases", value: 61, color: "#ff8a65" },
    ],
    rows: [
      { module: "WeChat", owner: "QA CN", severity: "High", aging: "新增 8 项", status: "补测中" },
      { module: "Music", owner: "Media QA", severity: "Medium", aging: "新增 5 项", status: "已排期" },
      { module: "Voice", owner: "Speech QA", severity: "High", aging: "新增 7 项", status: "覆盖不足" },
      { module: "Map", owner: "Map QA", severity: "Low", aging: "新增 2 项", status: "稳定" },
      { module: "Account", owner: "Platform QA", severity: "Medium", aging: "新增 3 项", status: "待执行" },
    ],
  },
  "test-status": {
    title: "测试状态分析",
    subtitle: "查看执行进度、阻塞原因和通过率分布，辅助每日推进节奏。",
    metrics: [
      { label: "执行用例", value: "1,248", delta: "+9.2%", tone: "up" },
      { label: "通过率", value: "88%", delta: "+1.5%", tone: "up" },
      { label: "阻塞用例", value: "46", delta: "-9", tone: "down" },
      { label: "待执行", value: "114", delta: "本周目标 80", tone: "neutral" },
    ],
    trend: [
      { week: "W18", incoming: 142, resolved: 118 },
      { week: "W19", incoming: 165, resolved: 134 },
      { week: "W20", incoming: 171, resolved: 139 },
      { week: "W21", incoming: 188, resolved: 166 },
      { week: "W22", incoming: 195, resolved: 181 },
      { week: "W23", incoming: 201, resolved: 194 },
    ],
    statuses: [
      { name: "Passed", value: 88, color: "#4dd0a8" },
      { name: "Failed", value: 7, color: "#ff8a65" },
      { name: "Blocked", value: 3, color: "#7c5cff" },
      { name: "Not Run", value: 12, color: "#6ea8fe" },
    ],
    rows: [
      { module: "Login Flow", owner: "QA 1", severity: "High", aging: "今日", status: "通过" },
      { module: "Music Resume", owner: "QA 2", severity: "Medium", aging: "今日", status: "失败" },
      { module: "Navigation", owner: "QA 3", severity: "Medium", aging: "昨日", status: "阻塞" },
      { module: "Voice Wakeup", owner: "QA 4", severity: "High", aging: "昨日", status: "通过" },
      { module: "Mini Program", owner: "QA 5", severity: "Low", aging: "今日", status: "待执行" },
    ],
  },
};
