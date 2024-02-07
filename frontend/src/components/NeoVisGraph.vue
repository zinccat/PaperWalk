<template>
    <h1 class="text-3xl text-center font-bold mb-4 mt-4">PaperWalk</h1>
    <FilterButtons @filter-applied="applyFilter" />
    <div class="flex">
        <!-- Graph Container -->
        <div class="flex-grow">
            <div id="neoVisGraph" class="neo-vis-container"></div>
        </div>
        <!-- SideBar for Paper Information -->
        <SideBar :paper="selectedPaper"></SideBar>
    </div>
</template>

<script>
import { useNodeStyles } from '../composables/useNodeStyles';
import { useFilter } from '../composables/useFilter';
import SideBar from './SideBar.vue';
import FilterButtons from './FilterButtons.vue';
import NeoVis from 'neovis.js/dist/neovis.js';

export default {
    name: 'NeoVisGraph',
    components: {
        SideBar,
        FilterButtons,
    },
    data() {
        return {
            selectedPaper: null, // Holds the selected paper's information
            selectedEdge: null, // Holds the selected edge's information
        };
    },
    setup() {
        // const { selectedPaper, selectedEdge, initializeGraph } = useGraph();
        const { randomSize, getColor, getOpacity, getTitles } = useNodeStyles();
        const { applyFilter } = useFilter();

        return {
            // selectedPaper,
            // selectedEdge,
            // initializeGraph,
            randomSize,
            getColor,
            getOpacity,
            getTitles,
            applyFilter,
        };
    },
    mounted() {
        this.initializeGraph();
    },
    methods: {
        initializeGraph(minCitationCount = 0) {
            let initialCypher;
            // if (minCitationCount === 0) { // No filter
            //     initialCypher = 'MATCH (p1:Paper)-[r:CITES]->(p2:Paper) RETURN p1,r,p2 LIMIT 20';
            // } else { // Specific range
            //     initialCypher = `MATCH (p1:Paper)-[r:CITES]->(p2:Paper) WHERE p1.citationCount >= ${minCitationCount} OR p2.citationCount >= ${minCitationCount} RETURN p1,r,p2 LIMIT 20`;
            // }
            initialCypher = `
                MATCH (p1:Paper) 
                WHERE p1.citationCount >= ${minCitationCount} 
                RETURN p1 AS paper1, NULL AS relationship, NULL AS paper2 
                LIMIT 20

                UNION

                // Query to return edges between papers where either paper meets the citation count condition
                MATCH (p1:Paper)-[r:CITES]->(p2:Paper) 
                WHERE p1.citationCount >= ${minCitationCount} AND p2.citationCount >= ${minCitationCount} 
                RETURN p1 AS paper1, r AS relationship, p2 AS paper2 
                LIMIT 20
                `;
            const config = {
                containerId: "neoVisGraph",
                neo4j: {
                    serverUrl: process.env.VUE_APP_NEO4J_URL,
                    serverUser: process.env.VUE_APP_NEO4J_USER,
                    serverPassword: process.env.VUE_APP_NEO4J_PASSWORD,
                },
                labels: {
                    "Paper": {
                        [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                            function: {
                                // value: (node) => this.randomSize(node),
                                title: (node) => NeoVis.objectToTitleString(node, [
                                    "title",
                                    "year",
                                    "citationCount",
                                    // "paperId",
                                    "firstAuthor",
                                    "pagerank",
                                    "articlerank",
                                    // "lastAuthor",
                                ]),

                                label: this.getTitles,
                                // value: this.randomSize,
                                opacity: this.getOpacity,
                                // color: this.getColor,
                            },
                            static: {
                                mass: 2.0
                            }
                        },
                    },
                },
                relationships: {
                    "CITES": {
                        // "thickness": "weight",
                        // "label": "weight",
                        // "thickness": "weight",
                        // "caption": true
                        [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                            function: {
                                // "label": (rel) => rel.type,
                                width: (rel) => {
                                    const nodeFrom = rel.start;
                                    const nodeTo = rel.end;
                                    const nodeFromCitationCount = viz.nodes.get(nodeFrom).raw.properties.citationCount;
                                    const nodeToCitationCount = viz.nodes.get(nodeTo).raw.properties.citationCount;
                                    return Math.max(1, nodeFromCitationCount * nodeToCitationCount * 0.02);
                                },
                            },
                            static: {
                                arrows: {
                                    to: {
                                        enabled: true,
                                    },
                                },
                                smooth: true,
                            }
                        },
                    },

                },
                initialCypher: initialCypher,

            };

            const viz = new NeoVis(config);
            viz.render();

            viz.registerOnEvent('clickNode', (e) => {
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
        }
    },
};
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
