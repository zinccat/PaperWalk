<template>
    <h1 class="text-3xl text-center font-bold mb-4 mt-4">PaperWalk</h1>
    <FilterButtons @filter-applied="applyFilter" />
    <div class="flex">
        <!-- Graph Container -->
        <div class="flex-grow">
            <div id="neoVisGraph" class="neo-vis-container"></div>
        </div>
        <!-- SideBar for Paper Information -->
        <SideBar :paper="selectedPaper"></SideBar>
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useFilter } from '../composables/useFilter';
import { useGraph } from '../composables/useGraph';
import SideBar from './SideBar.vue';
import FilterButtons from './FilterButtons.vue';


// Composition API functions
const { applyFilter } = useFilter();

// eslint-disable-next-line no-unused-vars
const { initializeGraph, selectedPaper, selectedEdge } = useGraph();

// Lifecycle hook
onMounted(() => {
    initializeGraph();
});
</script>

<style>
.neo-vis-container {
    height: calc(100% - 180px);
    /* Adjust based on actual button container height */
    width: 75%;
    position: absolute;
    top: 180px;
    /* Adjust this value as needed */
    left: 0;
}
</style>
