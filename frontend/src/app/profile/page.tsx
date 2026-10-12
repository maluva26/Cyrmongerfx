"use client";
import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

export default function ProfilePage() {
  const { user, token, clear } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [currentPw, setCurrentPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [msg, setMsg] = useState("");

  const updateName = async () => {
    setMsg("");
    try { await api.patch("/me", { full_name: fullName }, token || undefined); setMsg("Updated."); }
    catch (err: any) { setMsg(err.message); }
  };

  const changePw = async () => {
    setMsg("");
    try { await api.post("/auth/password/change", { current_password: currentPw, new_password: newPw }, token || undefined); setMsg("Password changed."); setCurrentPw(""); setNewPw(""); }
    catch (err: any) { setMsg(err.message); }
  };

  const deleteAccount = async () => {
    if (!confirm("Type DELETE to confirm account deletion.")) return;
    try { await api.delete("/me", token || undefined); clear(); }
    catch (err: any) { setMsg(err.message); }
  };

  if (!user) return <p className="p-4">Please sign in.</p>;

  return (
    <div className="mx-auto max-w-2xl px-4 py-6 space-y-6">
      <h1 className="text-2xl font-bold">Profile</h1>
      <div className="card p-4 space-y-2">
        <p>Email: {user.email}</p>
        <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        <button onClick={updateName} className="btn btn-primary">Update name</button>
      </div>
      <div className="card p-4 space-y-2">
        <h2 className="font-semibold">Change password</h2>
        <input className="input" type="password" placeholder="Current password" value={currentPw} onChange={(e) => setCurrentPw(e.target.value)} />
        <input className="input" type="password" placeholder="New password" value={newPw} onChange={(e) => setNewPw(e.target.value)} />
        <button onClick={changePw} className="btn btn-primary">Change password</button>
      </div>
      <div className="card p-4">
        <button onClick={deleteAccount} className="btn border border-red-300 text-red-700">Delete account</button>
      </div>
      {msg && <p className="text-sm">{msg}</p>}
    </div>
  );
}
