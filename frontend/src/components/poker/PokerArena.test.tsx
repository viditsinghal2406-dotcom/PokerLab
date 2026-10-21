import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ActionBar } from "./ActionBar";
import { BetSlider } from "./BetSlider";
import { PlayingCard } from "./PlayingCard";
import { Seat } from "./Seat";
import { ShowdownPanel } from "./ShowdownPanel";
import { seatLayout } from "./seatLayout";

describe("poker arena components", () => {
  afterEach(() => cleanup());

  it("renders accessible playing cards", () => {
    render(<PlayingCard code="Qd" />);
    expect(screen.getByRole("img", { name: "Queen of diamonds" })).toBeTruthy();
    expect(screen.getAllByText("♦").length).toBeGreaterThan(0);
    expect(document.querySelector("svg.card-face")).toBeTruthy();
  });

  it("does not render opponent card identities before showdown", () => {
    render(<Seat index={1} name="Opponent" stack={100} acting={false} cards={["As", "Kd"]} />);
    expect(screen.queryByLabelText("Ace of spades")).toBeNull();
    expect(screen.getAllByLabelText("Hidden opponent card")).toHaveLength(2);
  });

  it("disables actions absent from the backend legal-actions list", () => {
    render(<ActionBar legal={["fold", "check"]} callAmount={0} bet={2} min={2} max={20} pot={3} onBetChange={vi.fn()} onAction={vi.fn()} />);
    expect((screen.getByRole("button", { name: /Fold/ }) as HTMLButtonElement).disabled).toBe(false);
    expect((screen.getByRole("button", { name: /Check/ }) as HTMLButtonElement).disabled).toBe(false);
    expect((screen.getByRole("button", { name: /Bet \/ Raise/ }) as HTMLButtonElement).disabled).toBe(true);
    const actionBar = screen.getByLabelText("Poker actions");
    const actionButtons = actionBar.querySelectorAll("button");
    expect((actionButtons[3] as HTMLButtonElement).disabled).toBe(true);
  });

  it("clamps slider and numeric input to the pot-limit bounds", () => {
    const onChange = vi.fn();
    render(<BetSlider value={5} min={2} max={8} pot={6} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText("Bet amount"), { target: { value: "20" } });
    fireEvent.change(screen.getByLabelText("Bet amount number"), { target: { value: "0" } });
    expect(onChange).toHaveBeenNthCalledWith(1, 8);
    expect(onChange).toHaveBeenNthCalledWith(2, 2);
  });

  it("places every seat for supported player counts", () => {
    for (const count of [2, 3, 6, 9]) {
      const positions = seatLayout(count, "horizontal");
      expect(positions).toHaveLength(count);
      expect(positions.every((position) => position.left >= 0 && position.left <= 100 && position.top >= 0 && position.top <= 100)).toBe(true);
    }
  });

  it("renders backend showdown metadata and payout", () => {
    render(<ShowdownPanel winners={[0]} handNames={{ "0": "Full house" }} payouts={[12.5, 0]} />);
    expect(screen.getByText("Seat 1 wins")).toBeTruthy();
    expect(screen.getByText("Full house")).toBeTruthy();
    expect(screen.getByText(/12\.5 BB/)).toBeTruthy();
  });
});
