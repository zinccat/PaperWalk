import { ref } from 'vue';
import { useGraph, selectedPaper, selectedEdge } from './useGraph';

// eslint-disable-next-line no-unused-vars
const { initializeGraph } = useGraph(selectedPaper, selectedEdge);

export function useFilter() {
    const minCitationCount = ref(0);

    const applyFilter = (value) => {
        minCitationCount.value = value;
        initializeGraph(value);
    };

    return { minCitationCount, applyFilter };
}
