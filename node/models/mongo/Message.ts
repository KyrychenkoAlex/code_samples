import mongoose from "mongoose";
import paginate from 'mongoose-paginate-v2';

export interface MessageInterface {
    messageUUID: string
    roomUUID: string
    senderId?: string,
    message: string
}

const MessageSchema = new mongoose.Schema(
    {
        messageUUID: String,
        roomUUID: String,
        senderId: String,
        message: String
    },{
        timestamps: true
    }
);

MessageSchema.plugin(paginate);

interface MessageDocument extends mongoose.Document, MessageInterface {}

const Message = mongoose.model<
    MessageDocument,
    mongoose.PaginateModel<MessageDocument>
>('Message', MessageSchema);

export default Message;