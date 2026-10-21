import { CardBack } from "./CardBack";
import { ChipStack } from "./ChipStack";
import { DealerButton } from "./DealerButton";
import { PlayingCard } from "./PlayingCard";
import type { SeatPosition } from "./seatLayout";

type SeatProps = {
  index: number;
  name: string;
  stack: number;
  acting: boolean;
  human?: boolean;
  folded?: boolean;
  allIn?: boolean;
  dealer?: boolean;
  blind?: "SB" | "BB";
  cards?: string[];
  showdown?: boolean;
  position?: SeatPosition;
  currentBet?: number;
  lastAction?: string | null;
  highlightedCards?: string[];
};

export function Seat({ index, name, stack, acting, human, folded, allIn, dealer, blind, cards = [], showdown, position, currentBet = 0, lastAction, highlightedCards = [] }: SeatProps) {
  const seatPosition = position ?? { left: 50, top: 50 };
  return (
    <div className={`poker-seat ${acting ? "seat-acting" : ""} ${folded ? "seat-folded" : ""} ${human ? "seat-human" : ""}`} style={{ left: `${seatPosition.left}%`, top: `${seatPosition.top}%` }} aria-label={`${name} seat`}>
      <div className="seat-head">
        <span className="avatar">{name.slice(0, 2).toUpperCase()}</span>
        <span><b>{name}</b><small>Seat {index + 1}</small></span>
        {dealer && <DealerButton />}
        {blind && <span className="blind-badge">{blind}</span>}
      </div>
      <ChipStack amount={stack} />
      {currentBet > 0 && <span className="seat-bet">{currentBet.toFixed(1)} BB</span>}
      {human && <span className="seat-hand-label">Your hand</span>}
      <div className="seat-cards">
        {human || showdown ? cards.map((card) => <PlayingCard key={card} code={card} highlighted={highlightedCards.includes(card)} />) : [0, 1].map((card) => <CardBack key={card} />)}
      </div>
      {folded && <span className="state-badge">Folded</span>}
      {allIn && <span className="state-badge all-in-badge">All-in</span>}
      {lastAction && !folded && <span className="last-action">{lastAction.replace("-", " ")}</span>}
    </div>
  );
}
