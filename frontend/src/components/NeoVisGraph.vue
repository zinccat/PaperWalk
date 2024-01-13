<template>
    <div id="neoVisGraph" class="neo-vis-container"></div>
</template>


<script>
import NeoVis from 'neovis.js';

export default {
    name: 'NeoVisGraph',
    mounted() {
        this.initializeNeoVis();
    },
    methods: {
        randomSize(node) {
            let size = 1;
            if (node.properties.citationCount === undefined) {
                size = 1;
            }
            else
                size = node.properties.citationCount + 1;
            console.log(size / 2);
            return node.properties.citationCount ** 2 / 2;
        },
        getColor(node) {
            if (node.properties.citationCount < 10) {
                return "blue";
            }
            else if (node.properties.citationCount >= 10 && node.properties.citationCount < 100) {
                return "orange";
            }
            else {
                return "red";
            }
        },
        getOpacity(node) {
            // use log scale to make the opacity more even
            return Math.log(node.properties.citationCount + 2) / 5;
        },
        getTitles(node) {
            //    return node.properties.title === undefined ? "" : node.properties.title.split(" ")[0]
            let title = node.properties.firstAuthor === undefined ? "" : node.properties.firstAuthor.split(" ").slice(-1)[0]
            title += ", "
            title += node.properties.year === undefined ? "" : " " + node.properties.year

            return title
        },
        applyFilter(minCitationCount) {
            this.initializeNeoVis(minCitationCount);
        },
        initializeNeoVis(minCitationCount=0) {
            let initialCypher;
            if (minCitationCount === 0) { // No filter
                initialCypher = 'MATCH (p1:Paper)-[r:CITES]->(p2:Paper) RETURN p1,r,p2 LIMIT 50';
            } else if (minCitationCount === -1) { // 100+ Citations
                initialCypher = 'MATCH (p1:Paper)-[r:CITES]->(p2:Paper) WHERE p1.citationCount >= 100 RETURN p1,r,p2 LIMIT 50';
            } else { // Specific range
                initialCypher = `MATCH (p1:Paper)-[r:CITES]->(p2:Paper) WHERE p1.citationCount >= ${minCitationCount} AND p1.citationCount < ${minCitationCount * 10} RETURN p1,r,p2 LIMIT 50`;
            }
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
                                    "paperId",
                                    "firstAuthor",
                                    "lastAuthor",
                                ]),
                                
                                label: this.getTitles,
                                // value: this.randomSize,
                                opacity: this.getOpacity,
                                // color: this.getColor,
                            },
                            static: {
                                    mass: 5.0
                                }
                        },
                    },
                },
                relationships: {
                    "CITES": {
                        "thickness": "weight",
                        "label": "weight",
                        // "thickness": "weight",
                        // "caption": true
                        [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                            // function: {
                            //     "label": (rel) => rel.type,
                            // }
                        }
                    }
                },
                initialCypher: initialCypher,

            };

            const viz = new NeoVis(config);
            viz.render();
        }
    }
};
</script>

<style>
.neo-vis-container {
    height: calc(100% - 100px); /* Adjust height as per your layout */
    width: 100%;
    position: absolute;
    top: 100px; /* Adjust top as per your button's height */
    left: 0;
}
</style>
