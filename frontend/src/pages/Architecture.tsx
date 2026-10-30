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
} from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { EmptyState } from '../components/EmptyState'
import { useAnalysis } from '../context/AnalysisContext'
import type { ArchitectureNode } from '../types'

// ── Custom React Flow Node Components ──────────────────────────────────────────

function CustomNode({ data }: { data: ArchitectureNode }) {
  const getIcon = () => {
    switch (data.type) {
      case 'client':
        return <Globe className="w-4 h-4 text-sky-400" />
      case 'service':
        return <Server className="w-4 h-4 text-brand-400" />
      case 'database':
        return <Database className="w-4 h-4 text-emerald-400" />
      case 'auth':
        return <Lock className="w-4 h-4 text-amber-400" />
      case 'infrastructure':
        return <Container className="w-4 h-4 text-purple-400" />
      default:
        return <Network className="w-4 h-4 text-gray-400" />
    }
  }

  const getBorderColor = () => {
    switch (data.type) {
      case 'client':
        return 'border-sky-500/50 bg-sky-950/40 hover:border-sky-400'
      case 'service':
        return 'border-brand-500/60 bg-brand-950/50 hover:border-brand-400'
      case 'database':
        return 'border-emerald-500/50 bg-emerald-950/40 hover:border-emerald-400'
      case 'auth':
        return 'border-amber-500/50 bg-amber-950/40 hover:border-amber-400'
      case 'infrastructure':
        return 'border-purple-500/50 bg-purple-950/40 hover:border-purple-400'
      default:
        return 'border-surface-500 bg-surface-800'
    }
  }

  return (
    <div
      className={`px-4 py-3 rounded-xl border shadow-lg backdrop-blur-sm transition-all duration-150 min-w-[200px] max-w-[260px] text-left cursor-pointer ${getBorderColor()}`}
    >
      <Handle type="target" position={Position.Left} className="!bg-surface-400 !w-2.5 !h-2.5" />
      <div className="flex items-start gap-2.5">
        <div className="p-2 rounded-lg bg-surface-800/80 border border-surface-600/50 flex-shrink-0">
          {getIcon()}
        </div>
        <div className="overflow-hidden">
          <p className="text-xs font-semibold text-gray-100 truncate">{data.label}</p>
          {data.technology && (
            <p className="text-[10px] text-gray-400 truncate mt-0.5">{data.technology}</p>
          )}
          <div className="flex items-center gap-1.5 mt-2">
            <span
              className={`text-[9px] px-1.5 py-0.5 rounded font-mono ${
                data.confidence === 'verified_code_evidence'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'bg-surface-700 text-gray-300'
              }`}
            >
              {data.confidence === 'verified_code_evidence' ? 'verified' : 'inferred'}
            </span>
            {data.metadata?.routes_count > 0 && (
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30">
                {data.metadata.routes_count} routes
              </span>
            )}
          </div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-brand-500 !w-2.5 !h-2.5" />
    </div>
  )
}

const nodeTypes = {
  custom: CustomNode,
}

