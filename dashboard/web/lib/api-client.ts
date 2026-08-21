/**
 * API Client - Generic fetch wrapper for Elysia REST API
 * Handles error handling, logging, retries, and type safety
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";
const REQUEST_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 1;

/**
 * Fetch options extending standard RequestInit
 */
export interface FetchOptions extends RequestInit {
  timeout?: number;
  retries?: number;
}

/**
 * Error class for API errors
 */
export class ApiError extends Error {
  constructor(
    public code: string,
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Log function - only logs in development mode
 */
function log(...args: unknown[]): void {
  if (typeof window !== "undefined") {
    // Client-side
    if (process.env.NODE_ENV === "development") {
      console.log("[API Client]", ...args);
    }
  }
}

/**
 * Log error function - logs errors in dev mode
 */
function logError(...args: unknown[]): void {
  if (typeof window !== "undefined") {
    // Client-side
    if (process.env.NODE_ENV === "development") {
      console.warn("[API Client Warning]", ...args);
    }
  }
}

/**
 * Generic fetch wrapper for API calls
 * @template T - The response data type
 * @param endpoint - API endpoint (will be prepended with base URL)
 * @param options - Fetch options (timeout, retries, headers, etc.)
 * @returns Promise resolving to typed response data
 * @throws ApiError on network errors, timeouts, or non-200 status codes
 */
export async function fetchAPI<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const {
    timeout = REQUEST_TIMEOUT,
    retries = MAX_RETRIES,
    ...fetchOptions
  } = options;

  // Ensure endpoint starts with /
  const normalizedEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${BASE_URL}${normalizedEndpoint}`;

  // Set default headers
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...fetchOptions.headers,
  };

  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  let lastError: Error | null = null;
  let attemptCount = 0;

  while (attemptCount <= retries) {
    try {
      attemptCount++;

      log(`${fetchOptions.method || "GET"} ${url} (attempt ${attemptCount})`);

      const response = await fetch(url, {
        ...fetchOptions,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Log response status in dev mode
      log(`Response: ${response.status}`);

      // Handle non-200 status codes
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        let errorData: unknown;

        try {
          errorData = await response.json();
          if (typeof errorData === "object" && errorData !== null) {
            const errorObj = errorData as Record<string, unknown>;
            if (typeof errorObj.error === "string") {
              errorMessage = errorObj.error;
            }
          }
        } catch {
          // Could not parse error response as JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }

        throw new ApiError(
          `HTTP_${response.status}`,
          response.status,
          errorMessage
        );
      }

      // Parse response
      const data = await response.json();
      log("Response data:", data);

      return data as T;
    } catch (error) {
      clearTimeout(timeoutId);
      lastError = error instanceof Error ? error : new Error(String(error));

      // Check if it's a timeout error
      if (lastError instanceof DOMException && lastError.name === "AbortError") {
        throw new ApiError(
          "TIMEOUT",
          408,
          `Request timeout after ${timeout}ms`
        );
      }

      // Check if it's an API error (don't retry)
      if (error instanceof ApiError) {
        throw error;
      }

      // Network error - retry if attempts remaining
      if (attemptCount <= retries) {
        logError(`Network error: ${lastError.message}. Retrying...`);
        // Wait a bit before retrying
        await new Promise((resolve) => setTimeout(resolve, 500));
        continue;
      }

      // No more retries, throw the error
      throw new ApiError(
        "NETWORK_ERROR",
        0,
        lastError.message || "Network error occurred"
      );
    }
  }

  // Should not reach here, but just in case
  throw lastError || new ApiError("UNKNOWN_ERROR", 0, "Unknown error occurred");
}

/**
 * Fetch a single resource by ID
 */
export async function fetchById<T>(
  resource: string,
  id: string
): Promise<T> {
  return fetchAPI<T>(`/api/${resource}/${id}`);
}

/**
 * Fetch a list of resources with optional query parameters
 */
export async function fetchList<T>(
  resource: string,
  params?: Record<string, string | number | boolean>
): Promise<T> {
  const queryString = new URLSearchParams();

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        queryString.append(key, String(value));
      }
    });
  }

  const url = `/api/${resource}${queryString.toString() ? `?${queryString.toString()}` : ""}`;
  return fetchAPI<T>(url);
}

/**
 * Create a new resource via POST
 */
export async function createResource<T>(
  resource: string,
  data: unknown
): Promise<T> {
  return fetchAPI<T>(`/api/${resource}`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Update a resource via PATCH
 */
export async function updateResource<T>(
  resource: string,
  id: string,
  data: unknown
): Promise<T> {
  return fetchAPI<T>(`/api/${resource}/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

/**
 * Delete a resource via DELETE
 */
export async function deleteResource(
  resource: string,
  id: string
): Promise<void> {
  await fetchAPI(`/api/${resource}/${id}`, {
    method: "DELETE",
  });
}
