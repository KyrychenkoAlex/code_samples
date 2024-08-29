import {Expose} from "class-transformer";

import {MessageDTO} from "@/src/DTO/MessageDTO";


export class PaginatedMessagesListDTO {
    @Expose()
        messages!: MessageDTO[];

    @Expose()
        totalMessages!: number;

    @Expose()
        limit!: number;

    @Expose()
        totalPages!: number;

    @Expose()
        page!: number;

}