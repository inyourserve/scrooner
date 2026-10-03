// doc/design/shadcn-system.md section 12: "don't show 'Loading...' when a
// financial table loads -- show a skeleton matching the exact table layout."
// Reuses .results-table's real markup/classes so there's zero layout shift
// between this and the real result rows that replace it.
export function TableSkeleton({ columnLabels, rows = 6, showClassification = true }: { columnLabels: string[]; rows?: number; showClassification?: boolean }) {
  return (
    <div className="results-table-wrap ds-data-table-shell">
      <table className="results-table ds-data-table ds-table-skeleton">
        {/* Column headers are real, meaningful content (they tell an
            assistive-tech user what's about to load) -- only the shimmer
            placeholder rows below are decorative and hidden from the tree. */}
        <thead>
          <tr>
            <th scope="col">S.No.</th>
            <th scope="col">Company</th>
            {showClassification && <th scope="col">Industry</th>}
            {columnLabels.map((label, index) => <th className="results-metric-heading" scope="col" data-numeric="true" key={`${label}-${index}`}><span className="results-column-label">{label}</span></th>)}
          </tr>
        </thead>
        <tbody aria-hidden="true">
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              <td><span className="ds-skeleton ds-skeleton--text" style={{ width: "24px" }} /></td>
              <th scope="row"><span className="ds-skeleton ds-skeleton--text" style={{ width: "76%" }} /><span className="ds-skeleton ds-skeleton--text ds-skeleton--sub" style={{ width: "52%" }} /></th>
              {showClassification && <td><span className="ds-skeleton ds-skeleton--text" style={{ width: "64%" }} /></td>}
              {columnLabels.map((_, colIndex) => (
                <td className="results-metric-cell" data-numeric="true" key={colIndex}><span className="ds-skeleton ds-skeleton--text ds-skeleton--value" style={{ width: "58%" }} /></td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
