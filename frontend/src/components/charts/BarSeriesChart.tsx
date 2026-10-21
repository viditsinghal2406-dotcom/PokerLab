import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function BarSeriesChart({ values, title }: { values: number[]; title: string }) {
  const data = values.map((value, index) => ({ index, value }));
  return (
    <div className="chart" role="img" aria-label={title}>
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid stroke="#2c352f" />
          <XAxis dataKey="index" stroke="#8fa096" />
          <YAxis stroke="#8fa096" />
          <Tooltip />
          <Bar dataKey="value" fill="#2f8f63" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
