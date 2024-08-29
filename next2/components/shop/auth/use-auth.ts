import React from "react";
import AuthContext, { ContextProps } from "./auth-context";

interface useAuthReturn<T> extends ContextProps {
  user: T;
}

export default function useAuth<T = null | any>(): useAuthReturn<T> {
  const context = React.useContext(AuthContext);

  if (!context)
    throw new Error("useAuth should only be used inside <AuthProvider />");

  return context;
}
