"use client";
import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { formatDecimal, formatCurrency } from "@/lib/formatters";

export default function RiskPage() {
  const { token } = useAuth();
  const [balance, setBalance] = useState("1000");
  const [risk, setRisk] = useState("1");
  const [entry, setEntry] = useState("1.1000");
  const [stop, setStop] = useState("1.0900");
  const [tp, setTp] = useState("");
  const [result, setResult] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const calculate = async () => {
    setError("");
    try {
      const body: any = { account_balance: balance, risk_percent: risk, entry_price: entry, stop_loss: stop };
      if (tp) body.take_profit = tp;
      const data = await api.post("/risk/calculate", body, token);
      setResult(data);
    } catch (err: any) { setError(err.message); }
  };

  const save = async () => {
    setSaving(true);
    try {
      await api.post("/risk/calculate", { account_balance: balance, risk_percent: risk, entry_price: entry, stop_loss: stop, take_profit: tp || null, save: true }, token);
      alert("Plan saved.");
    } catch {}
    setSaving(false);
  };

  if (!token) return <p className="p-4">Please sign in.</p>;

  return (
    <div className="mx-auto max-w-2xl px-4 py-6">
      <h1 className="text-2xl font-bold">Risk Calculator</h1>
      <div className="mt-4 grid gap-3">
        <input className="input" placeholder="Account balance" value={balance} onChange={(e) => setBalance(e.target.value)} />
        <input className="input" placeholder="Risk % (max 5)" value={risk} onChange={(e) => setRisk(e.target.value)} />
        <input className="input" placeholder="Entry price" value={entry} onChange={(e) => setEntry(e.target.value)} />
        <input className="input" placeholder="Stop-loss" value={stop} onChange={(e) => setStop(e.target.value)} />
        <input className="input" placeholder="Take-profit (optional)" value={tp} onChange={(e) => setTp(e.target.value)} />
        <button onClick={calculate} className="btn btn-primary">Calculate</button>
      </div>
      {error && <p className="mt-2 text-red-600">{error}</p>}
      {result && (
        <div className="mt-4 card p-4 space-y-1">
          <p>Risk amount: {formatCurrency(result.risk_amount, result.currency)}</p>
          <p>Position size: {formatDecimal(result.calculated_position_size)}</p>
          {result.risk_reward_ratio && <p>Risk:Reward: 1:{formatDecimal(result.risk_reward_ratio)}</p>}
          <p className="text-xs text-gray-500">{result.assumptions}</p>
          <p className="text-xs text-gray-500">{result.disclaimer}</p>
          <button onClick={save} disabled={saving} className="btn border border-[var(--border)] mt-2">{saving ? "Saving..." : "Save plan"}</button>
        </div>
      )}
    </div>
  );
}
