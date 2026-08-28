"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  ChatResult,
  ConversationMeta,
  Message,
  ModelLite,
  ModelSelection,
  ProduceSummary,
  Progress,
  ArtifactMeta,
  downloadUrl,
  getConversations,
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

interface UploadedFile {
  attachment_id: string;
  filename: string;
  mime_type: string;
  file_size_bytes: number;
  parser_status: string;
}

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
  const [deliverables, setDeliverables] = useState<ArtifactMeta[]>([]);
  const [conversations, setConversations] = useState<ConversationMeta[]>([]);
  const [resolvedModel, setResolvedModel] = useState<string | null>(null);
  const [modelSelectionMode, setModelSelectionMode] = useState<string>("AUTO");
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getModels().then(setModels).catch(() => setModels([]));
    getConversations().then(setConversations).catch(() => setConversations([]));
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, summary, progress]);

  const buildModelSelection = useCallback((): ModelSelection => {
    if (modelChoice === "auto") {
      return { mode: "AUTO", allow_fallback: true };
    }
    return {
      mode: "MANUAL",
      model_id: modelChoice,
      allow_fallback: true,
    };
  }, [modelChoice]);

  const poll = useCallback(async (project: string, convId: string) => {
    try {
      const p = await getProgress(project);
      setProgress(p);
      if (p.by_state.SUCCEEDED === p.task_count && p.task_count > 0) {
        const ms = buildModelSelection();
        const s = await produce(project, ms.mode === "MANUAL", ms);
        setSummary(s);
        const arts = await getDeliverables(project);
        setDeliverables(arts);
        const msgs = await getMessages(convId);
        setMessages(msgs);
        setBusy(false);
        return;
      }
      if (busy) {
        setTimeout(() => poll(project, convId), 1500);
      }
    } catch {
      if (busy) {
        setTimeout(() => poll(project, convId), 2000);
      }
    }
  }, [busy, buildModelSelection]);

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    setUploading(true);
    for (const file of Array.from(files)) {
      const formData = new FormData();
      formData.append("file", file);
      try {
        const res = await fetch(
          `/api/attachments/upload?project_id=${projectId}`,
          {
            method: "POST",
            headers: { "X-Principal": "client-1" },
            body: formData,
          },
        );
        if (res.ok) {
          const data = await res.json();
          setUploadedFiles((prev) => [...prev, data]);
        }
      } catch {
        // silent — upload is optional enrichment
      }
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  async function send() {
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setBusy(true);
    setSummary(null);
    const ms = buildModelSelection();
    try {
      const r: ChatResult = await postChat(text, ms);
      setConv(r.conversation_id);
      setProjectId(r.project_id);
      setResolvedModel(r.resolved_model_id);
      setModelSelectionMode(r.model_selection_mode);
      setMessages(await getMessages(r.conversation_id));
      getConversations().then(setConversations).catch(() => {});
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

  function newChat() {
    setMessages([]);
    setSummary(null);
    setProgress(null);
    setConv("");
    setProjectId("proj-1");
    setResolvedModel(null);
    setModelSelectionMode("AUTO");
    setDeliverables([]);
    setUploadedFiles([]);
  }

  async function loadHistory(c: ConversationMeta) {
    setConv(c.conversation_id);
    setProjectId(c.project_id ?? "proj-1");
    setSummary(null);
    setProgress(null);
    setBusy(false);
    setUploadedFiles([]);
    try {
      const msgs = await getMessages(c.conversation_id);
      setMessages(msgs);
      if (c.project_id) {
        const arts = await getDeliverables(c.project_id);
        setDeliverables(arts);
        const p = await getProgress(c.project_id);
        setProgress(p);
      }
    } catch {
      // backend may not be running
    }
  }

  const checked = Object.entries(progress?.by_state ?? {})
    .filter(([k]) => ["SUCCEEDED", "FAILED"].includes(k))
    .reduce((a, [, v]) => a + v, 0);
  const total = progress?.task_count ?? 0;

  const hasMaterialGaps = summary && (summary.unsupported > 0 || summary.qa_fail > 0);
  const isReadyForReview = summary && summary.qa_fail === 0 && summary.status === "SUBMISSION_READY_MOCK";

  return (
    <main className="flex h-screen">
      {/* left sidebar */}
      <aside className="w-56 shrink-0 border-r border-surface-border bg-surface-raised p-3 flex flex-col gap-2">
        <button
          onClick={newChat}
          className="rounded-lg bg-accent px-3 py-2 text-sm font-medium text-black hover:opacity-90"
        >
          + New Chat
        </button>
        <div className="text-xs uppercase tracking-wide text-gray-500 pt-3">
          History
        </div>
        <div className="flex flex-col gap-1 text-sm overflow-y-auto max-h-48">
          {conversations.length === 0 && (
            <div className="text-gray-500 px-1">No conversations yet</div>
          )}
          {conversations.map((c) => (
            <button
              key={c.conversation_id}
              onClick={() => loadHistory(c)}
              className={`rounded px-2 py-1 text-left hover:bg-surface-border ${
                conv === c.conversation_id ? "bg-surface-border" : ""
              }`}
            >
              {c.title?.slice(0, 40) ?? c.conversation_id}
            </button>
          ))}
        </div>
        <div className="text-xs uppercase tracking-wide text-gray-500 pt-3">
          Deliverables
        </div>
        <div className="flex flex-col gap-1 text-sm">
          {deliverables.length === 0 && (
            <div className="text-gray-500 px-1">None yet</div>
          )}
          {deliverables.map((a) => (
            <a key={a.artifact_id} href={downloadUrl(a.artifact_id)}
               className="rounded px-2 py-1 hover:bg-surface-border">
              {a.kind.replace("proposal_", "Proposal ").replace("_", " ")}
            </a>
          ))}
        </div>
        {uploadedFiles.length > 0 && (
          <>
            <div className="text-xs uppercase tracking-wide text-gray-500 pt-3">
              Attachments
            </div>
            <div className="flex flex-col gap-1 text-sm">
              {uploadedFiles.map((f) => (
                <div key={f.attachment_id}
                     className="rounded px-2 py-1 text-green-400 text-xs truncate">
                  {f.filename}
                  {f.parser_status === "PARSE_ERROR" && " ⚠"}
                </div>
              ))}
            </div>
          </>
        )}
        <div className="mt-auto text-[11px] text-gray-600 px-1">
          DEV_PILOT — Submission disabled
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
                     : "self-start bg-surface-raised text-gray-100"
                 }`}>
              {m.content}
            </div>
          ))}
          {summary && (
            <div className="self-start max-w-[80%] rounded-xl border border-accent/40 bg-surface-raised p-4">
              {isReadyForReview ? (
                <div className="text-sm font-semibold text-green-400">
                  Proposal is ready for review.
                </div>
              ) : hasMaterialGaps ? (
                <div className="text-sm font-semibold text-amber-400">
                  Proposal needs your input — material gaps remain.
                </div>
              ) : (
                <div className="text-sm font-semibold text-gray-300">
                  Proposal generated ({summary.status}).
                </div>
              )}

              {hasMaterialGaps && (
                <div className="mt-2 text-xs text-amber-300/80 bg-amber-900/30 rounded p-2">
                  There are {summary.unsupported} unresolved material claim(s) and {summary.qa_fail} QA issue(s).
                  The proposal cannot be marked ready until these are resolved.
                </div>
              )}

              <div className="mt-2 text-xs text-gray-400">
                Requirement coverage: {summary.qa_pass}/{summary.qa_pass + summary.qa_fail} QA gates ·
                Evidence-backed claims: {summary.claims} · Unresolved: {summary.unsupported}
              </div>
              <div className="mt-1 text-xs text-gray-500">
                Generation: {summary.generation_mode}
                {modelSelectionMode !== "AUTO" && resolvedModel
                  ? ` · Model: ${resolvedModel}`
                  : ""}
              </div>
              <div className="mt-2 text-xs">
                {summary.sections} sections · {summary.word_count} words ·{" "}
                Budget ${Number(summary.budget_total).toLocaleString()} within ${Number(summary.ceiling).toLocaleString()} ceiling
              </div>
              <div className="mt-3 flex gap-2 text-xs">
                {deliverables.map((a) => (
                  <a key={a.artifact_id}
                     href={downloadUrl(a.artifact_id)}
                     className="rounded bg-accent px-3 py-1.5 font-medium text-black">
                    {a.kind === "proposal_docx" ? "DOCX" : "PDF"}
                  </a>
                ))}
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* input bar */}
        <div className="border-t border-surface-border p-4">
          <div className="flex items-end gap-2 max-w-3xl mx-auto">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf,.docx,.txt"
              className="hidden"
              multiple
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={busy || uploading}
              className="rounded-lg border border-surface-border bg-surface-raised px-3 py-3 text-sm hover:bg-surface-border disabled:opacity-50"
              title="Upload PDF, DOCX, or TXT"
            >
              {uploading ? "…" : "📎"}
            </button>
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
