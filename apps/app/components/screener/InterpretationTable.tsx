import { metricByName } from "@/lib/screener/catalog";
import { categorySummary, predicateSummary } from "@/lib/screener/interpretation";
import type { MetricDefinition, ScreenQueryPayload } from "@/lib/screener/types";

export function InterpretationTable({ query, metrics, partial = false }: {
  query: ScreenQueryPayload;
  metrics: MetricDefinition[];
  partial?: boolean;
}) {
  const categories = categorySummary(query);
  return (
    <div className={`interpretation-table ${partial ? "partial" : ""}`} role="table" aria-label={partial ? "Recognized partial criteria" : "Interpreted criteria"}>
      <div className="interpretation-table-head" role="row">
        <span role="columnheader">Metric or classification</span><span role="columnheader">Operator</span><span role="columnheader">Value</span><span role="columnheader">Period</span>
      </div>
      {query.metric_predicates.map((predicate, index) => {
        const summary = predicateSummary(predicate, metrics);
        return (
          <div className="interpretation-row" role="row" key={`${predicate.metric_name}-${index}`}>
            <strong role="cell">{summary.metric}</strong>
            <span role="cell">{summary.operator}</span>
            <span role="cell">{summary.value}</span>
            <span role="cell">Latest available</span>
          </div>
        );
      })}
      {categories.map((label) => (
        <div className="interpretation-row" role="row" key={label}>
          <strong role="cell">{label}</strong><span role="cell">Equal to</span><span role="cell">Selected class</span><span role="cell">Current company status</span>
        </div>
      ))}
      <div className="interpretation-settings" role="row">
        <span role="cell"><strong>Sort</strong> {query.sort_by ? metricByName(metrics, query.sort_by)?.display_name ?? query.sort_by : "Deterministic default"}</span>
        <span role="cell"><strong>Direction</strong> {query.sort_desc ? "Highest first" : "Lowest first"}</span>
        <span role="cell"><strong>Limit</strong> {query.limit ?? "No explicit limit"}</span>
        <span role="cell"><strong>Universe</strong> {query.include_inactive ? "Active and inactive" : "Active companies"}</span>
      </div>
    </div>
  );
}
