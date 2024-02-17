import { ref } from 'vue';
import axios from 'axios';
import { useGraph, selectedPaper, selectedEdge } from './useGraph';

// eslint-disable-next-line no-unused-vars
const { initializeGraph } = useGraph(selectedPaper, selectedEdge);

export function useSearchApi() {
    const data = ref(null);
    const loading = ref(false);
    const error = ref(null);

    const search = async (query) => {
        loading.value = true;
        error.value = null;
        try {
            const response = await axios.get('http://localhost:5007/search', { params: { query } });
            data.value = response.data;
            initializeGraph();
        } catch (err) {
            error.value = err;
            console.error(err);
        } finally {
            loading.value = false;
        }
    };

    return { data, loading, error, search };
}
