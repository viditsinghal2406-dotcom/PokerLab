import { PlayingCard } from "./PlayingCard";

export function Board({ cards, street, highlighted = [] }: { cards: string[]; street: string; highlighted?: string[] }) {
  return (
    <div className="board-area">
      <span className="street-label">{street}</span>
      <div className="board-cards" aria-label="Community cards">
        {cards.length ? cards.map((card) => <PlayingCard key={card} code={card} highlighted={highlighted.includes(card)} />) : <span className="board-empty">Community cards</span>}
      </div>
    </div>
  );
}
