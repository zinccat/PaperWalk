import { ref } from 'vue';

export function useFilter() {
    const minCitationCount = ref(0);

    const applyFilter = (value) => {
        minCitationCount.value = value;
        // Any other filter application logic
    };

    return { minCitationCount, applyFilter };
}
