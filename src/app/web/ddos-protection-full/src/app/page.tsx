"use client"

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Activity, AlertTriangle, CheckCircle, Terminal, RefreshCw, Server, Zap } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Badge, Button, Separator, Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/primitives"

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

// --- CONSTANTS ---
const API_URL = "http://localhost:8000"
const REFRESH_RATE = 2000 // 2 seconds

// --- COLORS ---
const COLORS = {
  Benign: "#10B981", // Emerald 500
  DDoS: "#EF4444",   // Red 500
  "Brute Force": "#F59E0B", // Amber 500
  Other: "#8B5CF6", // Violet 500
}

export default function Dashboard() {
  const [history, setHistory] = useState<Prediction[]>([])
  const [health, setHealth] = useState({ status: "unknown", model_loaded: false })
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const fetchData = async () => {
    try {
      // Fetch History
      const resHistory = await fetch(`${API_URL}/history`)
      if (resHistory.ok) {
        const data = await resHistory.json()
        setHistory(data)
      }
      // Fetch Health
      const resHealth = await fetch(`${API_URL}/health`)
      if (resHealth.ok) {
        const data = await resHealth.json()
        setHealth(data)
      }
    } catch (error) {
      console.error("Failed to fetch data:", error)
      setHealth({ status: "disconnected", model_loaded: false })
    } finally {
      setLoading(false)
    }
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
  const threatCount = totalPkts - benignCount
  const threatRate = totalPkts > 0 ? (threatCount / totalPkts) * 100 : 0

  const sortedHistory = [...history].reverse()
  const newestItem = sortedHistory[0]

  const isOk = health.status === "healthy"
  const systemStatus = newestItem?.prediction_class === "Benign" || !newestItem ? "SAFE" : "UNDER ATTACK"

  // Chart Data prep
  const pieData = [
    { name: 'Benign', value: benignCount },
    { name: 'DDoS', value: history.filter(p => p.prediction_class === 'DDoS').length },
    { name: 'Brute Force', value: history.filter(p => p.prediction_class === 'Brute Force').length },
    { name: 'Other', value: history.filter(p => p.prediction_class === 'Other').length },
  ].filter(d => d.value > 0)

  // Confidence Histogram (simplified logic for demo)
  const confidenceData = history.map((h, i) => ({
    name: i,
    confidence: h.confidence
  }))

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 font-sans">
      {/* HEADER */}
      <header className="flex justify-between items-center mb-8 bg-slate-900/50 p-6 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur-xl">
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-full ${isOk ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
            <Shield className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              ShieldGuard AI
            </h1>
            <p className="text-slate-400 text-sm">Advanced Network Intrusion Detection System</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex flex-col items-end mr-4">
            <span className="text-xs text-slate-500 uppercase tracking-widest font-semibold">System Status</span>
            <div className={`flex items-center gap-2 font-bold ${systemStatus === "SAFE" ? "text-emerald-400" : "text-rose-500 animate-pulse"}`}>
              {systemStatus === "SAFE" ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
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
        <MetricCard
          title="Total Analyzed"
          value={totalPkts}
          icon={<Server className="w-5 h-5 text-blue-400" />}
          trend="+12%" // Dummy trend for visuals
        />
        <MetricCard
          title="Benign Traffic"
          value={benignCount}
          icon={<CheckCircle className="w-5 h-5 text-emerald-400" />}
        />
        <MetricCard
          title="Threat Detected"
          value={threatCount}
          icon={<AlertTriangle className="w-5 h-5 text-rose-400" />}
          alert={threatCount > 0}
        />
        <MetricCard
          title="Threat Rate"
          value={`${threatRate.toFixed(1)}%`}
          icon={<Activity className="w-5 h-5 text-violet-400" />}
        />
      </div>

      {/* MAIN CONTENT ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">

        {/* LEFT COL - CHARTS */}
        <div className="lg:col-span-2 flex flex-col gap-6">
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
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                    />
                    <Area type="monotone" dataKey="confidence" stroke="#3B82F6" fillOpacity={1} fill="url(#colorConf)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* TABLE */}
          <Card className="bg-slate-900/50 border-slate-800 shadow-xl backdrop-blur-sm flex-1">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Terminal className="w-5 h-5 text-slate-400" /> Live Traffic Log
              </CardTitle>
              <CardDescription>Recent packets analyzed by the XGBoost Engine</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px] overflow-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-slate-800 hover:bg-slate-800/50">
                      <TableHead className="text-slate-400">Timestamp</TableHead>
                      <TableHead className="text-slate-400">Class</TableHead>
                      <TableHead className="text-slate-400">Confidence</TableHead>
                      <TableHead className="text-slate-400">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <AnimatePresence>
                      {sortedHistory.slice(0, 15).map((item, i) => (
                        <motion.tr
                          key={i} // Use unique ID in real app
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          className="border-slate-800 hover:bg-slate-800/30 transition-colors"
                        >
                          <TableCell className="font-mono text-xs text-slate-500">
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={item.prediction_class === 'Benign' ? 'success' : item.prediction_class === 'DDoS' ? 'destructive' : 'warning'}
                              className="uppercase text-[10px] tracking-wider"
                            >
                              {item.prediction_class}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <div className="h-1.5 w-16 bg-slate-700 rounded-full overflow-hidden">
                                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${item.confidence * 100}%` }}></div>
                              </div>
                              <span className="text-xs">{item.confidence.toFixed(2)}</span>
                            </div>
                          </TableCell>
                          <TableCell className="text-xs text-slate-300">
                            {item.input_summary.slice(0, 20)}...
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

        {/* RIGHT COL - STATS & ALERTS */}
        <div className="flex flex-col gap-6">
          <Card className="bg-slate-900/50 border-slate-800 shadow-xl backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-white text-lg">Distribution</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <div className="h-[200px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
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
              <div className="flex flex-col justify-center gap-2 text-xs ml-4">
                {pieData.map(d => (
                  <div key={d.name} className="flex items-center gap-2 text-slate-300">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[d.name as keyof typeof COLORS] }}></div>
                    {d.name}: {d.value}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* LATEST ALERT CARD */}
          <Card className={`border shadow-2xl transition-all duration-300 ${systemStatus !== "SAFE" ? 'bg-red-950/20 border-red-500/50 shadow-red-500/10' : 'bg-slate-900/50 border-slate-800'}`}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white text-lg flex items-center gap-2">
                  <Zap className={`w-5 h-5 ${systemStatus !== "SAFE" ? 'text-red-500' : 'text-slate-500'}`} />
                  Active Mitigation
                </CardTitle>
                {systemStatus !== "SAFE" && <Badge variant="destructive" className="animate-pulse">ACTION REQUIRED</Badge>}
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
                      {newestItem.mitigation_actions.map((action, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-red-100">
                          <CheckCircle className="w-3 h-3 mt-0.5 text-red-500" />
                          {action}
                        </div>
                      ))}
                    </div>
                  </div>
                  <Button className="w-full bg-red-600 hover:bg-red-700 text-white border-none">
                    Initiate Manual Override
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-8 text-slate-500">
                  <Shield className="w-12 h-12 mb-2 opacity-20" />
                  <p className="text-sm">System Secure</p>
                  <p className="text-xs opacity-50">Monitoring active traffic flows</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  )
}

function MetricCard({ title, value, icon, trend, alert }: any) {
  return (
    <Card className={`bg-slate-900/50 border-slate-800 backdrop-blur-sm ${alert ? 'ring-1 ring-red-500/50 bg-red-500/5' : ''}`}>
      <CardContent className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-slate-400 text-sm font-medium mb-1">{title}</p>
            <h3 className="text-2xl font-bold text-white">{value}</h3>
          </div>
          <div className="p-2 bg-slate-800/50 rounded-lg">
            {icon}
          </div>
        </div>
        {trend && (
          <div className="mt-4 flex items-center text-xs text-emerald-400">
            <span className="font-bold mr-1">{trend}</span> since last hour
          </div>
        )}
      </CardContent>
    </Card>
  )
}
