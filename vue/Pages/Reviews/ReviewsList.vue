<script>
import DashboardLayout from "@/Layouts/DashboardLayout.vue";
import staticData from "@/mixins/staticData.js";
import SvgIcon from "@jamescoyle/vue-icon";
import IconWithTooltip from "@/Components/IconWithTooltip.vue";

export default {
    components: {IconWithTooltip, SvgIcon, DashboardLayout},
    mixins: [staticData],
    props: {
        eventVideoRequests: Array,
    },
    data() {
        return {
            itemsPerPage: 10,
            headers: [
                {
                    title: 'Srv',
                    key: 'srv.title'
                },
                {
                    title: 'Requested',
                    key: 'user.name'
                },
                {
                    title: 'Car',
                    key: 'event.marker.car'
                },
                {
                    title: 'Request type',
                    key: 'request_type'
                },
                {
                    title: 'Request reason',
                    key: 'request_reason'
                },
                {
                    title: 'Event time',
                    key: 'start_time'
                },
                {
                    title: 'Requested at',
                    key: 'requested_at'
                }
            ],
        }
    },
    methods: {
        acceptRequest(item) {
            this.$inertia.put(`/srv/${item.srv_id}/event-video-request`, {
                event_video_request_id: item.id,
                approve: true,
            })
        },
        declineRequest(item) {
            this.$inertia.put(`/srv/${item.srv_id}/event-video-request`, {
                event_video_request_id: item.id,
                decline: true,
            })
        }
    }
}
</script>

<template>
    <DashboardLayout>
        <template #pageName>Video Downloads</template>
        <template #default>
            <v-container>
                <div class="bg-white bordered rounded-2xl mt-10">
                    <v-row>
                        <v-col>
                            <h2 class="mx-4 text-2xl mb-3">Video Requests</h2>
                            <v-card-text variant="flat" class="border rounded-2xl overflow-hidden mx-4">
                                <v-data-table
                                    v-model:items-per-page="itemsPerPage"
                                    :headers="headers"
                                    :items="eventVideoRequests"
                                    :hide-default-footer="eventVideoRequests.length<10"
                                    class="px-3 pb-2"

                                >
                                    <template v-slot:item.start_time="{item}">
                                      {{ formatTime(item.event.start_time) }}
                                    </template>
                                    <template v-slot:item.requested_at="{item}">
                                        {{ formatTime(item.requested_at) }}
                                    </template>
                                    <template v-slot:item.buttons="{ item }">
                                        <div class="d-flex justify-start gap-x-4">
                                            <icon-with-tooltip
                                                @click="acceptRequest(item)"
                                                :image="getIcon('check')"
                                                tooltipType="videoRequestAccept"
                                            ></icon-with-tooltip>
                                            <icon-with-tooltip
                                                @click="declineRequest(item)"
                                                :image="getIcon('close')"
                                                tooltipType="videoRequestDecline"
                                            ></icon-with-tooltip>
                                        </div>
                                    </template>
                                </v-data-table>
                            </v-card-text>
                        </v-col>
                    </v-row>

                </div>
            </v-container>
        </template>
    </DashboardLayout>
</template>

<style>
</style>
