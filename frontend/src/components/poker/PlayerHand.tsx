import { PlayingCard } from "./PlayingCard";

export function PlayerHand({ cards }: { cards: string[] }) {
  return <div className="player-hand" aria-label="Your hole cards">{cards.map((card) => <PlayingCard key={card} code={card} />)}</div>;
}
