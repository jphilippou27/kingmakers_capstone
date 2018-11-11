var lib = lib || {};

lib.sankeyModule = function() {
    var data = [];
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    const politicolor = d3.scaleSequential(d3.interpolateRdBu);

    function industry_data_(_) {
        var that = this;
        if (!arguments.length) return data;
        data = _;
        return that;
    }

    function plot_by_industry_() {
        const nodes_with_names = data.nodes
        var svg = d3.select("#chart1")
            .style("width", "1000px")
            .style("height", "1000px")
            .style("border", "red");

        const sk = d3.sankey()
            .nodeWidth(15)
            .nodePadding(10)
            .size([width, height])
            .nodeWidth(20)
            .nodePadding(10)
            .nodeAlign(d3.sankeyCenter);
        let graph = sk(data)
        let links = svg.append("g")
            .selectAll("path")
            .data(graph.links)
            .enter()
            .append("path")
            .classed("link", true)
            .attr("fill", "none")
            .attr("d", d3.sankeyLinkHorizontal())
            .attr("stroke-width", d => d.width)
            .attr("stroke-opacity", 0.5)
            .append("title").text(d =>  "$" + d.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));

        var nodes = svg.append("g")
            .classed("nodes", true)
            .selectAll("rect")
            .data(graph.nodes)
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

        svg.append("g")
            .style("font", "10px sans-serif")
            .selectAll("text")
            .data(graph.nodes)
            .enter().append("text")
            .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
            .attr("y", d => (d.y1 + d.y0) / 2)
            .attr("dy", "0.35em")
            .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
            .text(d => d.id);
        console.log(graph.nodes)
    }

    return {
        "industry_data": industry_data_,
        "plot_by_industry": plot_by_industry_
    };
};

var generateChordMatrix = function(raw) {
    var s = new Set();
    var counter = 0;
    raw.forEach(function(row) {
        s.add(row.source);
        s.add(row.target);
    });
    index = Array.from(s);
    var map = new Map()
    for (var i=0; i<index.length; i++) {
         
    }
}

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

var width = 964;
var height = 600;
var sankeydata = d3.json("/sankeydata")
sankeydata.then(function(d){
    var clean_data = generateNL(d)
    var sankey = lib.sankeyModule();
    sankey.industry_data(clean_data)
    sankey.plot_by_industry()
});
