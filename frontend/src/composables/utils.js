import axios from 'axios'
// import from components
import { useGraph, selectedPaper, selectedEdge } from '../composables/useGraph'
import NeoVis from "neovis.js";

export const { initializeGraph } = useGraph(selectedPaper, selectedEdge);

export async function expandGraph(paperId) {
    // console.log(paperId);
  // call the backend to expand the graph
  axios.get(`http://localhost:5007/papers/expand/${paperId}`)
    // eslint-disable-next-line no-unused-vars
    .then(response => {
      // const data = response.data
    //   console.log(data)
      initializeGraph();
    })
    .catch(error => {
      console.log(error)
    })

}

export const renderGraph = (config) => {
  const viz = new NeoVis(config);
  viz.render();

  viz.registerOnEvent("clickNode", (e) => {
    // e: { nodeId: number; node: Node }
    this.selectedPaper = e.node.raw.properties;
    console.log(this.selectedPaper);
  });
  // Assuming network is your Vis.js network instance
  viz.registerOnEvent("clickEdge", (e) => {
    this.selectedEdge = e.edge;
    // console.log(this.selectedEdge);
    // console.log(viz.nodes.get(e.edge.from));
  });
  return viz;
};
