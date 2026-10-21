export function HandHistory({ entries }: { entries: string[] }) {
  return <details className="hand-history"><summary>Hand history</summary><div>{entries.map((entry, index) => <p key={`${entry}-${index}`}>{entry}</p>)}</div></details>;
}
