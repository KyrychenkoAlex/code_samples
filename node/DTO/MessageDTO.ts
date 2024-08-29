import {Expose} from "class-transformer";

export class MessageDTO {
    @Expose()
        roomUUID!:string;

    @Expose()
        messageUUID!: string;

    @Expose()
        senderId!: string;

    @Expose()
        message!: string;

    @Expose()
        createdAt!: string;

    @Expose()
        updatedAt!: string;
}