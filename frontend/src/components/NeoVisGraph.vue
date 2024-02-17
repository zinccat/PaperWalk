<template>
    <h1 class="text-3xl text-center font-bold mb-4 mt-4">PaperWalk</h1>
    <div class="flex justify-center items-center">
        <input v-model="query" @keyup.enter="search(query)" class="border py-2 px-4 w-1/3 rounded mr-2" placeholder="Search..." />
        <button @click="search(query)" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2">Search</button>
        <button @click="clearGraph" class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded mr-2">Clear Graph</button>
    </div>
    <FilterButtons @filter-applied="applyFilter" />
    <div v-if="loading">Loading...</div>
    <div v-if="error">Error: {{ error.message }}</div>
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
import { onMounted, ref } from 'vue';
import { useFilter } from '../composables/useFilter';
import { useGraph, selectedPaper, selectedEdge } from '../composables/useGraph';
import { useSearchApi } from '../composables/useSearch'; // Adjust the path as necessary
import { clearGraph } from '../composables/utils';
// eslint-disable-next-line no-unused-vars
const { data, loading, error, search } = useSearchApi();
import SideBar from './SideBar.vue';
import FilterButtons from './FilterButtons.vue';

const query = ref('');

// Composition API functions
const { applyFilter } = useFilter();

// eslint-disable-next-line no-unused-vars
const { initializeGraph } = useGraph(selectedPaper, selectedEdge);

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
