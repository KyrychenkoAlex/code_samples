import axios, {AxiosInstance, AxiosRequestConfig} from "axios";
import {getCookie, removeCookies, setCookies} from 'cookies-next';

const {NEXT_PUBLIC_API_HOST} = process.env;

axios.defaults.baseURL = NEXT_PUBLIC_API_HOST;

const singleton = Symbol();
const singletonEnforcer = Symbol();


class ApiService {
    private session: AxiosInstance;

    constructor({enforcer}) {
        if (enforcer && enforcer !== singletonEnforcer) {
            throw new Error('Cannot construct singleton');
        }

        const token = getCookie('accessToken');

        this.session = axios.create({
            baseURL: NEXT_PUBLIC_API_HOST,
            headers: {
                'Authorization': token
            }
        });
    }

    static get instance() {
        if (!this[singleton]) {
            this[singleton] = new ApiService(singletonEnforcer as any);
        }

        return this[singleton];
    }

    get = (url: string, config?: AxiosRequestConfig) => this.session.get(url, config);
    post = (url: string, data?: any, config?: AxiosRequestConfig) => this.session.post(url, data, config);
    put = (url: string, data?: any, config?: AxiosRequestConfig) => this.session.put(url, data, config);
    patch = (url: string, data?: any, config?: AxiosRequestConfig) => this.session.patch(url, data, config);
    delete = (url: string, config?: AxiosRequestConfig) => this.session.delete(url, config);
    setToken = (accessToken: string, options = {}) => {
        this.session.defaults.headers['Authorization'] = accessToken;
        setCookies('accessToken', accessToken, options);
    };

    getToken = (options = {}) => {
        return getCookie('accessToken', options);
    };

    removeToken = (options = {}) => {
        return removeCookies('accessToken', options);
    };
}

export default ApiService.instance;
