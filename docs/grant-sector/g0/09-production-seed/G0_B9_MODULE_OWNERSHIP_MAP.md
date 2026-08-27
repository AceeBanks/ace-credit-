{
  "chapter": "B9.C8",
  "status": "FROZEN",
  "topology": "MODULAR_MONOLITH_FIRST",
  "modules": [
    {"module": "api", "owner": "product", "data_ownership": "none", "auth": "user session to tenant scope", "scaling_trigger": "api volume"},
    {"module": "personal_hermes", "owner": "product", "data_ownership": "hermes memory (curated, non-authoritative)", "auth": "user to tenant", "scaling_trigger": "client count"},
    {"module": "ceo_hermes", "owner": "product", "data_ownership": "hermes memory (curated)", "auth": "user/ceo to tenant+project", "scaling_trigger": "project count"},
    {"module": "worker_runtime", "owner": "platform", "data_ownership": "results only", "auth": "worker principal to task scope", "scaling_trigger": "fanout"},
    {"module": "policy_capability", "owner": "platform", "data_ownership": "postgres policy tables", "auth": "PDP internal, deny-by-default", "scaling_trigger": "auth volume"},
    {"module": "model_gateway", "owner": "platform", "data_ownership": "execution audit refs", "auth": "PDP-gated, egress policy", "scaling_trigger": "model calls"},
    {"module": "tool_gateway", "owner": "platform", "data_ownership": "none", "auth": "PDP-verified decisions only", "scaling_trigger": "tool calls"},
    {"module": "source_ingestion", "owner": "sector", "data_ownership": "postgres snapshot meta + object storage raw", "auth": "service identity", "scaling_trigger": "source volume"},
    {"module": "evidence_research", "owner": "sector", "data_ownership": "postgres evidence + object payloads", "auth": "service identity + project scope", "scaling_trigger": "research volume"},
    {"module": "application_drafting", "owner": "sector", "data_ownership": "postgres project + artifacts", "auth": "worker task scope", "scaling_trigger": "drafts"},
    {"module": "artifact_service", "owner": "sector", "data_ownership": "object storage", "auth": "project scope", "scaling_trigger": "artifact volume"},
    {"module": "evaluation", "owner": "platform", "data_ownership": "postgres eval results", "auth": "eval-only identity", "scaling_trigger": "eval runs"},
    {"module": "scheduler_jobs", "owner": "platform", "data_ownership": "postgres job meta", "auth": "service identity", "scaling_trigger": "job volume"},
    {"module": "postgres", "owner": "infra", "data_ownership": "canonical", "auth": "network-isolated", "scaling_trigger": "data volume"},
    {"module": "object_storage", "owner": "infra", "data_ownership": "immutable payloads", "auth": "IAM-scoped", "scaling_trigger": "payload volume"},
    {"module": "redis_queue", "owner": "infra", "data_ownership": "transport only", "auth": "network-isolated", "scaling_trigger": "message volume"},
    {"module": "graph_vector", "owner": "infra", "data_ownership": "rebuildable projection", "auth": "service identity", "scaling_trigger": "query volume"}
  ],
  "extraction_rule": "start modular monolith; extract only on measured triggers (sustained API volume, ingestion backpressure, model-gateway isolation, eval latency impact)"
}
