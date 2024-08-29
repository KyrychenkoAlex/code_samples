import {getUserByToken} from "../services/authService";

export const socketAuthMiddleware = async (socket, next) => {
    const rawToken = socket.handshake.headers['authorization'];
    const sender = await getUserByToken(rawToken);
    if (!sender) {
        next(new Error('Authentication error'));
    }
    socket.sender = sender;
    return next();
};