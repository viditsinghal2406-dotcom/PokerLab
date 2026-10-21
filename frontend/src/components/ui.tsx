import type { ButtonHTMLAttributes, ReactNode } from "react";

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger" | "ghost";
}) {
  return <button className={`ui-button ui-button-${variant} ${className}`} {...props} />;
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`ui-card ${className}`}>{children}</section>;
}

export function Stat({ label, value }: { label: string; value: ReactNode }) {
  return <div className="ui-stat"><span>{label}</span><strong>{value}</strong></div>;
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "success" | "danger" | "gold" }) {
  return <span className={`ui-badge ui-badge-${tone}`}>{children}</span>;
}

export function EmptyState({ title, children, action }: { title: string; children: ReactNode; action?: ReactNode }) {
  return <div className="ui-empty"><h3>{title}</h3><p>{children}</p>{action}</div>;
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`ui-skeleton ${className}`} aria-hidden="true" />;
}
