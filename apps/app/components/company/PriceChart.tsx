"use client";

import { useMemo, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { Delta } from "@/components/scrooner/Delta";
import { EmptyState } from "@/components/scrooner/EmptyState";
import type { PriceHistoryPoint } from "@/lib/company/db";

const ranges = [{ days: 30, label: "1M" }, { days: 180, label: "6M" }, { days: 365, label: "1Y" }, { days: 1095, label: "3Y" }, { days: 1825, label: "5Y" }, { days: 0, label: "Max" }];
const CHART_WIDTH = 1000;
const CHART_HEIGHT = 300;
const PLOT_TOP = 28;
const PLOT_BOTTOM = 272;

function totalSpan(points: PriceHistoryPoint[]) {
  return points.length > 1 ? (new Date(points.at(-1)!.date).getTime() - new Date(points[0].date).getTime()) / 86_400_000 : 0;
}

export function PriceChart({ companyName, points }: { companyName: string; points: PriceHistoryPoint[] }) {
  // Default to 1Y only once real history actually exceeds a year -- otherwise
  // start at "Max" so a company with a few weeks of verified data isn't stuck
  // on a period toggle that would show the exact same (small) chart anyway.
  const [days, setDays] = useState(() => (totalSpan(points) > 365 ? 365 : 0));
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const visible = useMemo(() => { if (!days || !points.length) return points; const end = new Date(points.at(-1)!.date); const cutoff = new Date(end); cutoff.setDate(cutoff.getDate() - days); return points.filter((point) => new Date(point.date) >= cutoff); }, [days, points]);
  const values = visible.map((point) => Number(point.price)).filter(Number.isFinite);
  // Only offer a period button that would actually narrow the view -- with
  // real price history still shallow for most companies (a small daily
  // snapshot table, not a full backfill yet), showing 1Y/3Y/5Y/Max side by
  // side when they'd all render the identical 2 points is misleading, not premium.
  const totalSpanDays = totalSpan(points);
  const availableRanges = ranges.filter((range) => range.days === 0 || range.days < totalSpanDays);

  if (values.length < 2) return <EmptyState title="Price history is not available yet." description="The chart will appear after verified daily observations accumulate." />;

  const min = Math.min(...values), max = Math.max(...values), spread = max - min || 1;
  const xAt = (index: number) => (index / (visible.length - 1)) * CHART_WIDTH;
  const yAt = (price: number) => PLOT_BOTTOM - ((price - min) / spread) * (PLOT_BOTTOM - PLOT_TOP);
  const polyline = visible.map((point, index) => `${xAt(index).toFixed(1)},${yAt(Number(point.price)).toFixed(1)}`).join(" ");
  const change = ((values.at(-1)! / values[0]) - 1) * 100;
  const hovered = hoverIndex != null ? visible[hoverIndex] : null;

  function onPointerMove(event: ReactPointerEvent<SVGSVGElement>) {
    const svg = svgRef.current;
    if (!svg || visible.length < 2) return;
    const rect = svg.getBoundingClientRect();
    const fraction = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
    setHoverIndex(Math.round(fraction * (visible.length - 1)));
  }

  return (
    <div className="price-chart">
      <div className="price-chart__toolbar">
        <div>
          <strong>${values.at(-1)!.toFixed(2)}</strong>
          <Delta value={change} size="sm" />
          <small>{visible.length} observation{visible.length === 1 ? "" : "s"} · {visible[0]?.date} – {visible.at(-1)?.date}</small>
        </div>
        {availableRanges.length > 1 && (
          <div className="segmented-control" role="group" aria-label="Chart period">
            {availableRanges.map((range) => <button type="button" aria-pressed={days === range.days} onClick={() => setDays(range.days)} key={range.label}>{range.label}</button>)}
          </div>
        )}
      </div>
      <div className="price-chart__plot">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
          preserveAspectRatio="none"
          role="img"
          aria-label={`${companyName} closing-price history`}
          onPointerMove={onPointerMove}
          onPointerLeave={() => setHoverIndex(null)}
        >
          <line x1="0" x2={CHART_WIDTH} y1={PLOT_BOTTOM} y2={PLOT_BOTTOM} />
          <polyline points={polyline} vectorEffect="non-scaling-stroke" />
          {hovered && (
            <g aria-hidden="true">
              <line className="price-chart__crosshair" x1={xAt(hoverIndex!)} x2={xAt(hoverIndex!)} y1={PLOT_TOP} y2={PLOT_BOTTOM} vectorEffect="non-scaling-stroke" />
              <circle className="price-chart__dot" cx={xAt(hoverIndex!)} cy={yAt(Number(hovered.price))} r="4" vectorEffect="non-scaling-stroke" />
            </g>
          )}
        </svg>
        {hovered && (
          <div className="price-chart__tooltip" style={{ left: `${(xAt(hoverIndex!) / CHART_WIDTH) * 100}%` }}>
            <strong>${Number(hovered.price).toFixed(2)}</strong>
            <span>{hovered.date}</span>
          </div>
        )}
      </div>
      <div className="price-chart__axis"><span>${min.toFixed(2)}</span><span>${max.toFixed(2)}</span></div>
    </div>
  );
}
