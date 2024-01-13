<template>
    <h1>Papers</h1>
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
            console.log(size/2);
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
        getTitles(node) {
           return node.properties.title === undefined ? "" : node.properties.title.split(" ")[0]
        },
        initializeNeoVis() {
            const config = {
                containerId: "neoVisGraph",
                neo4j: {
                    serverUrl: process.env.VUE_APP_NEO4J_URL,
                    serverUser: process.env.VUE_APP_NEO4J_USER,
                    serverPassword: process.env.VUE_APP_NEO4J_PASSWORD,
                },
                labels: {
                    "Paper": {
                        // first word in title
                        // "label": this.randomSize,
                        // "community": "paperId",
                        // "group": "paperId",
                        // "size": (node) => this.randomSize(node),
                        // "value": "citationCount",
                        [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                                function:{
                                    // value: (node) => this.randomSize(node),
                                    title: (node) => NeoVis.objectToTitleString(node, [
                                    "title",
                                    // "year",
                                    "citationCount",
                                    "paperId"
                                ]),
                                    color: this.getColor,
                                    label: this.getTitles,
                                    value: this.randomSize,
                                    // static: {
                                    //     value: 1.0
                                    // }
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
                initialCypher: 'MATCH (p1:Paper)-[r:CITES]->(p2:Paper) RETURN p1,r,p2 LIMIT 20',
                
            };

            const viz = new NeoVis(config);
            viz.render();
        }
    }
};
</script>

<style>
.neo-vis-container {
    height: 100%;
    width: 100%;
    position: absolute;
    top: 0;
    left: 0;
}
</style>
