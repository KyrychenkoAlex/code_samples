import React, { useEffect, useState } from "react";

import AuthContext, {
  ForgotPasswordPropsType,
  LoginPropsType,
  RegisterPropsType
} from "./auth-context";

import { ResponseErrorType } from "@/api/shop/apiClient";

import { getAuthenticatedCustomerRequest } from "@/api/shop/endpoints/auth/customer";
import { postLoginRequest } from "@/api/shop/endpoints/auth/login";
import { postLogoutRequest } from "@/api/shop/endpoints/auth/logout";
import { postRegisterRequest } from "@/api/shop/endpoints/auth/register";
import {
  ForgotPasswordResponseSuccessType,
  postForgotPasswordRequest
} from "@/api/shop/endpoints/auth/forgot-password";
import {
  postResetPasswordRequest,
  ResetPasswordRequestDataType,
  ResetPasswordResponseSuccessType
} from "@/api/shop/endpoints/auth/reset-password";
import { getSocialRedirectRequest, loginByTokenRequest } from "@/api/shop/endpoints/auth/oauth";

export interface UserType {
  id: number;
  email: string;
  full_name_initials: string;
}

interface Props {
  checkOnInit?: boolean;
  children: React.ReactNode;
}

const AuthProvider: React.FC<Props> = ({
                                         checkOnInit = true,
                                         children
                                       }) => {
  const [authState, setAuthState] = useState<{
    user: null | UserType;
    authenticated: null | boolean;
    isAuthenticating: boolean;
  }>({ user: null, authenticated: null, isAuthenticating: true });

  const [isLoggedOuting, setIsLoggedOuting] = useState<boolean>(false);

  const {
    isAuthenticating,
    authenticated,
    user
  } = authState;

  useEffect(() => {
    if (checkOnInit) {
      checkAuthentication();
    }
  }, [checkOnInit]);

  const checkAuthentication = (): Promise<boolean> => {
    return new Promise(async (resolve, reject) => {
      if (authenticated === null) {
        try {
          const result = await revalidateAuthState();
          return resolve(result);
        } catch (error: ResponseErrorType) {
          setAuthState({ user: null, authenticated: false, isAuthenticating: false });
          return resolve(false);
        }
      } else {
        return resolve(authenticated);
      }
    });
  };

  const revalidateAuthState = (): Promise<boolean | ResponseErrorType> => {
    return new Promise(async (resolve, reject) => {
      try {
        const user = await getAuthenticatedCustomerRequest();

        setAuthState({ user, authenticated: true, isAuthenticating: false });

        return resolve(true);
      } catch (error) {
        setAuthState({ user: null, authenticated: false, isAuthenticating: false });
        return reject(error);
      }
    });
  };

  const login = (
    props: LoginPropsType
  ): Promise<boolean | ResponseErrorType> => {
    return new Promise(async (resolve, reject) => {
      try {
        await postLoginRequest(props);
        await revalidateAuthState();
        return resolve(true);
      } catch (error) {
        return reject(error);
      }
    });
  };

  const loginByToken = (
    token: string
  ): Promise<{success: boolean; message: string}> => {
    return new Promise(async (resolve, reject) => {
      try {
        const data = await loginByTokenRequest(token);
        await revalidateAuthState();
        return resolve(data);
      } catch (error) {
        return reject(error);
      }
    });
  };

  const register = (
    props: RegisterPropsType
  ): Promise<boolean | ResponseErrorType> => {
    return new Promise(async (resolve, reject) => {
      try {
        await postRegisterRequest(props);
        await revalidateAuthState();
        return resolve(true);
      } catch (error) {
        return reject(error);
      }
    });
  };

  const forgotPassword = (props: ForgotPasswordPropsType): Promise<ForgotPasswordResponseSuccessType> => {
    return new Promise(async (resolve, reject) => {
      try {
        const result = await postForgotPasswordRequest(props);
        resolve(result);
      } catch (error: ResponseErrorType) {
        reject(error);
      }
    });
  };

  const resetPassword = (props: ResetPasswordRequestDataType): Promise<ResetPasswordResponseSuccessType> => {
    return new Promise(async (resolve, reject) => {
      try {
        const result = await postResetPasswordRequest(props);
        resolve(result);
      } catch (error) {
        reject(error);
      }
    });
  };

  const logout = (): Promise<boolean | ResponseErrorType> => {
    return new Promise(async (resolve, reject) => {
      try {
        setIsLoggedOuting(true);
        await postLogoutRequest();
        setAuthState({ user: null, authenticated: false, isAuthenticating: false });
        setIsLoggedOuting(false);
        return resolve(true);
      } catch (error) {
        setIsLoggedOuting(false);
        return reject(error);
      }
    });
  };

  const getSocialRedirect = (provider: string): Promise<{ url: string }> => {
    return new Promise(async (resolve, reject) => {
      try {
        const data = await getSocialRedirectRequest(provider);
        return resolve(data);
      } catch (error) {
        return reject(error);
      }
    });
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        authenticated,
        isAuthenticating,
        isLoggedOuting,
        login,
        loginByToken,
        getSocialRedirect,
        register,
        forgotPassword,
        resetPassword,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
