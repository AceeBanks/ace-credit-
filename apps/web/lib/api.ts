// Thin typed client for the FastAPI backend (routed via /api rewrites).
// The client stays ignorant of model infrastructure (Appendix A §10):
// it sends task intent; the backend decides eligibility/routing.

export interface ModelSelection {
  mode: "AUTO" | "MANUAL";
  provider_id?: string;
  model_id?: string;
  allow_fallback: boolean;
}

export interface ChatResult {
  conversation_id: string;
  intent_id: string;
  reply: string;
  plan_id: string | null;
  task_ids: string[];
  project_id: string;
  model_selection_mode: string;
  resolved_model_id: string | null;
}

export interface Message {
  message_id: string;
  role: string;
  content: string;
}

export interface TaskState {
  task_id: string;
  state: string;
  capability_id: string;
}

export interface Progress {
  project_id: string;
  task_count: number;
  by_state: Record<string, number>;
  tasks: TaskState[];
}

export interface ArtifactMeta {
  artifact_id: string;
  kind: string;
  version_number: number;
}

export interface ProduceSummary {
  status: string;
  readiness_state: string;
  generation_mode: string;
  sections: number;
  word_count: number;
  claims: number;
  claim_counts: Record<string, number>;
  unsupported: number;
  qa_pass: number;
  qa_fail: number;
  budget_total: string;
  ceiling: string;
  within_ceiling: boolean;
  submission_enabled: boolean;
}

export interface ModelLite {
  model_id: string;
  provider_id: string;
  context_window_tokens: number;
  max_output_tokens: number;
  cost_tier: string;
  quality_tier: string;
  availability: string;
  enabled: boolean;
}

export interface ConversationMeta {
  conversation_id: string;
  tenant_id: string;
  client_actor_id: string;
  title: string | null;
  project_id: string | null;
  created_at: string;
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail.slice(0, 200)}`);
  }
  return res.json() as Promise<T>;
}

const HEADERS = { "X-Principal": "client-1", "Content-Type": "application/json" };

export async function postChat(
  message: string,
  modelSelection?: ModelSelection,
): Promise<ChatResult> {
  return json<ChatResult>(
    await fetch("/api/chat", {
      method: "POST",
      headers: HEADERS,
      body: JSON.stringify({
        message,
        requested_capabilities: [],
        model_selection: modelSelection ?? { mode: "AUTO", allow_fallback: true },
      }),
    }),
  );
}

export async function getMessages(conversationId: string): Promise<Message[]> {
  const data = await json<{ messages: Message[] }>(
    await fetch(`/api/chat/${conversationId}/messages`, { headers: HEADERS }),
  );
  return data.messages;
}

export async function getProgress(projectId: string): Promise<Progress> {
  return json<Progress>(
    await fetch(`/api/projects/${projectId}/progress`, { headers: HEADERS }),
  );
}

export async function produce(
  projectId: string,
  liveModel = false,
  modelSelection?: ModelSelection,
): Promise<ProduceSummary> {
  return json<ProduceSummary>(
    await fetch(`/api/projects/${projectId}/produce`, {
      method: "POST",
      headers: HEADERS,
      body: JSON.stringify({
        project_id: projectId,
        live_model: liveModel,
        model_selection: modelSelection,
      }),
    }),
  );
}

export async function getDeliverables(projectId: string): Promise<ArtifactMeta[]> {
  const data = await json<{ artifacts: ArtifactMeta[] }>(
    await fetch(`/api/projects/${projectId}/deliverables`, { headers: HEADERS }),
  );
  return data.artifacts;
}

export async function getModels(): Promise<ModelLite[]> {
  const data = await json<{ models: ModelLite[] }>(
    await fetch("/api/models", { headers: HEADERS }),
  );
  return data.models;
}

export function downloadUrl(artifactId: string): string {
  return `/api/artifacts/${artifactId}/download?principal_id=client-1`;
}

export async function getConversations(): Promise<ConversationMeta[]> {
  const data = await json<{ conversations: ConversationMeta[] }>(
    await fetch("/api/conversations", { headers: HEADERS }),
  );
  return data.conversations;
}
