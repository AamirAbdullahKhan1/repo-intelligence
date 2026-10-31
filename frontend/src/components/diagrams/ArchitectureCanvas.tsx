import { useEffect, useState, useRef } from "react";
import ReactFlow, {
  Background,
  Controls,
  Position,
  MarkerType,
  BaseEdge,
  type EdgeProps,
  type Node,
  type Edge,
  type ReactFlowInstance,
  useNodesState,
} from "reactflow";
import ELK, { type ElkNode } from "elkjs/lib/elk-api.js";
import ElkWorker from "elkjs/lib/elk-worker.min.js?worker";
import type { View } from "../../../../shared/contracts/analysis";
import "reactflow/dist/style.css";
import { relationshipLabel, statusLabels } from "../../services/presentation";

const elk = new ELK({ workerFactory: () => new ElkWorker() });
const palette: Record<string, string> = {
  application: "#234367",
  component: "#28434c",
  architecture_group: "#3a3759",
  unresolved: "#3b293c",
  deployable: "#443662",
  symbol: "#263a50",
  endpoint: "#2c5764",
  sdk: "#214f4b",
  sdk_group: "#214f4b",
  external_service: "#254e50",
  storage: "#54462a",
  container: "#433858",
};

function RoutedEdge(props: EdgeProps) {
  const points = props.data?.points as { x: number; y: number }[] | undefined;
  if (!points?.length) return null;
  const path = points.map((p, i) => `${i ? "L" : "M"} ${p.x} ${p.y}`).join(" ");
  let longest = 0,
    label = { x: 0, y: 0 };
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1],
      b = points[i],
      length = Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
    if (length > longest) {
      longest = length;
      label = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
    }
  }
  return <BaseEdge {...props} path={path} labelX={label.x} labelY={label.y} />;
}
const edgeTypes = { routed: RoutedEdge };

