import { ref } from 'vue';
import NeoVis from 'neovis.js/dist/neovis.js';
import { useNodeStyles } from './useNodeStyles';

// eslint-disable-next-line no-unused-vars
const { randomSize, getColor, getOpacity, getTitles } = useNodeStyles();

export const selectedPaper = ref(null);
export const selectedEdge = ref(null);

export function useGraph(selectedPaper, selectedEdge) {
    
    function initializeGraph(minCitationCount = 0) {
        let initialCypher;
        // if (minCitationCount === 0) { // No filter
        //     initialCypher = 'MATCH (p1:Paper)-[r:CITES]->(p2:Paper) RETURN p1,r,p2 LIMIT 100';
        // } else { // Specific range
        //     initialCypher = `MATCH (p1:Paper)-[r:CITES]->(p2:Paper) WHERE p1.citationCount >= ${minCitationCount} OR p2.citationCount >= ${minCitationCount} RETURN p1,r,p2 LIMIT 100`;
        // }
        initialCypher = `
                    MATCH (p1:Paper) 
                    WHERE p1.citationCount >= ${minCitationCount} 
                    RETURN p1 AS paper1, NULL AS relationship, NULL AS paper2 
                    LIMIT 100
    
                    UNION
    
                    // Query to return edges between papers where either paper meets the citation count condition
                    MATCH (p1:Paper)-[r:CITES]->(p2:Paper) 
                    WHERE p1.citationCount >= ${minCitationCount} AND p2.citationCount >= ${minCitationCount} 
                    RETURN p1 AS paper1, r AS relationship, p2 AS paper2 
                    LIMIT 100
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
    
                            label: getTitles,
                            // value: this.randomSize,
                            opacity: getOpacity,
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
                                try {
                                    const nodeFrom = rel.start;
                                    const nodeTo = rel.end;
                                    const nodeFromCitationCount = viz.nodes.get(nodeFrom).raw.properties.citationCount;
                                    const nodeToCitationCount = viz.nodes.get(nodeTo).raw.properties.citationCount;
                                    return Math.max(1, nodeFromCitationCount * nodeToCitationCount * 0.02);
                                } catch (e) {
                                    console.error(e);
                                    return 1;
                                }
                            }
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
            try {
                selectedPaper.value = e.node.raw.properties;
                console.log(selectedPaper.value);
            }
            catch (e) {
                console.error(e);
            }
        });
        // Assuming network is your Vis.js network instance
        viz.registerOnEvent("clickEdge", (e) => {
            selectedEdge.value = e.edge;
            // console.log(this.selectedEdge);
            // console.log(viz.nodes.get(e.edge.from));
        });
    }

    return { initializeGraph };
}
