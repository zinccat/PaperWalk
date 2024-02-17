export function useNodeStyles() {
    const randomSize = (node) => {
        let size = 1;
    if (node.properties.citationCount === undefined) {
        size = 1;
    }
    else
        size = node.properties.citationCount + 1;
    console.log(size);
    return node.properties.citationCount ** 2 / 2;
    };

    const getColor = (node) => {
        if (node.properties.citationCount < 10) {
            return "blue";
        }
        else if (node.properties.citationCount >= 10 && node.properties.citationCount < 100) {
            return "orange";
        }
        else {
            return "red";
        }
    };

    const getOpacity = (node) => {
        // use log scale to make the opacity more even
        return Math.log(node.properties.citationCount + 2) / 13;
    };

    const getTitles = (node) => {
        //    return node.properties.title === undefined ? "" : node.properties.title.split(" ")[0]
    let title = node.properties.firstAuthor === undefined ? "" : node.properties.firstAuthor.split(" ").slice(-1)[0]
    if (node.properties.year === undefined) {
        return title
    }
    title += " (" + node.properties.year + ")"

    return title
    };

    return { randomSize, getColor, getOpacity, getTitles };
}