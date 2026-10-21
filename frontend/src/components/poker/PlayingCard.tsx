const ranks: Record<string, string> = {
  A: "Ace", K: "King", Q: "Queen", J: "Jack", T: "10",
  "9": "9", "8": "8", "7": "7", "6": "6", "5": "5", "4": "4", "3": "3", "2": "2",
};

const suits: Record<string, { symbol: string; name: string; red: boolean }> = {
  h: { symbol: "♥", name: "hearts", red: true },
  d: { symbol: "♦", name: "diamonds", red: true },
  s: { symbol: "♠", name: "spades", red: false },
  c: { symbol: "♣", name: "clubs", red: false },
};

export function PlayingCard({ code, highlighted = false }: { code: string; highlighted?: boolean }) {
  const rank = ranks[code[0]] ?? code[0];
  const suit = suits[code[1]?.toLowerCase()] ?? suits.s;
  const pipCount = code[0] === "A" ? 1 : Number(code[0]) || (code[0] === "T" ? 10 : 0);
  const pips = Array.from({ length: pipCount }, (_, index) => ({
    x: 30 + (index % 2) * 10,
    y: 27 + Math.floor(index / 2) * 9,
  }));
  return (
    <div className={`playing-card ${suit.red ? "card-red" : "card-dark"} ${highlighted ? "card-highlighted" : ""}`} role="img" aria-label={`${rank} of ${suit.name}`}>
      <svg className="card-face" viewBox="0 0 70 100" aria-hidden="true">
        <text className="card-rank" x="7" y="15">{code[0]}</text>
        <text className="card-corner-suit" x="8" y="27">{suit.symbol}</text>
        {pipCount > 0 ? pips.map((pip, index) => <text key={index} className="card-pip" x={pip.x} y={pip.y}>{suit.symbol}</text>) : <text className="card-face-suit" x="35" y="64">{suit.symbol}</text>}
        <text className="card-rank card-rank-bottom" x="63" y="85">{code[0]}</text>
        <text className="card-corner-suit card-corner-suit-bottom" x="62" y="73">{suit.symbol}</text>
      </svg>
    </div>
  );
}
