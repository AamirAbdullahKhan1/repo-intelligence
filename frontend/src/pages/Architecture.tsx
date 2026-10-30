import { useState, useMemo, useCallback } from 'react'
import { Link } from 'react-router-dom'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Position,
  Handle,
  type Node,
  type Edge,
} from 'reactflow'
import 'reactflow/dist/style.css'
import {
  Network,
  Server,
  Database,
  Lock,
  Globe,
  Container,
  FileCode,
  CheckCircle2,
  Sparkles,
  Info,
  X,
  Search,
  Bot,
  Zap,
  ArrowRight,
  GitCommit,
  SlidersHorizontal,
  ChevronRight,
  Cpu,
} from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { EmptyState } from '../components/EmptyState'
import { useAnalysis } from '../context/AnalysisContext'
import type { ArchitectureEdge, ArchitectureNode } from '../types'

// ── Node Visual Configs ────────────────────────────────────────────────────────

const NODE_CONFIGS: Record<
  string,
  { icon: any; border: string; bg: string; text: string; badge: string }
> = {
  client: {
    icon: Globe,
    border: 'border-sky-500/50',
    bg: 'bg-sky-950/40',
    text: 'text-sky-400',
    badge: 'badge-blue',
  },
  frontend_app: {
    icon: Globe,
    border: 'border-cyan-500/60',
    bg: 'bg-cyan-950/50',
    text: 'text-cyan-400',
    badge: 'badge-blue',
  },
  api_service: {
    icon: Server,
    border: 'border-brand-500/60',
    bg: 'bg-brand-950/50',
    text: 'text-brand-400',
    badge: 'badge-blue',
  },
  mcp_server: {
    icon: Bot,
    border: 'border-violet-500/60',
    bg: 'bg-violet-950/50',
    text: 'text-violet-400',
    badge: 'bg-violet-500/20 text-violet-300 border-violet-500/40',
  },
  worker: {
    icon: Zap,
    border: 'border-amber-500/60',
    bg: 'bg-amber-950/50',
    text: 'text-amber-400',
    badge: 'badge-yellow',
  },
  cache: {
    icon: Cpu,
    border: 'border-emerald-500/60',
    bg: 'bg-emerald-950/50',
    text: 'text-emerald-400',
    badge: 'badge-green',
  },
  database: {
    icon: Database,
    border: 'border-emerald-500/60',
    bg: 'bg-emerald-950/50',
    text: 'text-emerald-400',
    badge: 'badge-green',
  },
  auth: {
    icon: Lock,
    border: 'border-amber-500/50',
    bg: 'bg-amber-950/40',
    text: 'text-amber-400',
    badge: 'badge-yellow',
  },
  infrastructure: {
    icon: Container,
    border: 'border-purple-500/50',
    bg: 'bg-purple-950/40',
    text: 'text-purple-400',
    badge: 'bg-purple-500/20 text-purple-300 border-purple-500/40',
  },
  shared_library: {
    icon: FileCode,
    border: 'border-slate-500/50',
    bg: 'bg-slate-900/60',
    text: 'text-slate-400',
    badge: 'badge-gray',
  },
}

// ── Custom React Flow Node Component ──────────────────────────────────────────

