export function CardBack({ label = "Hidden opponent card" }: { label?: string }) {
  return <div className="card-back" role="img" aria-label={label}><span /></div>;
}
