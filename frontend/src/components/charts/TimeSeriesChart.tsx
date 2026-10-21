import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Series = { label: string; values: number[]; color: string };

export function TimeSeriesChart({ series, title }: { series: Series[]; title: string }) {
  const length = Math.max(...series.map((item) => item.values.length));
  const data = Array.from({ length }, (_, index) => {
    const point: Record<string, number> = { index: index + 1 };
    series.forEach((item) => {
      const value = item.values[index];
      if (Number.isFinite(value)) point[item.label] = value;
    });
    return point;
  });
  return (
    <div className="chart" role="img" aria-label={title}>
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data}>
          <CartesianGrid stroke="#2c352f" />
          <XAxis dataKey="index" stroke="#8fa096" />
          <YAxis stroke="#8fa096" />
          <Tooltip />
          <Legend />
          {series.map((item) => (
            <Line key={item.label} dataKey={item.label} stroke={item.color} dot={false} connectNulls />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
