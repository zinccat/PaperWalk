<template>
    <div v-if="paper" class="sidebar">
      <h2 class="text-xl font-bold mb-2">Paper Information</h2>
      <p><strong>Title:</strong> {{ paper.title }}</p>
      <a :href="'https://arxiv.org/abs/' + paper.ArXiv" target="_blank" class="text-blue-500 hover:text-blue-800"> ArXiv Link </a>
      <p><strong>First Author:</strong> {{ paper.firstAuthor }}</p>
      <p><strong>Last Author:</strong> {{ paper.lastAuthor }}</p>
      <p><strong>Year:</strong> {{ paper.year }}</p>
      <p><strong>Abstract:</strong> {{ paper.abstract }}</p>
    </div>
  </template>
  
  <script>
  export default {
    name: 'SideBar',
    props: {
      paper: {
        type: Object,
        default: () => null
      }
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
  