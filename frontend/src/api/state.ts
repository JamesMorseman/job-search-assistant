export type DataStatus = "idle" | "loading" | "success" | "error" | "not-found";

export type DataState<T> = {
  status: DataStatus;
  data: T | null;
  error: string | null;
};

export const idleState = <T>(): DataState<T> => ({
  status: "idle",
  data: null,
  error: null,
});

export const loadingState = <T>(data: T | null = null): DataState<T> => ({
  status: "loading",
  data,
  error: null,
});

export const successState = <T>(data: T): DataState<T> => ({
  status: "success",
  data,
  error: null,
});

export const errorState = <T>(error: string, data: T | null = null): DataState<T> => ({
  status: "error",
  data,
  error,
});

export const notFoundState = <T>(): DataState<T> => ({
  status: "not-found",
  data: null,
  error: null,
});
