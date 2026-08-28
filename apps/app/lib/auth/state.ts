export type AuthActionState = {
  status: "idle" | "error" | "success";
  message?: string;
  errors?: { email?: string; password?: string };
};

export const INITIAL_AUTH_STATE: AuthActionState = { status: "idle" };
