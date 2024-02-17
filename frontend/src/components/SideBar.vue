<template>
  <div v-if="paper" class="sidebar">
    <h2 class="text-xl font-bold mb-2">Paper Information</h2>
    <p><strong>Title:</strong> {{ paper.title }}</p>
    <button @click="expandGraph(paper.paperId)" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-2">Expand Graph</button>
    <p v-if="paper.ArXiv"><strong>ArXiv Link:</strong> <a :href="'https://arxiv.org/abs/' + paper.ArXiv" target="_blank"
        class="text-blue-500 hover:text-blue-800"> {{ paper.ArXiv }} </a></p>
    <p><strong>First Author:</strong> {{ paper.firstAuthor }}</p>
    <p><strong>Last Author:</strong> {{ paper.lastAuthor }}</p>
    <p v-if="paper.year"><strong>Year:</strong> {{ paper.year }}</p>
    <p v-if="paper.citationCount"><strong>Citation Count:</strong> {{ paper.citationCount }}</p>
    <p v-if="paper.abstract"><strong>Abstract:</strong> {{ paper.abstract }}</p>
  </div>
</template>
  
<script>

import { expandGraph } from '../composables/utils.js';

export default {
  name: 'SideBar',
  props: {
    paper: {
      type: Object,
      default: () => null
    }
  },
  methods: {
    expandGraph
  }
};
</script>
  
<style>
.sidebar {
  width: 25%;
  padding: 20px;
  background-color: #f3f3f3;
  /* Additional styling as needed */
}
</style>
  