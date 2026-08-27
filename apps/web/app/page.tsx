"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  ChatResult,
  Message,
  ModelLite,
  ProduceSummary,
  Progress,
  downloadUrl,
  getDeliverables,
  getMessages,
  getModels,
  getProgress,
  postChat,
  produce,
} from "@/lib/api";

const WORK_LABELS: Record<string, string> = {
  discover: "Finding opportunities",
  eligibility: "Checking eligibility",
  match: "Scoring the match",
  research: "Researching community",
  research_funder: "Researching funder",
  research_org: "Researching prior winners",
  requirements: "Planning proposal",
  draft: "Drafting sections",
  budget: "Building budget",
  ledger: "Checking claims",
  qa: "Running QA",
  package: "Packaging deliverable",
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conv, setConv] = useState<string>("");
  const [projectId, setProjectId] = useState<string>("proj-1");
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [summary, setSummary] = useState<ProduceSummary | null>(null);
  const [models, setModels] = useState<ModelLite[]>([]);
  const [modelChoice, setModelChoice] = useState("auto");
  const [deliverables, setDeliverables] = useState<string[]>([]);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getModels().then(setModels).catch(() => setModels([]));
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, summary, progress]);

  const poll = useCallback(async (project: string, convId: string) => {
    try {
      const p = await getProgress(project);
      setProgress(p);
      if (p.by_state.SUCCEEDED === p.task_count && p.task_count > 0) {
        const s = await produce(project, false);
        setSummary(s);
        const arts = await getDeliverables(project);
        setDeliverables(arts.map((a) => a.artifact_id));
        const msgs = await getMessages(convId);
        setMessages(msgs);
        setBusy(false);
        return;
      }
      if (busy) {
        setTimeout(() => poll(project, convId), 1500);
      }
    } catch {
      // backend not running yet — keep polling only while busy
      if (busy) {
        setTimeout(() => poll(project, convId), 2000);
      }
    }
  }, [busy]);

  async function send() {
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setBusy(true);
    setSummary(null);
    try {
      const r: ChatResult = await postChat(text);
      setConv(r.conversation_id);
      setProjectId(r.project_id);
      setMessages(await getMessages(r.conversation_id));
      setTimeout(() => poll(r.project_id, r.conversation_id), 800);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { message_id: "err", role: "assistant",
          content: `Error: ${(e as Error).message}` },
      ]);
      setBusy(false);
    }
  }

  const checked = Object.entries(progress?.by_state ?? {})
    .filter(([k]) => ["SUCCEEDED", "FAILED"].includes(k))
    .reduce((a, [, v]) => a + v, 0);
  const total = progress?.task_count ?? 0;

  return (
    <main className="flex h-screen">
      {/* left sidebar */}
      <aside className="w-56 shrink-0 border-r border-surface-border bg-surface-raised p-3 flex flex-col gap-2">
        <button
          onClick={() => { setMessages([]); setSummary(null); setProgress(null); }}
          className="rounded-lg bg-accent px-3 py-2 text-sm font-medium text-black hover:opacity-90"
        >
          + New Chat
        </button>
        <div className="text-xs uppercase tracking-wide text-gray-500 pt-3">
          History
        </div>
        <div className="text-sm text-gray-400 px-1">
          {conv ? "Georgia Rural Impact Grant" : "No conversations yet"}
        </div>
        <div className="text-xs uppercase tracking-wide text-gray-500 pt-3">
          Deliverables
        </div>
        <div className="flex flex-col gap-1 text-sm">
          {deliverables.length === 0 && (
            <div className="text-gray-500 px-1">None yet</div>
          )}
          {deliverables.map((id) => (
            <a key={id} href={downloadUrl(id)}
               className="rounded px-2 py-1 hover:bg-surface-border">
              {id.replace(/^proj-1-/, "").replace("proposal_", "Proposal ")}
            </a>
          ))}
        </div>
        <div className="mt-auto text-[11px] text-gray-600 px-1">
          Submission disabled — review only
        </div>
      </aside>

      {/* center conversation */}
      <section className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center pt-16 text-gray-400">
              <h1 className="text-xl font-semibold text-gray-200">
                What do you need funding for?
              </h1>
              <p className="mt-2 text-sm max-w-md mx-auto">
                Tell us about your program — we handle finding opportunities,
                checking eligibility, research, and drafting.
              </p>
            </div>
          )}
          {messages.map((m) => (
            <div key={m.message_id}
                 className={`max-w-[80%] whitespace-pre-wrap rounded-xl px-4 py-3 text-sm ${
                   m.role === "user"
                     ? "self-end bg-accent-muted text-white ml-auto"
                     : "self-start bg-surface-raised text-gray-100"}`}>
              {m.content}
            </div>
          ))}
          {summary && (
            <div className="self-start max-w-[80%] rounded-xl border border-accent/40 bg-surface-raised p-4">
              <div className="text-sm font-semibold">Your proposal is ready.</div>
              <div className="mt-2 text-xs text-gray-400">
                Requirement coverage: {summary.qa_pass}/{summary.qa_pass + summary.qa_fail} QA gates ·
                Evidence-backed claims: {summary.claims} · Unsupported: {summary.unsupported}
              </div>
              <div className="mt-2 text-xs">
                {summary.sections} sections · {summary.word_count} words ·{" "}
                Budget ${Number(summary.budget_total).toLocaleString()} within ${Number(summary.ceiling).toLocaleString()} ceiling
              </div>
              <div className="mt-3 flex gap-2 text-xs">
                <a href={downloadUrl("proj-1-proposal_docx")}
                   className="rounded bg-accent px-3 py-1.5 font-medium text-black">
                  DOCX
                </a>
                <a href={downloadUrl("proj-1-proposal_pdf")}
                   className="rounded bg-accent px-3 py-1.5 font-medium text-black">
                  PDF
                </a>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* input bar */}
        <div className="border-t border-surface-border p-4">
          <div className="flex items-end gap-2 max-w-3xl mx-auto">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
              placeholder="We need funding for an after-school STEM program in Atlanta…"
              rows={2}
              className="flex-1 resize-none rounded-xl border border-surface-border bg-surface-raised px-4 py-3 text-sm outline-none focus:border-accent"
            />
            <select
              aria-label="Model"
              value={modelChoice}
              onChange={(e) => setModelChoice(e.target.value)}
              className="rounded-lg border border-surface-border bg-surface-raised px-2 py-2 text-xs"
            >
              <option value="auto">Auto — Recommended</option>
              {models.map((m) => (
                <option key={m.model_id} value={m.model_id} disabled={!m.enabled}>
                  {m.model_id.split("/")[1]} · {m.cost_tier} cost
                </option>
              ))}
            </select>
            <button
              onClick={send}
              disabled={busy}
              className="rounded-xl bg-accent px-5 py-3 text-sm font-semibold text-black disabled:opacity-50"
            >
              {busy ? "Working…" : "Send"}
            </button>
          </div>
        </div>
      </section>

      {/* right work-preview panel */}
      <aside className="w-64 shrink-0 border-l border-surface-border bg-surface-raised p-4 hidden md:block">
        <div className="text-xs uppercase tracking-wide text-gray-500">Work</div>
        {!progress && <div className="mt-3 text-sm text-gray-500">Idle</div>}
        {progress && (
          <div className="mt-2 space-y-1.5 text-xs">
            <div className="text-gray-400">
              {checked}/{total} tasks done
            </div>
            {Object.entries(progress.by_state).map(([state, n]) => (
              <div key={state} className="flex justify-between text-gray-500">
                <span>{state}</span><span>{n}</span>
              </div>
            ))}
            <div className="mt-3 border-t border-surface-border pt-2 text-gray-300">
              {progress.tasks
                .filter((t) => t.state !== "SUCCEEDED")
                .slice(0, 5)
                .map((t) => {
                  const step = t.capability_id.split(".")[1];
                  return (
                    <div key={t.task_id} className="py-0.5 flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                      {WORK_LABELS[step] ?? t.capability_id}
                    </div>
                  );
                })}
            </div>
          </div>
        )}
      </aside>
    </main>
  );
}
