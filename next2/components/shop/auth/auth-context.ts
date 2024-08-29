import React from "react";
import { ForgotPasswordResponseSuccessType } from "@/api/shop/endpoints/auth/forgot-password";
import { ResetPasswordResponseSuccessType } from "@/api/shop/endpoints/auth/reset-password";

export interface LoginPropsType {
  email: string;
  password: string;
  remember: boolean;
}

export interface RegisterPropsType {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  password_confirmation: string;
}

export interface ForgotPasswordPropsType {
  email: string;
}

export interface ResetPasswordPropsType {
  email: string;
  password: string;
  password_confirmation: string;
}

export interface ContextProps {
  user: null | any;
  authenticated: null | boolean;
  isAuthenticating: boolean;
  isLoggedOuting: boolean;
  login: (props: LoginPropsType) => Promise<boolean>;
  loginByToken: (token: string) => Promise<{success: true; message: string;}>;
  register: (props: RegisterPropsType) => Promise<boolean>;
  getSocialRedirect: (provider: string) => Promise<{ url: string }>;
  forgotPassword: (props: ForgotPasswordPropsType) => Promise<ForgotPasswordResponseSuccessType>;
  resetPassword: (props: ResetPasswordPropsType) => Promise<ResetPasswordResponseSuccessType>;
  logout: () => Promise<boolean>;
}

const AuthContext = React.createContext<ContextProps | undefined>(undefined);

export default AuthContext;
