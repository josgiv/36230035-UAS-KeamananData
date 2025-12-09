"use client"

import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield, Activity, AlertTriangle, CheckCircle, Terminal, RefreshCw,
  Server, Zap, Lock, Globe, Cpu, Radio, AlertOctagon, FileText,
  User, Database, Network, Key
} from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts'
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
  Tabs, TabsContent, TabsList, TabsTrigger,
  Badge, Button, Separator,
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/primitives"

// --- TYPES ---
interface Prediction {
  prediction_class: "Benign" | "DDoS" | "Brute Force" | "Other"
  confidence: number
  threat_type: string
  response_mode: string
  mitigation_actions: string[]
  timestamp: string
  input_summary: string
  prediction_id: number
}

interface ActionLog {
  id: string
  type: "BLOCK" | "ISOLATE" | "THROTTLE" | "TRACE" | "LOCK" | "QUARANTINE"
  threatSource: string
  target: string
  status: "PENDING" | "EXECUTED"
  timestamp: Date
  details: string
  category: "NETWORK" | "ENDPOINT" | "IDENTITY"
}

// --- CONSTANTS ---
const API_URL = "http://localhost:8000"
const REFRESH_RATE = 2000

const COLORS = {
  Benign: "#10B981",
  DDoS: "#EF4444",
  "Brute Force": "#F59E0B",
  Other: "#8B5CF6",
}

// --- MOCK DATA GENERATORS ---
const MOCK_IPS = ["192.168.1.105", "10.0.5.22", "203.114.12.5", "172.16.0.44", "45.33.22.11", "88.99.100.50", "12.34.56.78", "77.88.99.10"]
const MOCK_HASHES = ["e5d3...8a2f", "99a1...b2c3", "malware_win32.exe", "trojan_dropper.bat", "ransomware.dll", "keylogger_v2.exe", "backdoor.sh"]
const MOCK_USERS = ["admin_sys", "root", "user_service", "database_admin", "guest_wifi", "backup_operator", "web_service", "ftp_admin"]
const MOCK_PORTS = ["22", "443", "3389", "8080", "21", "3306", "5432", "27017"]

const ACTIONS = {
  NETWORK: [
    { type: "BLOCK", template: "Blocking source IP {target} via firewall rule #442" },
    { type: "THROTTLE", template: "Applying QoS limit (10kbps) on flow from {target}" },
    { type: "BLOCK", template: "Adding {target} to IP blacklist (24h TTL)" },
    { type: "THROTTLE", template: "Rate limiting connections from {target} to 5/min" },
    { type: "BLOCK", template: "Dropping all packets from {target} on port 443" },
    { type: "TRACE", template: "Capturing packet dump for traffic from {target}" },
  ],
  ENDPOINT: [
    { type: "QUARANTINE", template: "Isolating file hash {target} to Sandbox" },
    { type: "TRACE", template: "Tracing process origin for {target}" },
    { type: "QUARANTINE", template: "Moving {target} to quarantine zone" },
    { type: "BLOCK", template: "Killing process associated with {target}" },
    { type: "TRACE", template: "Analyzing memory dump for {target}" },
    { type: "QUARANTINE", template: "Preventing execution of {target} system-wide" },
  ],
  IDENTITY: [
    { type: "LOCK", template: "Locking account {target} due to repeated failures" },
    { type: "ISOLATE", template: "Terminating active sessions for {target}" },
  ]
} as const;

