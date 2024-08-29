<script>


import SvgIcon from "@jamescoyle/vue-icon";
import staticData from "@/mixins/staticData.js";

export default {
    name: 'CustomBadge',
    mixins: [staticData],
    components: {SvgIcon},
    props: {
        value: Number,
        iconType: String
    },
    data() {
        return {
        }
    },
    methods: {

    }
}
</script>

<template>
    <v-badge
        :content="value"
        v-if="value > 1"
    >
        <svg-icon
            type="mdi"
            :path="getIcon(iconType)"
            class="text-grey my-auto ml-3"
            size="25"
        ></svg-icon>
    </v-badge>
    <svg-icon
        v-else
        type="mdi"
        :path="getIcon(iconType)"
        class="text-grey my-auto ml-3"
        size="25"
    ></svg-icon>
</template>
