<template>
    <h1 class="text-3xl text-center font-bold mb-4">PaperWalk</h1>
    <div class="flex justify-center pt-4">
        <div class="mb-4">
            <button @click="applyFilter(10)" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2">
                More than 10 Citations
            </button>
            <button @click="applyFilter(100)" class="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded mr-2">
                More than 100 Citations
            </button>
            <button @click="applyFilter(1000)" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded mr-2">
                More than 1000 Citations
            </button>
            <button @click="applyFilter(0)" class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
                Clear Filter
            </button>
        </div>
    </div>
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
            } else { // Specific range
                initialCypher = `MATCH (p1:Paper)-[r:CITES]->(p2:Paper) WHERE p1.citationCount >= ${minCitationCount} RETURN p1,r,p2 LIMIT 50`;
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
    height: calc(100% - 180px); /* Adjust based on actual button container height */
    width: 100%;
    position: absolute;
    top: 180px; /* Adjust this value as needed */
    left: 0;
}
</style>
