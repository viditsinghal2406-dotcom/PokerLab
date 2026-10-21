import { Board } from "./Board";
import { PlayerHand } from "./PlayerHand";
import { PotDisplay } from "./PotDisplay";
import { Seat } from "./Seat";
import { seatLayout } from "./seatLayout";
import type { TableSeat } from "../../services/api";

type TableLayoutProps = { board: string[]; street: string; pot: number; stacks: number[]; acting: number; hole: string[][]; finished: boolean; winners: number[]; seats?: TableSeat[]; usedCards?: Record<string, string[]> };

export function TableLayout({ board, street, pot, stacks, acting, hole, finished, winners, seats, usedCards = {} }: TableLayoutProps) {
  const tableSeats = seats?.length ? seats : stacks.map((stack, index) => ({
    index, name: index === 0 ? "You" : `Player ${index + 1}`, stack, current_bet: 0, total_committed: 0,
    folded: false, all_in: false, is_dealer: index === 0, is_sb: index === 1, is_bb: index === 2,
    last_action: null, cards_visible: hole[index] ?? [],
  }));
  const positions = seatLayout(tableSeats.length, typeof window !== "undefined" && window.matchMedia("(max-width: 700px)").matches ? "vertical" : "horizontal");
  return (
    <div className="arena-table">
      <div className="table-seats">{tableSeats.map((seat) => <Seat key={seat.index} index={seat.index} name={seat.name} stack={seat.stack} acting={acting === seat.index && !finished} human={seat.index === 0} dealer={seat.is_dealer} blind={seat.is_sb ? "SB" : seat.is_bb ? "BB" : undefined} showdown={finished} cards={seat.cards_visible} folded={seat.folded} allIn={seat.all_in} position={positions[seat.index]} currentBet={seat.current_bet} lastAction={seat.last_action} highlightedCards={usedCards[String(seat.index)]} />)}</div>
      <div className="felt-core"><Board cards={board} street={street} highlighted={Object.values(usedCards).flat()} /><PotDisplay amount={pot} /></div>
    </div>
  );
}