export default function Dashboard() {
  const [history, setHistory] = useState<Prediction[]>([])
  const [actionLog, setActionLog] = useState<ActionLog[]>([])
  const [health, setHealth] = useState({ status: "unknown", model_loaded: false })
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const seenPredictionIds = useRef<Set<number>>(new Set())

  // --- DATA FETCHING ---
  const fetchData = async () => {
    try {
      const resHistory = await fetch(`${API_URL}/history`)
      if (resHistory.ok) {
        const data: Prediction[] = await resHistory.json()

        data.forEach(prediction => {
          if (
            !seenPredictionIds.current.has(prediction.prediction_id) &&
            prediction.prediction_class !== "Benign"
          ) {
            triggerRandomAction(prediction.prediction_class)
            seenPredictionIds.current.add(prediction.prediction_id)
          }
        })
        data.forEach(p => seenPredictionIds.current.add(p.prediction_id))
        setHistory(data)
      }

      const resHealth = await fetch(`${API_URL}/health`)
      if (resHealth.ok) {
        setHealth(await resHealth.json())
      }
    } catch (error) {
      console.error("Fetch error:", error)
      setHealth({ status: "disconnected", model_loaded: false })
    } finally {
      setLoading(false)
    }
  }

  // --- ACTION SIMULATION ---
  const triggerRandomAction = (threatType: string) => {
    const newActions: ActionLog[] = []
    const numActions = Math.floor(Math.random() * 3) + 2 // 2-4 actions per threat
    const categories: ("NETWORK" | "ENDPOINT" | "IDENTITY")[] = ["NETWORK", "ENDPOINT", "IDENTITY"]

    for (let i = 0; i < numActions; i++) {
      let category: "NETWORK" | "ENDPOINT" | "IDENTITY"
      let target: string

      // Assign category based on threat type but also add cross-category actions
      if (i === 0) {
        // First action matches threat type
        if (threatType === "DDoS") {
          category = "NETWORK"
          target = MOCK_IPS[Math.floor(Math.random() * MOCK_IPS.length)]
        } else if (threatType === "Brute Force") {
          category = "IDENTITY"
          target = MOCK_USERS[Math.floor(Math.random() * MOCK_USERS.length)]
        } else {
          category = "ENDPOINT"
          target = MOCK_HASHES[Math.floor(Math.random() * MOCK_HASHES.length)]
        }
      } else {
        // Subsequent actions can be any category
        category = categories[Math.floor(Math.random() * categories.length)]
        if (category === "NETWORK") {
          target = MOCK_IPS[Math.floor(Math.random() * MOCK_IPS.length)]
        } else if (category === "IDENTITY") {
          target = MOCK_USERS[Math.floor(Math.random() * MOCK_USERS.length)]
        } else {
          target = MOCK_HASHES[Math.floor(Math.random() * MOCK_HASHES.length)]
        }
      }

      const actionTemplate = ACTIONS[category][Math.floor(Math.random() * ACTIONS[category].length)]

      newActions.push({
        id: crypto.randomUUID(),
        type: actionTemplate.type as ActionLog["type"],
        threatSource: threatType,
        target: target,
        status: "EXECUTED",
        timestamp: new Date(Date.now() + i * 100), // Slight time offset
        details: actionTemplate.template.replace("{target}", target),
        category: category
      })
    }

    setActionLog(prev => [...newActions, ...prev].slice(0, 100))
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(() => {
      if (autoRefresh) fetchData()
    }, REFRESH_RATE)
    return () => clearInterval(interval)
  }, [autoRefresh])

  // --- DERIVED METRICS ---
  const totalPkts = history.length
  const benignCount = history.filter(p => p.prediction_class === "Benign").length
  const ddosCount = history.filter(p => p.prediction_class === "DDoS").length
  const bruteForceCount = history.filter(p => p.prediction_class === "Brute Force").length
  const otherCount = history.filter(p => p.prediction_class === "Other").length
  const threatCount = totalPkts - benignCount
  const threatRate = totalPkts > 0 ? (threatCount / totalPkts) * 100 : 0

  const sortedHistory = [...history].reverse()
  const newestItem = sortedHistory[0]
  const isOk = health.status === "healthy"
  const systemStatus = newestItem?.prediction_class === "Benign" || !newestItem ? "SECURE" : "CRITICAL"

  // Chart Data
  const confidenceData = history.slice(0, 50).map((h, i) => ({
    name: i,
    confidence: h.confidence
  })).reverse()

  const pieData = [
    { name: 'Benign', value: benignCount },
    { name: 'DDoS', value: ddosCount },
    { name: 'Brute Force', value: bruteForceCount },
    { name: 'Other', value: otherCount },
  ].filter(d => d.value > 0)

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans">
      {/* IDENTITY HEADER */}
      <div className="bg-slate-900 border-b border-slate-800 py-2 px-6 flex justify-between items-center text-[10px] font-mono text-slate-400">
        <div className="flex gap-4">
          <span className="text-cyan-400 font-bold">NAMA: JOSIA GIVEN SANTOSO</span>
          <span>|</span>
          <span className="text-emerald-400 font-bold">NIM: 36230035</span>
        </div>
        <div className="flex gap-4">
          <span>DOSEN: ALANIAH NISRINA, B.ENG., M.ENG.</span>
          <span>|</span>
          <span>MK: KEAMANAN DATA</span>
        </div>
      </div>

      <div className="p-6">
        {/* HEADER */}
        <header className="flex justify-between items-center mb-8 bg-slate-900/50 p-6 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur-xl">
          <div className="flex items-center gap-4">
            <div className={`p-3 rounded-full ${isOk ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
              <Shield className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
                SHIELDGUARD SOC
              </h1>
              <p className="text-slate-400 text-sm">Advanced Network Intrusion Detection System</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end mr-4">
              <span className="text-xs text-slate-500 uppercase tracking-widest font-semibold">System Status</span>
              <div className={`flex items-center gap-2 font-bold text-xl ${systemStatus === "SECURE" ? "text-emerald-400" : "text-rose-500 animate-pulse"}`}>
                {systemStatus === "SECURE" ? <Lock className="w-5 h-5" /> : <AlertOctagon className="w-5 h-5" />}
                {systemStatus}
              </div>
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`${autoRefresh ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400' : 'bg-slate-800 border-slate-700'}`}
            >
              <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </header>

        {/* METRICS GRID */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard title="Total Analyzed" value={totalPkts} icon={<Server className="w-5 h-5 text-blue-400" />} />
          <MetricCard title="Benign Traffic" value={benignCount} icon={<CheckCircle className="w-5 h-5 text-emerald-400" />} />
          <MetricCard title="Threat Detected" value={threatCount} icon={<AlertTriangle className="w-5 h-5 text-rose-400" />} alert={threatCount > 0} />
          <MetricCard title="Threat Rate" value={`${threatRate.toFixed(1)}%`} icon={<Activity className="w-5 h-5 text-violet-400" />} />
        </div>

        {/* MAIN CONTENT */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* LEFT: CHARTS */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            {/* CONFIDENCE CHART */}
            <Card className="bg-slate-900/50 border-slate-800 shadow-xl backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-400" /> Confidence Trend
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[250px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={confidenceData}>
                      <defs>
                        <linearGradient id="colorConf" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="name" hide />
                      <YAxis domain={[0, 1.2]} hide />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }} />
                      <Area type="monotone" dataKey="confidence" stroke="#3B82F6" fillOpacity={1} fill="url(#colorConf)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* LIVE TRAFFIC LOG */}
            <Card className="bg-slate-900/50 border-slate-800 shadow-xl backdrop-blur-sm flex-1">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-slate-400" /> Live Traffic Log
                </CardTitle>
                <CardDescription>Recent packets analyzed by the XGBoost Engine</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px] overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-slate-800 hover:bg-slate-800/50">
                        <TableHead className="text-slate-400">Timestamp</TableHead>
                        <TableHead className="text-slate-400">Class</TableHead>
                        <TableHead className="text-slate-400">Confidence</TableHead>
                        <TableHead className="text-slate-400">Summary</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <AnimatePresence>
                        {sortedHistory.slice(0, 10).map((item, i) => (
                          <motion.tr
                            key={`traffic-${item.prediction_id}-${item.timestamp}-${i}`}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="border-slate-800 hover:bg-slate-800/30 transition-colors"
                          >
                            <TableCell className="font-mono text-xs text-slate-500">
                              {new Date(item.timestamp).toLocaleTimeString()}
                            </TableCell>
                            <TableCell>
                              <Badge
                                variant={item.prediction_class === 'Benign' ? 'default' : 'destructive'}
                                className="uppercase text-[10px] tracking-wider"
                                style={{
                                  backgroundColor: COLORS[item.prediction_class] + '20',
                                  color: COLORS[item.prediction_class],
                                  borderColor: COLORS[item.prediction_class] + '50'
                                }}
                              >
                                {item.prediction_class}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <div className="h-1.5 w-16 bg-slate-700 rounded-full overflow-hidden">
                                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${item.confidence * 100}%` }}></div>
                                </div>
                                <span className="text-xs">{(item.confidence * 100).toFixed(0)}%</span>
                              </div>
                            </TableCell>
                            <TableCell className="text-xs text-slate-300 max-w-[200px] truncate">
                              {item.input_summary}
                            </TableCell>
                          </motion.tr>
                        ))}
                      </AnimatePresence>
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* RIGHT: DISTRIBUTION & ALERTS */}
          <div className="flex flex-col gap-6">
            {/* PIE CHART */}
            <Card className="bg-slate-900/50 border-slate-800 shadow-xl backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white text-lg">Traffic Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[200px] w-full grid grid-cols-2 items-center">
                  <div className="h-full w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={70}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || "#fff"} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex flex-col gap-2 text-xs">
                    {pieData.map(d => (
                      <div key={d.name} className="flex items-center gap-2 text-slate-300">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[d.name as keyof typeof COLORS] }}></div>
                        <span className="font-medium">{d.name}:</span>
                        <span className="text-white font-bold">{d.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ACTIVE MITIGATION */}
            <Card className={`border shadow-2xl transition-all duration-300 ${systemStatus !== "SECURE" ? 'bg-red-950/20 border-red-500/50 shadow-red-500/10' : 'bg-slate-900/50 border-slate-800'}`}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-white text-lg flex items-center gap-2">
                    <Zap className={`w-5 h-5 ${systemStatus !== "SECURE" ? 'text-red-500' : 'text-slate-500'}`} />
                    Active Mitigation
                  </CardTitle>
                  {systemStatus !== "SECURE" && <Badge variant="destructive" className="animate-pulse">ACTIVE</Badge>}
                </div>
              </CardHeader>
              <CardContent>
                {newestItem && newestItem.prediction_class !== "Benign" ? (
                  <div className="space-y-4">
                    <div className="p-3 bg-red-500/10 rounded-lg border border-red-500/20">
                      <h4 className="text-red-400 font-bold mb-1">{newestItem.threat_type}</h4>
                      <p className="text-xs text-red-200/70 mb-2">Confidence: {(newestItem.confidence * 100).toFixed(1)}%</p>
                      <Separator className="bg-red-500/20 my-2" />
                      <div className="grid gap-2">
                        {newestItem.mitigation_actions?.slice(0, 3).map((action, i) => (
                          <div key={i} className="flex items-start gap-2 text-xs text-red-100">
                            <CheckCircle className="w-3 h-3 mt-0.5 text-red-500 flex-shrink-0" />
                            <span>{action}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-6 text-slate-500">
                    <Shield className="w-12 h-12 mb-2 opacity-20" />
                    <p className="text-sm font-medium">System Secure</p>
                    <p className="text-xs opacity-50">Monitoring active traffic</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* SOC OPERATIONS CENTER */}
        <Card className="bg-slate-900/50 border-slate-800 shadow-xl">
          <Tabs defaultValue="all" className="w-full">
            <CardHeader className="pb-0 border-b border-slate-800">
              <div className="flex items-center justify-between">
                <CardTitle className="text-white flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-cyan-400" />
                  Security Operations Center
                  <Badge variant="outline" className="ml-2 text-xs">{actionLog.length} Events</Badge>
                </CardTitle>
                <TabsList className="bg-slate-800/50">
                  <TabsTrigger value="all" className="data-[state=active]:bg-slate-500/20 data-[state=active]:text-white">
                    <Activity className="w-4 h-4 mr-2" /> All
                  </TabsTrigger>
                  <TabsTrigger value="network" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
                    <Network className="w-4 h-4 mr-2" /> Network
                  </TabsTrigger>
                  <TabsTrigger value="endpoint" className="data-[state=active]:bg-purple-500/20 data-[state=active]:text-purple-400">
                    <Database className="w-4 h-4 mr-2" /> Endpoint
                  </TabsTrigger>
                  <TabsTrigger value="identity" className="data-[state=active]:bg-amber-500/20 data-[state=active]:text-amber-400">
                    <User className="w-4 h-4 mr-2" /> Identity
                  </TabsTrigger>
                </TabsList>
              </div>
            </CardHeader>

            <CardContent className="p-0">
              <TabsContent value="all" className="m-0 min-h-[300px]">
                <ActionLogTable logs={actionLog} color="all" emptyMsg="No Security Events" showCategory />
              </TabsContent>
              <TabsContent value="network" className="m-0 min-h-[300px]">
                <ActionLogTable logs={actionLog.filter(l => l.category === 'NETWORK')} color="cyan" emptyMsg="No Network Events" />
              </TabsContent>
              <TabsContent value="endpoint" className="m-0 min-h-[300px]">
                <ActionLogTable logs={actionLog.filter(l => l.category === 'ENDPOINT')} color="purple" emptyMsg="No Endpoint Events" />
              </TabsContent>
              <TabsContent value="identity" className="m-0 min-h-[300px]">
                <ActionLogTable logs={actionLog.filter(l => l.category === 'IDENTITY')} color="amber" emptyMsg="No Identity Events" />
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>
      </div>
    </div>
  )
}

// --- METRIC CARD ---
function MetricCard({ title, value, icon, alert }: { title: string; value: string | number; icon: React.ReactNode; alert?: boolean }) {
  return (
    <Card className={`bg-slate-900/50 border-slate-800 backdrop-blur-sm ${alert ? 'ring-1 ring-red-500/50 bg-red-500/5' : ''}`}>
      <CardContent className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-slate-400 text-sm font-medium mb-1">{title}</p>
            <h3 className="text-2xl font-bold text-white">{value}</h3>
          </div>
          <div className="p-2 bg-slate-800/50 rounded-lg">{icon}</div>
        </div>
      </CardContent>
    </Card>
  )
}

// --- ACTION LOG TABLE ---
function ActionLogTable({ logs, color, emptyMsg, showCategory = false }: { logs: ActionLog[]; color: string; emptyMsg: string; showCategory?: boolean }) {
  const colorMap: Record<string, string> = {
    cyan: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
    purple: "text-purple-400 bg-purple-500/10 border-purple-500/30",
    amber: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    all: "text-slate-300 bg-slate-500/10 border-slate-500/30",
  }

  const categoryColorMap: Record<string, string> = {
    NETWORK: "text-cyan-400 bg-cyan-500/20",
    ENDPOINT: "text-purple-400 bg-purple-500/20",
    IDENTITY: "text-amber-400 bg-amber-500/20",
  }

  if (logs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[250px] text-slate-500">
        <CheckCircle className="w-12 h-12 mb-2 opacity-20" />
        <p className="text-sm">{emptyMsg}</p>
      </div>
    )
  }

  return (
    <div className="overflow-auto max-h-[350px]">
      <Table>
        <TableHeader className="bg-slate-900 sticky top-0">
          <TableRow className="border-slate-800">
            <TableHead className="text-slate-400 text-xs">TIME</TableHead>
            {showCategory && <TableHead className="text-slate-400 text-xs">CATEGORY</TableHead>}
            <TableHead className="text-slate-400 text-xs">TYPE</TableHead>
            <TableHead className="text-slate-400 text-xs">TARGET</TableHead>
            <TableHead className="text-slate-400 text-xs">DETAILS</TableHead>
            <TableHead className="text-slate-400 text-xs text-right">STATUS</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <AnimatePresence>
            {logs.map((log) => (
              <motion.tr
                key={log.id}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="border-slate-800"
              >
                <TableCell className="font-mono text-xs text-slate-400">
                  {log.timestamp.toLocaleTimeString()}
                </TableCell>
                {showCategory && (
                  <TableCell>
                    <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded ${categoryColorMap[log.category]}`}>
                      {log.category}
                    </span>
                  </TableCell>
                )}
                <TableCell>
                  <span className={`text-xs font-bold uppercase px-2 py-1 rounded border ${showCategory ? categoryColorMap[log.category] : colorMap[color]}`}>
                    {log.type}
                  </span>
                </TableCell>
                <TableCell>
                  <code className="text-xs bg-slate-800 px-2 py-1 rounded text-white">{log.target}</code>
                </TableCell>
                <TableCell className="text-xs text-slate-300 max-w-[300px] truncate">{log.details}</TableCell>
                <TableCell className="text-right">
                  <span className="text-xs font-bold text-emerald-400 flex items-center justify-end gap-1">
                    <CheckCircle className="w-3 h-3" /> {log.status}
                  </span>
                </TableCell>
              </motion.tr>
            ))}
          </AnimatePresence>
        </TableBody>
      </Table>
    </div>
  )
}