export function ArchitectureCanvas({
  view,
  onSelect,
  panelOpen,
}: {
  view: View;
  onSelect: (id: string) => void;
  panelOpen: boolean;
}) {
  const flow = useRef<ReactFlowInstance>();
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const frame = requestAnimationFrame(() =>
      flow.current?.fitView({ padding: 0.12, duration: 150 }),
    );
    return () => cancelAnimationFrame(frame);
  }, [panelOpen]);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  useEffect(() => {
    if (!ready || !host.current) return;
    let frame = 0;
    const observer = new ResizeObserver(() => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() =>
        flow.current?.fitView({ padding: 0.12, duration: 0 }),
      );
    });
    observer.observe(host.current);
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
    };
  }, [ready]);
  useEffect(() => {
    let active = true;
    setReady(false);
    setError("");
    const nodeWidth = view.kind === "system" ? 205 : 250;
    elk
      .layout({
        id: "root",
        layoutOptions: {
          "elk.algorithm": "layered",
          "elk.direction": "RIGHT",
          "elk.spacing.nodeNode": view.kind === "system" ? "32" : "45",
          "elk.layered.spacing.nodeNodeBetweenLayers":
            view.kind === "system" ? "60" : "110",
          "elk.edgeRouting": "ORTHOGONAL",
        },
        children: view.nodes.map((n) => ({
          id: n.id,
          width: nodeWidth,
          height: 88,
        })),
        edges: view.edges.map((e) => ({
          id: e.id,
          sources: [e.source],
          targets: [e.target],
        })),
      } as ElkNode)
      .then((layout) => {
        if (!active) return;
        const positions = new Map(
          layout.children?.map((n) => [n.id, { x: n.x || 0, y: n.y || 0 }]),
        );
        const routes = new Map(
          layout.edges?.map((e) => [e.id, e.sections?.[0]]),
        );
        setNodes(
          view.nodes.map(
            (n) =>
              ({
                id: n.id,
                position: positions.get(n.id) || { x: 0, y: 0 },
                sourcePosition: Position.Right,
                targetPosition: Position.Left,
                style: {
                  width: nodeWidth,
                  height: 88,
                  background: palette[n.kind] || "#283548",
                  color: "#e8f0fa",
                  border:
                    n.resolution === "unresolved"
                      ? "2px dashed #dd8196"
                      : n.resolution === "ambiguous"
                        ? "2px dashed #e1b664"
                        : "1px solid #62809d",
                  borderRadius: 12,
                  padding: 12,
                  textAlign: "left",
                },
                data: {
                  label: (
                    <>
                      <div className="node-kind">
                        {n.kind === "symbol"
                          ? n.declaration_kind?.includes("Class")
                            ? "CLASS"
                            : n.declaration_kind?.includes("Interface")
                              ? "INTERFACE"
                              : n.declaration_kind?.includes("Method")
                                ? "METHOD"
                                : "FUNCTION"
                          : n.kind === "component"
                            ? "LOGICAL MODULE"
                            : n.kind === "application"
                              ? n.boundary?.includes("candidate")
                                ? "SOURCE ROOT CANDIDATE"
                                : "PACKAGE BOUNDARY"
                              : n.kind.replaceAll("_", " ")}
                      </div>
                      <strong title={n.label} className="node-label">
                        {n.id === "group:http"
                          ? "HTTP integrations"
                          : n.id === "group:infrastructure"
                            ? "Infrastructure"
                            : n.label}
                      </strong>
                      <div className="node-detail">
                        {n.role ||
                          n.reason ||
                          n.technology ||
                          n.file ||
                          n.boundary ||
                          n.profile ||
                          "Source-backed identity"}
                      </div>
                      {n.stats && n.stats.unresolved > 0 && (
                        <div className="node-uncertainty">
                          {n.stats.unresolved} refs need context
                        </div>
                      )}
                      {n.resolution && n.resolution !== "confirmed" && (
                        <div className={`node-status ${n.resolution}`}>
                          {statusLabels[n.resolution] || n.resolution}
                        </div>
                      )}
                    </>
                  ),
                },
              }) as Node,
          ),
        );
        setEdges(
          view.edges.map((e) => {
            const declaration =
              /BINDS_|DECLARES_|CONFIGURES_|STARTS_AFTER|ENTRYPOINT_|CONTAINS_|DEFINED_IN|IMPORTS|REEXPORTS|TYPE_REFERENCES|IMPORT_DEPENDENCY/.test(
                e.kind,
              );
            const route = routes.get(e.id);
            const resolution = e.resolution || "confirmed";
            const imports = /IMPORT|REEXPORT|TYPE_REFERENCES/.test(e.kind);
            const ownership =
              e.kind === "CONTAINS_COMPONENT" || e.kind === "DEFINED_IN";
            const color =
              resolution === "unresolved"
                ? "#df8da2"
                : resolution === "ambiguous"
                  ? "#e0bc6c"
                  : resolution === "conditional"
                    ? "#e5a964"
                    : imports
                      ? "#80aaff"
                      : declaration
                        ? "#b5a2dd"
                        : "#7dbfc8";
            const dash =
              resolution === "unresolved"
                ? "3 6"
                : resolution === "ambiguous"
                  ? "8 3 2 3"
                  : resolution === "conditional"
                    ? "9 4"
                    : ownership
                      ? "3 5"
                      : imports
                        ? "7 4"
                        : declaration
                          ? "2 4"
                          : undefined;
            return {
              id: e.id,
              type: "routed",
              data: {
                points: route
                  ? [
                      route.startPoint,
                      ...(route.bendPoints || []),
                      route.endPoint,
                    ]
                  : [],
              },
              source: e.source,
              target: e.target,
              label: ownership
                ? ""
                : (view.kind === "system" && e.kind === "USES_SDK"
                    ? "Uses SDK"
                    : view.kind === "system" && e.kind === "HTTP_INTEGRATION"
                      ? "HTTP"
                      : relationshipLabel(e.kind)) +
                  (view.kind === "workflow" && e.count && e.count > 1
                    ? ` · ${e.count}`
                    : ""),
              markerEnd: {
                type: MarkerType.ArrowClosed,
                color,
              },
              style: {
                stroke: color,
                opacity: ownership ? 0.45 : 1,
                strokeDasharray: dash,
                strokeWidth: 1.5,
              },
              labelStyle: { fill: "#d4deec", fontSize: 10 },
              labelBgStyle: { fill: "#111d2d", fillOpacity: 0.95 },
              interactionWidth: 20,
            };
          }),
        );
        setReady(true);
      })
      .catch((e) => {
        if (active) setError(String(e));
      });
    return () => {
      active = false;
    };
  }, [view, setNodes]);
  if (error) return <div role="alert">Layout failed: {error}</div>;
  if (!ready)
    return (
      <div className="canvas-message">
        Laying out {view.nodes.length} components…
      </div>
    );
  if (!nodes.length)
    return (
      <div className="canvas-message">
        No supported relationships in this view. Choose another source entry or
        logical module in the explorer.
      </div>
    );
  return (
    <div
      ref={host}
      className="flow-host"
      style={{ width: "100%", height: "100%" }}
    >
      <ReactFlow
        key={
          view.kind +
          String(view.metadata.scope_id || "") +
          String(view.metadata.entry_id || "") +
          view.nodes.length
        }
        nodes={nodes}
        onInit={(instance) => {
          flow.current = instance;
          requestAnimationFrame(() =>
            instance.fitView({ padding: 0.12, duration: 0 }),
          );
        }}
        edges={edges}
        edgeTypes={edgeTypes}
        onNodesChange={onNodesChange}
        fitView
        fitViewOptions={{ padding: 0.12 }}
        minZoom={0.15}
        maxZoom={2}
        onNodeClick={(_, n) => onSelect(n.id)}
        onEdgeClick={(_, e) => onSelect(e.id)}
        nodesDraggable={false}
        nodesConnectable={false}
        edgesFocusable
      >
        <Background color="#2a3b50" gap={24} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
