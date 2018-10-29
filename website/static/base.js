function run(data) {
    var svg = d3.select("#chart1")
        .style("width", "1000px")
        .style("height", "1000px")
        .style("border", "red");

    //const {nodes, links} = sankey(data);
    const sk = d3.sankey()
        .nodeWidth(15)
        .nodePadding(10)
        .size([width, height])
        .nodeWidth(20)
        .nodePadding(10)
        .nodeAlign(d3.sankeyCenter);
    let graph = sk(data)
    console.log(graph)
    //console.log(sk.links);
    //console.log(sk.nodes);
    //console.log(sk.links());
    //console.log(sk.nodes());
    //console.log(data.links);
    //console.log(data.nodes);
    //svg.append("g")
    //    .attr("stroke", "#000")
    //    .selectAll("rect")
    //    .data(sk.nodes)
    //    .enter()
    //    .append("rect")
    //      .attr("x", d => d.x0)
    //      .attr("y", d => d.y0)
    //      .attr("height", d => d.y1 - d.y0)
    //      .attr("width", d => d.x1 - d.x0)
    //      .attr("fill", d => color(d.name))
    //    .append("title")
    //    .text(d => '${d.name}\n${format(d.value)}');
    //
    let links = svg.append("g")
        .selectAll("path")
        .data(graph.links)
        .enter()
        .append("path")
        .classed("link", true)
        .attr("fill", "none")
        .attr("d", d3.sankeyLinkHorizontal())
        .attr("stroke-width", d => d.width)
        .attr("stroke-opacity", 0.5);

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
        .append("title").text(d => data.nodes[d.index]);

    console.log(graph.nodes)
    console.log(data.nodes)
    
    //nodes.append("text")
     //   .text(d => d.id);
    //    .data(sk.links)
    //    link.enter().append("g")
    //      .style("mix-blend-mode", "multiply");
    //
    //  if (edgeColor === "path") {
    //    const gradient = link.append("linearGradient")
    //        .attr("id", d => (d.uid = DOM.uid("link")).id)
    //        .attr("gradientUnits", "userSpaceOnUse")
    //        .attr("x1", d => d.source.x1)
    //        .attr("x2", d => d.target.x0);
    //
    //    gradient.append("stop")
    //        .attr("offset", "0%")
    //        .attr("stop-color", d => color(d.source.name));
    //
    //    gradient.append("stop")
    //        .attr("offset", "100%")
    //        .attr("stop-color", d => color(d.target.name));
    //  }
    
    //link.append("path")
    //      .attr("d", d3.sankeyLinkHorizontal())
    //      .attr("stroke", d => edgeColor === "path" ? d.uid 
    //          : edgeColor === "input" ? color(d.source.name) 
    //          : color(d.target.name))
    //      .attr("stroke-width", d => Math.max(1, d.width));
    //
    //  link.append("title")
    //      .text(d => `${d.source.name} → ${d.target.name}\n${format(d.value)}`);
    //
    //  svg.append("g")
    //      .style("font", "10px sans-serif")
    //    .selectAll("text")
    //    .data(sk.nodes)
    //    .enter().append("text")
    //      .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
    //      .attr("y", d => (d.y1 + d.y0) / 2)
    //      .attr("dy", "0.35em")
    //      .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
    //      .text(d => d.name);
    
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
        n2[counter] = {"id": +value}
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

var sankey = function(data) {
    var sk = d3.sankey()
        .nodeWidth(15)
        .nodePadding(10)
        .extent([[1, 1], [width - 1, height - 5]]);
    console.log(sk.links())
    return ({nodes, links}) => sk({
        nodes: nodes.map(d => Object.assign({}, d)),
        links: links.map(d => Object.assign({}, d))
    });
}

var format = function(d) {
    const f = d3.format(",.0f");
    return d => '${f(d)} TWh';
}

var color = function(name) {
  const color = d3.scaleOrdinal(d3.schemeCategory10);
  return name => color(name.replace(/ .*/, ""));
}

//var data = d3.json("https://gist.githubusercontent.com/mbostock/ca9a0bb7ba204d12974bca90acc507c0/raw/398136b7db83d7d7fd89181b080924eb76041692/energy.json")
var data = d3.json("/sankey")
var width = 964;
var height = 600;

data.then(function(d){

    var clean_data = generateNL(d)
    run(clean_data);
});
