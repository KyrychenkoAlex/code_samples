<script>
import RegionsTableBody from "@/Components/Tables/RegionsTableBody.vue";

export default {
    components: {RegionsTableBody},
    mixins: [],
    props: {
        items: Array,
        onEdit: Function,
        onDelete: Function,
    },
    data() {
        return {
            itemsPerPage: 10,
        }
    },
    methods: {
        itemsToList(items) {
            return items.map(item => item);
        }
    }
}
</script>

<template>
    <v-data-table
        class="basic-table"
        v-model:items-per-page="itemsPerPage"
        :items="items"
    >
        <template v-slot:headers></template>
        <template v-slot:body="{items}">
            <RegionsTableBody
                :onEdit="onEdit"
                :onDelete="onDelete"
                :items="itemsToList(items)"
                :showHeaders="true"
                :showPagination="true"
                :isNestedBody="false"
            />
        </template>
    </v-data-table>
</template>

<style>
.companies-table > .v-table__wrapper {
    padding: 0 10px 10px 10px !important;
}
</style>
