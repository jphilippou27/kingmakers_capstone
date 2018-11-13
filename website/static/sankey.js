var lib = lib || {};

lib.sankeyModule = function() {
    var contentDiv = document.getElementById("content")
    var height = 1600;
    //var width = contentDiv.clientWidth;
    var data = [];
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    const politicolor = d3.scaleSequential(d3.interpolateRdBu);
    var svg = d3.select("#chart1");
    let links = svg.append("g");
    var nodes = svg.append("g");
    var titles  = svg.append("g")
    window.addEventListener("resize", plot_by_industry_)

    function industry_data_(_) {
        var that = this;
        if (!arguments.length) return data;
        data = _;
        return that;
    }

    function plot_by_industry_() {
        var width = contentDiv.clientWidth - 40;
        const nodes_with_names = data.nodes
        svg
            .attr("width", width)
            .attr("height", height);
        console.log(svg);

        const sk = d3.sankey()
            .nodeWidth(15)
            .nodePadding(10)
            .size([width, height])
            .nodeWidth(20)
            .nodePadding(10)
            .nodeAlign(d3.sankeyCenter);
        let graph = sk(data)

        links
            .selectAll("path")
            .data(graph.links)
            .attr("d", d3.sankeyLinkHorizontal())
            .attr("stroke-width", d => d.width)
            .enter()
            .append("path")
            .classed("link", true)
            .attr("fill", "none")
            .attr("d", d3.sankeyLinkHorizontal())
            .attr("stroke-width", d => d.width)
            .attr("stroke-opacity", 0.5)
            .append("title").text(d =>  "$" + d.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
        nodes
            .classed("nodes", true)
            .selectAll("rect")
            .data(graph.nodes)
            .attr("x", d => d.x0)
            .attr("y", d => d.y0)
            .attr("width", d => d.x1 - d.x0)
            .attr("height", d => d.y1 - d.y0)
            .enter()
            .append("rect")
            .classed("nodes", true)
            .attr("x", d => d.x0)
            .attr("y", d => d.y0)
            .attr("width", d => d.x1 - d.x0)
            .attr("height", d => d.y1 - d.y0)
            .attr("opacity", 0.8)
            .attr("fill", function(d) {
                if ("color" in d) {
                    return politicolor(d.color); 
                } else {
                    return color(d.id)
                }
            }).append("title").text(function(d) {
                return d.id + "\n" + "$" + d.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","); 
            });
        titles
            .style("font", "10px sans-serif")
            .selectAll("text")
            .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
            .attr("y", d => (d.y1 + d.y0) / 2)
            .attr("dy", "0.35em")
            .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
            .data(graph.nodes)
            .enter().append("text")
            .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
            .attr("y", d => (d.y1 + d.y0) / 2)
            .attr("dy", "0.35em")
            .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
            .text(d => d.id);
    }

    return {
        "industry_data": industry_data_,
        "plot_by_industry": plot_by_industry_
    };
};


var generateNL = function(rawdata) {
    var n1 = new Set();
    for (i = 0; i < rawdata.length; i++) {
        n1.add(rawdata[i].source)
        n1.add(rawdata[i].target)
    }
    var l1 = {}
    var counter = 0
    var n2 = []
    n1.forEach(function(value) {
        if (value.includes("(D)")) {
            n2[counter] = {"id": value, "color": 0.9}
        } else if (value.includes("(R)")) {
            n2[counter] = {"id": value, "color": 0.1}
        } else {
            n2[counter] = {"id": value}
        }
        l1[value] = counter;
        counter++;
    });
    l2 = []
    var counter = 0
    rawdata.forEach(function(value) {
        l2[counter] = {"source": l1[value.source], "target": l1[value.target], "value": +value.value }
        counter++;
    });

    //console.log(n2)
    //console.log(l2)
    return {"nodes": n2, "links": l2 }
}

var sankeydata = d3.json("/sankeydata")
sankeydata.then(function(d){
    var clean_data = generateNL(d)
    var sankey = lib.sankeyModule();
    sankey.industry_data(clean_data)
    sankey.plot_by_industry()
});