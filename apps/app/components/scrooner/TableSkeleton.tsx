// doc/design/shadcn-system.md section 12: "don't show 'Loading...' when a
// financial table loads -- show a skeleton matching the exact table layout."
// Reuses .results-table's real markup/classes so there's zero layout shift
// between this and the real result rows that replace it.
export function TableSkeleton({ columnLabels, rows = 6 }: { columnLabels: string[]; rows?: number }) {
  return (
    <div className="results-table-wrap">
      <table className="results-table ds-table-skeleton">
        {/* Column headers are real, meaningful content (they tell an
            assistive-tech user what's about to load) -- only the shimmer
            placeholder rows below are decorative and hidden from the tree. */}
        <thead>
          <tr>
            <th scope="col">Company</th>
            <th scope="col">Classification</th>
            {columnLabels.map((label, index) => <th scope="col" key={`${label}-${index}`}>{label}</th>)}
            <th scope="col"><span className="sr-only">Actions</span></th>
          </tr>
        </thead>
        <tbody aria-hidden="true">
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              <th scope="row"><span className="ds-skeleton ds-skeleton--text" style={{ width: "76%" }} /><span className="ds-skeleton ds-skeleton--text ds-skeleton--sub" style={{ width: "52%" }} /></th>
              <td><span className="ds-skeleton ds-skeleton--text" style={{ width: "64%" }} /></td>
              {columnLabels.map((_, colIndex) => (
                <td key={colIndex}><span className="ds-skeleton ds-skeleton--text ds-skeleton--value" style={{ width: "58%" }} /></td>
              ))}
              <td />
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
