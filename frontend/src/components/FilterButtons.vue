<template>
    <div class="flex justify-center pt-4">
        <button v-for="filter in filters" :key="filter.count" @click="applyFilter(filter.count)" :class="filter.classes">
            {{ filter.text }}
        </button>
    </div>
</template>

<script>
export default {
    name: 'FilterButtons',
    data() {
        return {
            filters: [
                { count: 10, text: 'More than 10 Citations', classes: 'bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2' },
                { count: 100, text: 'More than 100 Citations', classes: 'bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded mr-2' },
                { count: 1000, text: 'More than 1000 Citations', classes: 'bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded mr-2' },
                { count: 0, text: 'Clear Filter', classes: 'bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded' },
            ],
        };
    },
    methods: {
        applyFilter(minCitationCount) {
            this.$emit('filter-applied', minCitationCount);
        },
    },
};
</script>
