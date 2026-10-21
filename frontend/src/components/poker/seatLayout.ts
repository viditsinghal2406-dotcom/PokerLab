export type SeatPosition = { left: number; top: number };

export function seatLayout(playerCount: number, orientation: "horizontal" | "vertical" = "horizontal"): SeatPosition[] {
  if (playerCount < 2 || playerCount > 9) throw new Error("playerCount must be between 2 and 9");
  const positions: SeatPosition[] = [{ left: 50, top: 90 }];
  const start = orientation === "horizontal" ? 160 : 150;
  const end = orientation === "horizontal" ? 380 : 390;
  const width = orientation === "horizontal" ? 64 : 68;
  const height = orientation === "horizontal" ? 32 : 28;
  const centerTop = orientation === "horizontal" ? 42 : 34;
  for (let index = 1; index < playerCount; index += 1) {
    const angle = (start + ((end - start) * (index - 1)) / Math.max(1, playerCount - 2)) * Math.PI / 180;
    positions.push({
      left: Number((50 + width * Math.cos(angle) / 2).toFixed(3)),
      top: Number((centerTop + height * Math.sin(angle) / 2).toFixed(3)),
    });
  }
  return positions;
}
