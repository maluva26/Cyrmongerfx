const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1").replace(/\/+$/, "");

export type ApiUser = {
  user_id: string;
  email: string;
  full_name?: string;
  role: string;
};

export type AuthSession = { access: string; user: ApiUser };

export class ApiError extends Error {
  constructor(message: string, public readonly status: number, public readonly code?: string) {
    super(message);
    this.name = "ApiError";
  }
}

const sessionListeners = new Set<(session: AuthSession | null) => void>();
let refreshInFlight: Promise<AuthSession | null> | null = null;

function notifySession(session: AuthSession | null) {
  sessionListeners.forEach((listener) => listener(session));
}

export function subscribeToSession(listener: (session: AuthSession | null) => void) {
  sessionListeners.add(listener);
  return () => sessionListeners.delete(listener);
}

function asSession(value: unknown): AuthSession | null {
  if (!value || typeof value !== "object") return null;
  const data = value as Record<string, unknown>;
  const user = data.user as Record<string, unknown> | undefined;
  if (
    typeof data.access !== "string" ||
    !user ||
    typeof user.user_id !== "string" ||
    typeof user.email !== "string" ||
    typeof user.role !== "string"
  ) return null;

  return { access: data.access, user: user as ApiUser };
}

async function refreshSession(): Promise<AuthSession | null> {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      try {
        const response = await fetch(`${API_BASE}/auth/refresh`, {
          method: "POST",
          credentials: "include",
        });
        if (!response.ok) {
          if (response.status === 401) notifySession(null);
          return null;
        }
        const session = asSession(await response.json());
        notifySession(session);
        return session;
      } catch {
        return null;
      } finally {
        refreshInFlight = null;
      }
    })();
  }
  return refreshInFlight;
}

export function restoreSession() {
  return refreshSession();
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function errorMessage(value: unknown): { message: string; code?: string } {
  if (typeof value === "string") return { message: value };
  if (isRecord(value)) {
    const error = isRecord(value.error) ? value.error : undefined;
    if (error && typeof error.message === "string") {
      return { message: error.message, code: typeof error.code === "string" ? error.code : undefined };
    }
    if (typeof value.detail === "string") return { message: value.detail };
    if (typeof value.message === "string") return { message: value.message };

    const messages = Object.values(value).flatMap((item) => {
      if (typeof item === "string") return [item];
      if (Array.isArray(item)) return item.filter((entry): entry is string => typeof entry === "string");
      return [];
    });
    if (messages.length) return { message: messages.join(" ") };
  }
  return { message: "Request failed. Please try again." };
}

async function readResponse(response: Response): Promise<unknown> {
  if (response.status === 204) return null;
  const body = await response.text();
  if (!body) return null;
  try {
    return JSON.parse(body) as unknown;
  } catch {
    return body;
  }
}

async function request<T = any>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
  hasRetried = false,
): Promise<T> {
  const headers = new Headers(options.headers);
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
  if (options.body && !isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (response.status === 401 && token && !hasRetried) {
    const session = await refreshSession();
    if (session) return request<T>(path, options, session.access, true);
  }

  const data = await readResponse(response);
  if (!response.ok) {
    const error = errorMessage(data);
    throw new ApiError(error.message, response.status, error.code);
  }
  return data as T;
}

async function download(path: string, token?: string | null, hasRetried = false): Promise<Blob> {
  const headers = new Headers();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_BASE}${path}`, { headers, credentials: "include" });

  if (response.status === 401 && token && !hasRetried) {
    const session = await refreshSession();
    if (session) return download(path, session.access, true);
  }

  if (!response.ok) {
    const error = errorMessage(await readResponse(response));
    throw new ApiError(error.message, response.status, error.code);
  }
  return response.blob();
}

export const api = {
  get: <T = any>(path: string, token?: string | null) => request<T>(path, {}, token),
  post: <T = any>(path: string, body: unknown, token?: string | null) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }, token),
  patch: <T = any>(path: string, body: unknown, token?: string | null) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }, token),
  delete: <T = any>(path: string, token?: string | null) =>
    request<T>(path, { method: "DELETE" }, token),
  upload: <T = any>(path: string, formData: FormData, token?: string | null) =>
    request<T>(path, { method: "POST", body: formData }, token),
  download: (path: string, token?: string | null) => download(path, token),
};
