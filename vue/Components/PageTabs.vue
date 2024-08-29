<script>
import staticData from "@/mixins/staticData.js";
import {computed} from "vue";
import {usePage} from "@inertiajs/vue3";

export default {
  components: {},
  mixins: [staticData],
  props: {
    settings: Array,
    tabs: Array,
    routeName: String
  },
  beforeMount() {
      const activeTab = this.tabs.find(tab =>
          tab.route.slice(0, tab.route.indexOf('.')) === this.routeName.slice(0, this.routeName.indexOf('.'))
      );

      if (activeTab?.route) {
          this.activeTabRoute = activeTab.route;
      }

      this.pageTabs = this.getTabs();
  },
  watch: {
    "settings"() {
      this.pageTabs = this.getTabs();
    }
  },
  data() {
    return {
        activeTabRoute: '',
        pageTabs: [],
        is_admin: computed(() => usePage().props.is_admin),
    }
  },
  methods: {
    getTabs() {
      const isApiEnabled = this.settings.find(item => item.setting_key === 'enable_api')?.setting_value || this.is_admin
      const isPusherEnabled = this.settings.find(item => item.setting_key === 'is_socket_on')?.setting_value || this.is_admin
        let tabs = this.tabs
        if(!isApiEnabled) {
            tabs = tabs.filter(tab => tab.route !== 'region-api.index')
        }
        if(!isPusherEnabled) {
            tabs = tabs.filter(tab => tab.route !== 'pusher-configuration.index')
        }

      return tabs
    },
    onTabChange() {
      this.$inertia.get(route(this.activeTabRoute));
    }
  }
}
</script>

<template>
  <v-container v-if="pageTabs.length">
    <v-tabs
        v-if="activeTabRoute"
        class="tabs"
        centered
        grow
        height="60px"
        v-model="activeTabRoute"
        @update:modelValue="onTabChange"
    >
      <v-tab
          v-for="tab in pageTabs"
          :value="tab.route"
          :key="tab.route"
      >{{ tab.name }}</v-tab>
    </v-tabs>
  </v-container>
  <slot />

</template>

<style lang="scss">
</style>
