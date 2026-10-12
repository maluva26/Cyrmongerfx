export function formatPercent(n: number | string) {
  return `${Number(n).toFixed(2)}%`;
}
export function formatDecimal(n: number | string, digits = 4) {
  return Number(n).toFixed(digits);
}
export function formatCurrency(n: number | string, currency = "USD") {
  return `${Number(n).toLocaleString()} ${currency}`;
}
export function formatDate(iso?: string) {
  if (!iso) return "";
  return new Date(iso).toLocaleString();
}