function CustomNode({ data }: { data: ArchitectureNode }) {
  const cfg = NODE_CONFIGS[data.type] || NODE_CONFIGS.api_service
  const Icon = cfg.icon

  return (
    <div
      className={`px-4 py-3 rounded-xl border shadow-xl backdrop-blur-md transition-all duration-150 min-w-[210px] max-w-[270px] text-left cursor-pointer hover:scale-[1.02] ${cfg.border} ${cfg.bg}`}
    >
      <Handle type="target" position={Position.Left} className="!bg-surface-400 !w-2.5 !h-2.5" />
      <div className="flex items-start gap-2.5">
        <div className="p-2 rounded-lg bg-surface-800/90 border border-surface-600/60 flex-shrink-0">
          <Icon className={`w-4 h-4 ${cfg.text}`} />
        </div>
        <div className="overflow-hidden flex-1">
          <p className="text-xs font-semibold text-gray-100 truncate">{data.label}</p>
          {data.technology && (
            <p className="text-[10px] text-gray-400 truncate mt-0.5">{data.technology}</p>
          )}

          <div className="flex flex-wrap items-center gap-1.5 mt-2">
            <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono border ${cfg.badge}`}>
              {data.type.replace('_', ' ')}
            </span>
            <span
              className={`text-[9px] px-1.5 py-0.5 rounded font-mono ${
                data.confidence === 'VERIFIED'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'bg-surface-700 text-gray-400'
              }`}
            >
              {data.confidence}
            </span>
          </div>

          {data.sub_modules && data.sub_modules.length > 0 && (
            <p className="text-[10px] text-gray-400 mt-1.5 truncate">
              {data.sub_modules.length} sub-module(s): {data.sub_modules[0]}
            </p>
          )}
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-brand-500 !w-2.5 !h-2.5" />
    </div>
  )
}

const nodeTypes = { custom: CustomNode }

export function Architecture() {
  const { architecture, inventory } = useAnalysis()

  // View state
  const [activeView, setActiveView] = useState<'runtime' | 'deployment'>('runtime')
  const [level, setLevel] = useState<1 | 2>(1) // Level 1: System Overview, Level 2: Component View
  const [filterType, setFilterType] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedNode, setSelectedNode] = useState<ArchitectureNode | null>(null)
  const [selectedEdge, setSelectedEdge] = useState<ArchitectureEdge | null>(null)

  // Determine active dataset based on view
  const currentNodesData = useMemo(() => {
    if (!architecture) return []
    if (activeView === 'deployment') {
      return architecture.deployment_view?.nodes || []
    }
    // Runtime view: filter by level & category
    return architecture.nodes.filter((n) => {
      if (level === 1 && n.level === 2) return false
      if (filterType !== 'all' && n.type !== filterType) return false
      if (
        searchQuery &&
        !n.label.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !(n.technology || '').toLowerCase().includes(searchQuery.toLowerCase())
      ) {
        return false
      }
      return true
    })
  }, [architecture, activeView, level, filterType, searchQuery])

  const currentEdgesData = useMemo(() => {
    if (!architecture) return []
    if (activeView === 'deployment') {
      return architecture.deployment_view?.edges || []
    }
    return architecture.edges
  }, [architecture, activeView])

  // Compute Layout for Nodes
  const initialNodes: Node[] = useMemo(() => {
    if (activeView === 'deployment') {
      return currentNodesData.map((node, idx) => ({
        id: node.id,
        type: 'custom',
        position: { x: 80 + idx * 280, y: 180 },
        data: node,
      }))
    }

    // Runtime multi-layer layout
    let workerIdx = 0
    let dbIdx = 0
    let serverIdx = 0

    return currentNodesData.map((node) => {
      let x = 380
      let y = 180

      if (node.type === 'client') {
        x = 40
        y = 180
      } else if (node.type === 'frontend_app') {
        x = 340
        y = 120
      } else if (node.type === 'mcp_server') {
        x = 340
        y = 320
      } else if (node.type === 'worker') {
        x = 680
        y = 70 + workerIdx * 130
        workerIdx++
      } else if (node.type in ['database', 'cache']) {
        x = 1020
        y = 160 + dbIdx * 140
        dbIdx++
      } else if (node.type === 'auth') {
        x = 680
        y = 360
      } else if (node.type === 'api_service') {
        x = 340
        y = 480 + serverIdx * 120
        serverIdx++
      } else if (node.level === 2) {
        x = 520
        y = 100 + Math.random() * 300
      }

      return {
        id: node.id,
        type: 'custom',
        position: { x, y },
        data: node,
      }
    })
  }, [currentNodesData, activeView])

  // Compute React Flow Edges
  const initialEdges: Edge[] = useMemo(() => {
    return currentEdgesData.map((edge) => {
      let strokeColor = '#6366f1' // default indigo
      if (edge.relationship_type === 'READS_FROM') strokeColor = '#10b981' // emerald
      if (edge.relationship_type === 'WRITES_TO') strokeColor = '#f59e0b' // amber
      if (edge.relationship_type === 'HANDLES_ROUTE') strokeColor = '#06b6d4' // cyan
      if (edge.relationship_type === 'TRIGGERS_WORKFLOW') strokeColor = '#a855f7' // purple
      if (edge.relationship_type === 'DEPLOYED_AS') strokeColor = '#3b82f6' // blue

      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: `${edge.relationship_type}: ${edge.label}`,
        animated: edge.relationship_type in ['HANDLES_ROUTE', 'TRIGGERS_WORKFLOW', 'READS_FROM', 'WRITES_TO'],
        style: { stroke: strokeColor, strokeWidth: 1.8 },
        labelStyle: { fill: '#cbd5e1', fontSize: 10, fontWeight: 600 },
        labelBgStyle: { fill: '#0f172a', fillOpacity: 0.9, rx: 4, ry: 4 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
        },
        data: edge,
      }
    })
  }, [currentEdgesData])

  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  const onNodeClick = useCallback((_: any, node: Node) => {
    setSelectedEdge(null)
    setSelectedNode(node.data as ArchitectureNode)
  }, [])

  const onEdgeClick = useCallback((_: any, edge: Edge) => {
    setSelectedNode(null)
    if (edge.data) {
      setSelectedEdge(edge.data as ArchitectureEdge)
    }
  }, [])

  if (!architecture || !inventory) {
    return (
      <div className="px-6 py-6 max-w-5xl mx-auto space-y-6">
        <PageHeader
          title="Architecture Map"
          description="Interactive multi-layer architecture graph extracted from code evidence."
          badge={<span className="badge badge-blue">Reconstruction Engine V2</span>}
        />
        <div className="card min-h-96 flex flex-col items-center justify-center">
          <EmptyState
            icon={Network}
            title="No Architecture Model"
            description="Enter a public GitHub URL or upload a repository archive on the Overview dashboard to reconstruct its multi-layer architecture."
          />
          <Link to="/overview" className="btn-primary mt-4">
            <Search className="w-4 h-4" />
            Go to Overview & Analyse
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="px-6 py-6 max-w-7xl mx-auto space-y-5">
      <PageHeader
        title={`Architecture Map — ${architecture.repo_name}`}
        description="Multi-layer component reconstruction distinguishing runtime applications from deployment architecture."
        badge={
          architecture.llm_enhanced ? (
            <span className="badge badge-green flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              LLM Enhanced ({architecture.model_used})
            </span>
          ) : (
            <span className="badge badge-blue flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              Verified Code Evidence
            </span>
          )
        }
      />

      {/* Control Toolbar */}
      <div className="card p-3 flex flex-wrap items-center justify-between gap-3">
        {/* Left: View Mode Toggle */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-gray-400">View:</span>
          <div className="flex rounded-lg bg-surface-700 p-1">
            <button
              onClick={() => {
                setActiveView('runtime')
                setSelectedNode(null)
                setSelectedEdge(null)
              }}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                activeView === 'runtime'
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <Network className="w-3.5 h-3.5" />
              Runtime Architecture
            </button>
            <button
              onClick={() => {
                setActiveView('deployment')
                setSelectedNode(null)
                setSelectedEdge(null)
              }}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                activeView === 'deployment'
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <GitCommit className="w-3.5 h-3.5" />
              Deployment & CI/CD
            </button>
          </div>
        </div>

        {/* Center: Level & Filter Controls (only in Runtime view) */}
        {activeView === 'runtime' && (
          <div className="flex flex-wrap items-center gap-3">
            {/* Level Toggle */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-gray-400">Level:</span>
              <div className="flex rounded bg-surface-700 p-0.5 border border-surface-600">
                <button
                  onClick={() => setLevel(1)}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                    level === 1 ? 'bg-surface-500 text-white' : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  L1: System
                </button>
                <button
                  onClick={() => setLevel(2)}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                    level === 2 ? 'bg-surface-500 text-white' : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  L2: Components
                </button>
              </div>
            </div>

            {/* Filter by Type */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-gray-400">Filter:</span>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="bg-surface-700 border border-surface-500 rounded px-2 py-1 text-xs text-gray-200 focus:outline-none"
              >
                <option value="all">All Components ({architecture.nodes.length})</option>
                <option value="frontend_app">Frontend Applications</option>
                <option value="mcp_server">MCP Protocol Servers</option>
                <option value="worker">Background Workers</option>
                <option value="database">Databases & Caches</option>
              </select>
            </div>

            {/* Search */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-gray-400 absolute left-2.5 top-2" />
              <input
                type="text"
                placeholder="Search components..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-surface-700 border border-surface-500 rounded pl-8 pr-2 py-0.5 text-xs text-gray-200 w-40 focus:w-48 transition-all focus:outline-none"
              />
            </div>
          </div>
        )}

        {/* Right: Legend Toggle indicator */}
        <div className="text-xs text-gray-400 font-mono">
          {activeView === 'runtime' ? `${currentNodesData.length} nodes · ${currentEdgesData.length} edges` : 'Pipeline stages: ' + (architecture.deployment_view?.pipeline_stages?.length || 0)}
        </div>
      </div>

      {/* Main Graph Canvas */}
      <div className="card p-0 overflow-hidden relative border border-surface-600 rounded-xl h-[560px] bg-surface-900">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onEdgeClick={onEdgeClick}
          fitView
          attributionPosition="bottom-left"
        >
          <Background color="#334155" gap={18} size={1} />
          <Controls className="!bg-surface-800 !border-surface-600 !text-gray-200" />
          <MiniMap
            nodeColor={(n) => {
              if (n.data?.type === 'mcp_server') return '#8b5cf6'
              if (n.data?.type === 'worker') return '#f59e0b'
              if (n.data?.type in ['database', 'cache']) return '#10b981'
              if (n.data?.type === 'frontend_app') return '#06b6d4'
              return '#6366f1'
            }}
            maskColor="rgba(15, 23, 42, 0.75)"
            className="!bg-surface-800 !border-surface-600 rounded-lg"
          />
        </ReactFlow>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="absolute top-4 right-4 w-84 bg-surface-800/95 backdrop-blur-md border border-surface-600 rounded-xl p-4 shadow-2xl z-10 space-y-3.5 max-h-[500px] overflow-y-auto">
            <div className="flex items-start justify-between">
              <div>
                <span className="badge badge-blue text-[10px] uppercase font-mono">
                  {selectedNode.type}
                </span>
                <h3 className="text-sm font-semibold text-gray-100 mt-1">
                  {selectedNode.label}
                </h3>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-gray-200 p-1"
                aria-label="Close component details"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-gray-300 leading-relaxed font-sans">
              {selectedNode.description}
            </p>

            {selectedNode.technology && (
              <div className="text-xs">
                <span className="text-gray-400 block text-[11px]">Technology</span>
                <span className="font-mono text-brand-300">{selectedNode.technology}</span>
              </div>
            )}

            <div className="text-xs">
              <span className="text-gray-400 block text-[11px] mb-1">Evidence Status</span>
              <span
                className={`badge ${
                  selectedNode.confidence === 'VERIFIED' ? 'badge-green' : 'badge-gray'
                }`}
              >
                {selectedNode.confidence}
              </span>
            </div>

            {/* Sub-modules list */}
            {selectedNode.sub_modules && selectedNode.sub_modules.length > 0 && (
              <div className="text-xs pt-2 border-t border-surface-600">
                <span className="text-gray-400 block text-[11px] mb-1.5 flex items-center gap-1 font-semibold">
                  <SlidersHorizontal className="w-3.5 h-3.5" />
                  Sub-Modules & Handlers ({selectedNode.sub_modules.length})
                </span>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {selectedNode.sub_modules.map((sm, i) => (
                    <div
                      key={i}
                      className="font-mono text-[11px] text-gray-300 bg-surface-700/60 px-2 py-1 rounded truncate"
                      title={sm}
                    >
                      {sm}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Code citations */}
            {selectedNode.file_references?.length > 0 && (
              <div className="text-xs pt-2 border-t border-surface-600">
                <span className="text-gray-400 block text-[11px] mb-1.5 flex items-center gap-1 font-semibold">
                  <FileCode className="w-3.5 h-3.5" />
                  Verified Code Evidence
                </span>
                <div className="space-y-1 max-h-28 overflow-y-auto">
                  {selectedNode.file_references.map((f) => (
                    <div
                      key={f}
                      className="font-mono text-[10px] text-brand-300 bg-surface-700/60 px-2 py-1 rounded truncate"
                      title={f}
                    >
                      {f}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Selected Edge Details Drawer */}
        {selectedEdge && (
          <div className="absolute top-4 right-4 w-80 bg-surface-800/95 backdrop-blur-md border border-brand-500/50 rounded-xl p-4 shadow-2xl z-10 space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <span className="badge badge-green text-[10px] font-mono">
                  {selectedEdge.relationship_type}
                </span>
                <h3 className="text-xs font-semibold text-gray-100 mt-1">
                  {selectedEdge.label}
                </h3>
              </div>
              <button
                onClick={() => setSelectedEdge(null)}
                className="text-gray-400 hover:text-gray-200 p-1"
                aria-label="Close relationship details"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-gray-300">{selectedEdge.description}</p>

            <div className="text-xs space-y-1 pt-2 border-t border-surface-600">
              <div className="flex justify-between">
                <span className="text-gray-400">Source:</span>
                <span className="font-mono text-gray-200">{selectedEdge.source}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Target:</span>
                <span className="font-mono text-gray-200">{selectedEdge.target}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Confidence:</span>
                <span className="font-semibold text-emerald-400">{selectedEdge.confidence}</span>
              </div>
            </div>

            {selectedEdge.evidence_file && (
              <div className="text-xs pt-2 border-t border-surface-600">
                <span className="text-gray-400 block text-[11px] mb-1">Evidence Citation</span>
                <div className="font-mono text-[11px] text-brand-300 bg-surface-700/60 p-2 rounded">
                  {selectedEdge.evidence_file}
                  {selectedEdge.line_number ? `:${selectedEdge.line_number}` : ''}
                </div>
                {selectedEdge.evidence?.snippet && (
                  <div className="mt-1 font-mono text-[10px] text-gray-300 bg-surface-900 p-1.5 rounded overflow-x-auto">
                    {selectedEdge.evidence.snippet}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Graph Legend Overlay */}
        <div className="absolute bottom-3 right-3 bg-surface-800/90 backdrop-blur-sm border border-surface-600 rounded-lg px-3 py-2 text-[10px] space-y-1.5 z-10">
          <p className="font-semibold text-gray-300 mb-1">Graph Legend</p>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span className="text-gray-300">Frontend App</span>
            <span className="w-2 h-2 rounded-full bg-violet-400 ml-2" />
            <span className="text-gray-300">MCP Server</span>
            <span className="w-2 h-2 rounded-full bg-amber-400 ml-2" />
            <span className="text-gray-300">Worker</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-gray-300">Data & Cache (Redis)</span>
            <span className="w-2 h-2 rounded-full bg-purple-400 ml-2" />
            <span className="text-gray-300">CI/CD & Infra</span>
          </div>
        </div>
      </div>

      {/* Architectural Narrative Explanation */}
      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <h2 className="text-sm font-semibold text-gray-100">
              Architecture Analysis & Component Explanation
            </h2>
          </div>
          <span className="text-xs text-gray-400 font-mono">
            Model: {architecture.model_used || 'deterministic_synthesizer_v2'}
          </span>
        </div>

        <div className="prose prose-invert max-w-none text-xs text-gray-300 leading-relaxed bg-surface-900/60 p-4 rounded-lg border border-surface-700 font-sans space-y-2 whitespace-pre-line">
          {architecture.explanation}
        </div>

        <div className="flex items-start gap-2 p-3 bg-surface-700/40 rounded-lg text-xs text-gray-400 border border-surface-600">
          <Info className="w-4 h-4 text-brand-400 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Grounding Standard:</strong> Component boundaries and relationship edges are derived strictly from AST scans, entry points, and manifest configurations. Inferred relationships and deployment pathways are distinctly labeled and separated from runtime communication paths.
          </span>
        </div>
      </div>
    </div>
  )
}
