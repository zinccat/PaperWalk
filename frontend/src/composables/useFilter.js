import { ref } from 'vue';
import { useGraph } from '../composables/useGraph';

// eslint-disable-next-line no-unused-vars
const { selectedPaper, selectedEdge, initializeGraph } = useGraph();

export function useFilter() {
    const minCitationCount = ref(0);

    const applyFilter = (value) => {
        minCitationCount.value = value;
        initializeGraph(value);
    };

    return { minCitationCount, applyFilter };
}
