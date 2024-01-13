<template>
  <div id="app">
    <NeoVisGraph />
  </div>
</template>

<script>
import NeoVisGraph from './components/NeoVisGraph.vue';

export default {
  name: 'App',
  components: {
    NeoVisGraph
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
