var lib = lib || {};

lib.sankeyModule = function(type, zoom) {
    var contentDiv = document.getElementById("sankey-content")
    if (type == "tree") {
        var height = 700;
        //var height = contentDiv.clientHeight - 40;
    } else {
        var height = 1000;
    }
    var data = [];
    var canzoom = zoom;
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    const politicolor = d3.scaleSequential(d3.interpolateRdBu);
    var svg = d3.select("#sankey");

    var links = svg.select("#links");
    if (links.empty()) {
        links = svg.append("g").attr("id", "links");
    }

    var nodes = svg.select("#nodes");
    if (nodes.empty()) {
        nodes = svg.append("g").attr("id", "nodes");
    }

    var titlesg = svg.select("#titles");
    if (titlesg.empty()) {
        titlesg = svg.append("g").attr("id", "titles");
    }

    window.addEventListener("resize", plot_by_industry_)

    function industry_data_(_) {
        var that = this;
        if (!arguments.length) return data;
        data = _;
        return that;
    }

    function plot_by_industry_() {
        var width = contentDiv.clientWidth - 40;
        var width = contentDiv.clientWidth - 40;
        var nodes_with_names = data.nodes
        svg
            .attr("width", width)
            .attr("height", height + 30);

        var sk = d3.sankey()
            .nodeWidth(15)
            .nodePadding(10)
            .size([width, height])
            .nodeWidth(20)
            .nodePadding(10)
            .nodeAlign(d3.sankeyJustify);
        var graph = sk(data)

        var paths = links.selectAll("path")
            .data(graph.links)
            .attr("d", d3.sankeyLinkHorizontal())
            .attr("stroke-width", d => d.width)
            .on("click", function(d){
                if (canzoom) linkZoom1(d);
            });
        paths.select("title").remove();
        paths.append("title").text(d =>  "$" + d.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
        paths.enter()
            .append("path")
            .classed("link", true)
            .attr("fill", "none")
            .attr("d", d3.sankeyLinkHorizontal())
            .attr("stroke-width", d => d.width)
            .attr("stroke-opacity", 0.5)
            .on("click", function(d){
                if (canzoom) linkZoom1(d);
            });
        paths.append("title").text(d =>  "$" + d.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
        paths.exit().remove();

        var rects = nodes.classed("nodes", true)
            .selectAll("rect")
            .data(graph.nodes)
            .attr("x", d => d.x0)
            .attr("y", d => d.y0)
            .attr("width", d => d.x1 - d.x0)
            .attr("height", d => d.y1 - d.y0);
        rects.select("title").remove();
        rects.append("title").text(function(d) {
            return d.id + "\n" + "$" + d.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","); 
        })

        rects.enter()
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
            })
        rects.exit().remove();

        var titles = titlesg.style("font", "10px sans-serif")
            .selectAll("text")
            .data(graph.nodes)
            .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
            .attr("y", d => (d.y1 + d.y0) / 2)
            .attr("dy", "0.35em")
            .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
            .text(d => d.id);
        titles.enter()
            .append("text")
            .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
            .attr("y", d => (d.y1 + d.y0) / 2)
            .attr("dy", "0.35em")
            .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
            .text(d => d.id)
        titles.exit().remove();

    }

    return {
        "industry_data": industry_data_,
        "plot_by_industry": plot_by_industry_
    };
};


var generateNL = function(rawdata, include_parties) {
    //console.log(rawdata);
    if (include_parties) {
        for (i = 0; i < rawdata.length; i++) {
            rawdata[i].target =  rawdata[i].target + " (" + rawdata[i].party + ")"
        }
    }
    var n1 = new Set();
    for (i = 0; i < rawdata.length; i++) {
        n1.add(rawdata[i].source)
        n1.add(rawdata[i].target)
    }
    var l1 = {}
    var counter = 0
    var n2 = []
    if (include_parties) {
        n1.forEach(function(value) {
            if (value.includes("(DEM)")) {
                n2[counter] = {"id": value, "color": 0.9}
            } else if (value.includes("(REP)")) {
                n2[counter] = {"id": value, "color": 0.1}
            } else {
                n2[counter] = {"id": value}
            }
            l1[value] = counter;
            counter++;
        });
    } else {
        n1.forEach(function(value) {
            n2[counter] = {"id": value}
            l1[value] = counter;
            counter++;
        });
    }
    l2 = []
    var counter = 0
    rawdata.forEach(function(value) {
        l2[counter] = {"source": l1[value.source], "target": l1[value.target], "value": +value.value }
        counter++;
    });

    return {"nodes": n2, "links": l2 }
};

var linkZoom1 = function(d) {
    d3.select("#backbtn").style("display","block");
    var source = d.source.id;
    var target  = d.target.id;
    var sankeydata = d3.json("/industries/data?industry=" + encodeURIComponent(source) + "&party=" + encodeURIComponent(target) )
    sankeydata.then(function(d){
        var clean_data = generateNL(d, true)
        var sankey = lib.sankeyModule("full", false);
        sankey.industry_data(clean_data)
        sankey.plot_by_industry()
    });
};

var linkZoom2 = function(d) {
    var source = d.source.id;
    var target  = d.target.id;
    var sankeydata = d3.json("/industries/data?industry=" + encodeURIComponent(source))
    sankeydata.then(function(d){
        var clean_data = generateNL(d, true)
        var sankey = lib.sankeyModule("full");
        sankey.industry_data(clean_data)
        sankey.plot_by_industry()
    });
};

var goback = function() {
    d3.select("#backbtn").style("display","none");
    var sankeydata = d3.json("/industries/data")
    sankeydata.then(function(d){
        var clean_data = generateNL(d, false)
        var sankey = lib.sankeyModule("full", true);
        sankey.industry_data(clean_data)
        sankey.plot_by_industry()
    });

}


var sankeydata = d3.json(data_endpoint)
sankeydata.then(function(d){
    if (data_endpoint.startsWith("/candidates")) {
        var clean_data = generateNL(d, false)
        var sankey = lib.sankeyModule("tree", false);
    } else if (data_endpoint.startsWith("/industries")){
        var clean_data = generateNL(d, false)
        var sankey = lib.sankeyModule("full", true);
    } else{
        return
    }
    sankey.industry_data(clean_data)
    sankey.plot_by_industry()
});
