import { plainToInstance} from "class-transformer";

import {MessageDTO} from "../DTO/MessageDTO";
import Message, {MessageInterface} from "../models/mongo/Message";

export const saveMessage = async (data: MessageInterface) => {
    const message = new Message(data);
    return await message.save();
};

export interface GetMessagesInterface {
    roomUUID: string,
    page: string
}
export const getRoomPaginatedMessages = async (data:GetMessagesInterface) => {
    const {roomUUID, page} = data;

    const result = await Message.paginate({
        roomUUID,
    },{
        page:parseInt(page),
        limit:30,
        sort:'-createdAt'
    });

    const docs = result.docs.map(dock =>
        plainToInstance(MessageDTO, dock, { excludeExtraneousValues: true })
    ).reverse();

    return {...result, messages:docs, totalMessages:result.totalDocs};

};