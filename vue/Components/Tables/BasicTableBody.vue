<script>

import SvgIcon from "@jamescoyle/vue-icon";
import permission from "@/mixins/permission.js";
import staticData from "@/mixins/staticData.js";
import {computed} from "vue";
import {router, usePage} from "@inertiajs/vue3";
import IconWithTooltip from "@/Components/IconWithTooltip.vue";


export default {
    mixins: [staticData, permission, staticData],
    props: {
        items: Array,
        showHeaders: Boolean,
        showPagination: Boolean,
        shift: Number,
        onEdit: Function,
        onDelete: Function,
        isNestedBody: Boolean
    },
    components: {
        IconWithTooltip,
        SvgIcon
    },

    name: "RegionsTableBody",
    data() {
        return {
            showRegionColumn: computed(() => (
                usePage().props.current_Region.has_subcompanies && usePage().props.current_Region.show_data_from_children
            ))
        }
    },
    methods: {
        viewRegionDashboard(id) {
            window.open(`/regions/${id}/dashboard`, "_blank")
        },
    }
};
</script>

<template>
    <div v-if="showHeaders" class="flex w-full px-4 py-2 border-b text-grey">
        <div class="flex-grow-1 align-self-center text-start">Title</div>
        <div :class="showRegionColumn ? 'w-1/3' : 'w-1/2'" class="align-self-center text-start">Address</div>
        <div v-if="showRegionColumn" class="w-1/4 px-2 align-self-center text-start">Region</div>
        <div class="w-1/12 align-self-center text-start">Enabled</div>
        <div class="w-1/12 align-self-center text-start">Actions</div>
    </div>

    <div
        v-for="item in items"
        :key="item.id"
    >
        <div
            class="flex w-full px-4 py-2 border-b"
        >
            <div :style="`width:${shift*25}px;`"></div>
            <div class="flex-grow-1 align-self-center" :class="shift ? 'dash' : ''">{{ item.title }}</div>
            <div :class="showRegionColumn ? 'w-1/3' : 'w-1/2'" class="align-self-center">{{ item.address }}</div>
            <div v-if="showRegionColumn" class="w-1/4 px-2 align-self-center">{{ item.Region?.title }}</div>
            <div class="w-1/12 px-2 align-self-center">
                <v-checkbox-btn
                    v-model="item.enabled"
                    :disabled="true"
                ></v-checkbox-btn>
            </div>

            <div class="w-1/12 align-self-center">
                <div class="d-flex justify-start gap-x-3">
                    <icon-with-tooltip
                        @click="viewRegionDashboard(item.id)"
                        :image="getIcon('regionDashboard')"
                        tooltipType="regionDashBoard"
                    ></icon-with-tooltip>
                    <icon-with-tooltip
                        v-if="canEdit('region')"
                        @click="onEdit(item)"
                        :image="getIcon('edit')"
                        tooltipType="regionEdit"
                    ></icon-with-tooltip>
                    <icon-with-tooltip
                        v-if="items.length > 1 && canDelete('region') || isNestedBody"
                        @click="onDelete(item)"
                        :image="getIcon('delete')"
                        tooltipType="regionRemove"
                    ></icon-with-tooltip>
                </div>
            </div>

        </div>
        <RegionsTableBody
            :shift="shift ? shift + 1 : 1"
            v-if="item.regions.length"
            :items="item.regions"
            :onEdit="onEdit"
            :onDelete="onDelete"
            :isNestedBody="true"
        />
    </div>
</template>

<style scoped>
.dash::before {
    content: "- ";
}
</style>