export function Architecture() {
  const { architecture, inventory } = useAnalysis()
  const [selectedNode, setSelectedNode] = useState<ArchitectureNode | null>(null)

  // Layout calculation for React Flow
  const initialNodes: Node[] = useMemo(() => {
    if (!architecture) return []

    let dbIndex = 0
    let infraIndex = 0

    return architecture.nodes.map((node) => {
      let x = 380
      let y = 200

      if (node.type === 'client') {
        x = 50
        y = 200
      } else if (node.type === 'service') {
        x = 380
        y = 200
      } else if (node.type === 'auth') {
        x = 720
        y = 70
      } else if (node.type === 'database') {
        x = 720
        y = 210 + dbIndex * 130
        dbIndex++
      } else if (node.type === 'infrastructure') {
        x = 380
        y = 380 + infraIndex * 120
        infraIndex++
      }

      return {
        id: node.id,
        type: 'custom',
        position: { x, y },
        data: node,
      }
    })
  }, [architecture])

  const initialEdges: Edge[] = useMemo(() => {
    if (!architecture) return []

    return architecture.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      animated: edge.relationship_type === 'calls',
      style: { stroke: '#6366f1', strokeWidth: 1.5 },
      labelStyle: { fill: '#94a3b8', fontSize: 10, fontWeight: 500 },
      labelBgStyle: { fill: '#0f172a', fillOpacity: 0.85, rx: 4, ry: 4 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#6366f1',
      },
    }))
  }, [architecture])

  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  const onNodeClick = useCallback(
    (_: any, node: Node) => {
      setSelectedNode(node.data as ArchitectureNode)
    },
    []
  )

  if (!architecture || !inventory) {
    return (
      <div className="px-6 py-6 max-w-5xl mx-auto space-y-6">
        <PageHeader
          title="Architecture Map"
          description="Interactive component diagram extracted from static code analysis."
          badge={<span className="badge badge-blue">Milestone 3</span>}
        />
        <div className="card min-h-96 flex flex-col items-center justify-center">
          <EmptyState
            icon={Network}
            title="No Architecture Model"
            description="Analyse a repository on the Overview dashboard to generate an interactive component diagram and relationship map."
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
    <div className="px-6 py-6 max-w-6xl mx-auto space-y-6">
      <PageHeader
        title={`Architecture Map — ${architecture.repo_name}`}
        description="Interactive component diagram and verified data relationships extracted from static analysis."
        badge={
          architecture.llm_enhanced ? (
            <span className="badge badge-green flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              LLM Enhanced ({architecture.model_used})
            </span>
          ) : (
            <span className="badge badge-blue flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              Deterministic Code Evidence
            </span>
          )
        }
      />

      {/* Main Graph Area */}
      <div className="card p-0 overflow-hidden relative border border-surface-600 rounded-xl h-[520px] bg-surface-900">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          fitView
          attributionPosition="bottom-left"
        >
          <Background color="#334155" gap={16} size={1} />
          <Controls className="!bg-surface-800 !border-surface-600 !text-gray-200" />
          <MiniMap
            nodeColor={(n) => {
              if (n.data?.type === 'database') return '#10b981'
              if (n.data?.type === 'auth') return '#f59e0b'
              if (n.data?.type === 'client') return '#38bdf8'
              return '#6366f1'
            }}
            maskColor="rgba(15, 23, 42, 0.7)"
            className="!bg-surface-800 !border-surface-600 rounded-lg"
          />
        </ReactFlow>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="absolute top-4 right-4 w-80 bg-surface-800/95 backdrop-blur-md border border-surface-600 rounded-xl p-4 shadow-2xl z-10 space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <span className="badge badge-blue text-[10px] uppercase">
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

            <p className="text-xs text-gray-300 leading-relaxed">
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
                  selectedNode.confidence === 'verified_code_evidence'
                    ? 'badge-green'
                    : 'badge-gray'
                }`}
              >
                {selectedNode.confidence}
              </span>
            </div>

            {selectedNode.file_references?.length > 0 && (
              <div className="text-xs pt-2 border-t border-surface-600">
                <span className="text-gray-400 block text-[11px] mb-1.5 flex items-center gap-1">
                  <FileCode className="w-3.5 h-3.5" />
                  Code References
                </span>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {selectedNode.file_references.map((f) => (
                    <div
                      key={f}
                      className="font-mono text-[11px] text-gray-300 bg-surface-700/60 px-2 py-1 rounded truncate"
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
      </div>

      {/* Architectural Narrative Explanation */}
      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <h2 className="text-sm font-semibold text-gray-100">
              Architecture Analysis & Interpretation
            </h2>
          </div>
          <span className="text-xs text-gray-400 font-mono">
            Model: {architecture.model_used || 'deterministic_synthesizer'}
          </span>
        </div>

        <div className="prose prose-invert max-w-none text-xs text-gray-300 leading-relaxed bg-surface-900/60 p-4 rounded-lg border border-surface-700 font-sans space-y-2 whitespace-pre-line">
          {architecture.explanation}
        </div>

        <div className="flex items-start gap-2 p-3 bg-surface-700/40 rounded-lg text-xs text-gray-400 border border-surface-600">
          <Info className="w-4 h-4 text-brand-400 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Safety & Grounding:</strong> Component relationships are derived from deterministic code evidence. Azure OpenAI (GPT-4.1 / GPT-6 Astra) reasons only over structured component metadata without receiving raw code files or credentials.
          </span>
        </div>
      </div>
    </div>
  )
}
