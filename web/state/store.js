export const AUTO_VALUE = "auto";
export const TOKEN_STORAGE_KEY = "sistemaPeticoesApiToken";
export const THEME_STORAGE_KEY = "sistemaPeticoesTheme";
export const TOKEN_TTL_MS = 12 * 60 * 60 * 1000;

export const state = {
  pieceTypes: [],
  profiles: [],
  defaultProfileId: "judicial-inicial-jef",
  limits: {
    max_text_chars: 500000,
    max_file_bytes: 25 * 1024 * 1024,
    max_total_upload_bytes: 200 * 1024 * 1024,
    max_upload_files: 20,
    llm_required: true,
    llm_allow_client_provider: true,
    llm_allowed_providers: ["mock", "ollama", "openai", "anthropic"],
    llm_default_provider: "mock",
    llm_default_model: "",
    llm_external_provider: false,
    llm_requires_external_consent: false,
  },
  theme: "system",
};

export function setProfiles(items, defaultProfileId) {
  state.profiles = items;
  state.defaultProfileId = defaultProfileId || "judicial-inicial-jef";
}

export function setPieceTypes(items) {
  state.pieceTypes = items;
}

export function setLimits(limits) {
  state.limits = { ...state.limits, ...limits };
}

export function setTheme(theme) {
  state.theme = theme;
}
