var lib = lib || {};

lib.sankeyModule = function(type, zoom, svgid, parentid, superpaczoom) {
    console.log(parentid); var contentDiv = document.getElementById(parentid)
    if (type == "tree") {
        var height = 700;
        //var height = contentDiv.clientHeight - 40;
    } else {
        var height = 1500;
    }
    var data = []; var canzoom = zoom; const color = d3.scaleOrdinal(d3.schemeCategory10);
    const politicolor = d3.scaleSequential(d3.interpolateRdBu);
    var svg = d3.select(svgid);

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
        var nodes_with_names = data.nodes
        svg
            .attr("width", width)
            .attr("height", height + 30);
        var sk = d3.sankey()
            .nodeWidth(15)
            .nodePadding(10)
            .size([width, height])
            .nodeWidth(20)
            .nodePadding(10);
        if (superpaczoom) {
            sk.nodeAlign(d3.sankeyJustify)
        } else {
            sk.nodeAlign(d3.sankeyJustify)
        }
           
        var graph = sk(data)

        var paths = links.selectAll("path")
            .data(graph.links)
            //.transition().duration(1300)
            .attr("d", d3.sankeyLinkHorizontal())
            .attr("stroke-width", d => d.width)
            .attr("fill", "green")
            .on("click", function(d){
                if (canzoom) linkZoom1(d);
            });
        paths.selectAll("title").remove();
        paths.append("title").text(d =>  "$" + d.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
        paths.enter()
            .append("path")
            .classed("link", true)
            .attr("d", d3.sankeyLinkHorizontal())
            .attr("stroke-width", d => d.width)
            //.style("stroke", "blue")
            .style("stroke", function(d) {
                if (d.target.hasOwnProperty("type")) {
                    if (d.target.type == "For") return "gray";
                    if (d.target.type == "Against") return "red";
                }
            })
            .attr("stroke-opacity", 0.5)
            .on("click", function(d){
                if (canzoom) linkZoom1(d);
                if (superpaczoom) linkZoom3(d);
            })
            .append("title").text(d =>  "$" + d.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
        //paths.selectAll("title").remove();
        paths.exit().remove();

        var rects = nodes.classed("nodes", true)
            .selectAll("rect")
            .data(graph.nodes)
            //.transition().duration(1300)
            .attr("x", d => d.x0)
            .attr("y", d => d.y0)
            .attr("width", d => d.x1 - d.x0)
            .attr("height", d => d.y1 - d.y0)
            .attr("fill", function(d) {
                if ("color" in d) {
                    return politicolor(d.color);
                } else {
                    return color(d.id)
                }
            }).on("click", function(d) {
                if ("cand_id" in d) {
                    window.location.href = "/candidates/" + d.cand_id;
                } else if ("industry" in d) {
                    //window.location.href = "/candidates/" + d.cand_id;
                    console.log("skip to " + d.industry);
                    linkZoom2(d.industry);
                }


            });
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
            }).on("click", function(d) {
                if ("cand_id" in d) {
                    window.location.href = "/candidates/" + d.cand_id;
                } else if ("industry" in d) {
                    console.log("skip to " + d.industry);
                    linkZoom2(d.industry);
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


var generateNL = function(rawdata, party_id, left_party_color, right_party_color, industry_link) {
    if (party_id) {
        for (i = 0; i < rawdata.length; i++) {
            rawdata[i].target =  rawdata[i].target + " (" + rawdata[i].party + ")"
        }
    }
    //var n1 = new Set();
    var n1 = {};
    if (left_party_color && right_party_color) {
        //console.log("left and right")
        for (i = 0; i < rawdata.length; i++) {
            if ("party" in rawdata[i]) {
                n1[rawdata[i].source] = {"party": rawdata[i].party};
                n1[rawdata[i].target] = {"party": rawdata[i].party};
            } else {
                n1[rawdata[i].source] = {};
                n1[rawdata[i].target] = {};
            }
            if ("proportion" in rawdata[i]) {
                n1[rawdata[i].source] = {"proportion": rawdata[i].proportion};
            } else {
                n1[rawdata[i].source] = {};
            }
            if ("cand_id" in rawdata[i]) {
                n1[rawdata[i].target].cand_id = rawdata[i].cand_id;
            }
            if ("type" in rawdata[i]) {
                n1[rawdata[i].target].type = rawdata[i].type;
            }
            if (industry_link) {
                n1[rawdata[i].source].industry = rawdata[i].source;
            }
        }
    } else if (right_party_color) {
        //console.log("right only")
        for (i = 0; i < rawdata.length; i++) {
            if ("party" in rawdata[i]) {
                //n1[rawdata[i].source] = {"proportion": rawdata[i].proportion};
                n1[rawdata[i].target] = {"party": rawdata[i].party};
            } else {
                n1[rawdata[i].target] = {};
            }
            if ("proportion" in rawdata[i]) {
                n1[rawdata[i].source] = {"proportion": rawdata[i].proportion};
            } else {
                n1[rawdata[i].source] = {};
            }
            if ("cand_id" in rawdata[i]) {
                n1[rawdata[i].target].cand_id = rawdata[i].cand_id;
            }
            if ("type" in rawdata[i]) {
                n1[rawdata[i].target].type = rawdata[i].type;
            }
            if (industry_link) {
                n1[rawdata[i].source].industry = rawdata[i].source;
            }
        }
    }
    var l1 = {}
    var counter = 0
    var n2 = []
    if (left_party_color || right_party_color) {
        for(var key in n1) {
            if (n1[key].party == "Democratic") {
                n2[counter] = {"id": key, "color": 0.99}
            } else if (n1[key].party == "Republican") {
                n2[counter] = {"id": key, "color": 0.01}
            } else if (n1[key].party == "REP") {
                n2[counter] = {"id": key, "color": 0.01}
            } else if (n1[key].party == "DEM") {
                n2[counter] = {"id": key, "color": 0.99}
            } else if (n1[key].hasOwnProperty("proportion")) {
                n2[counter] = {"id": key, "color": n1[key].proportion}
            } else {
                n2[counter] = {"id": key}
            }
            if (n1[key].hasOwnProperty("cand_id")) {
                n2[counter].cand_id =  n1[key].cand_id;
            }
            if (n1[key].hasOwnProperty("industry")) {
                n2[counter].industry =  n1[key].industry;
            }
            if (n1[key].hasOwnProperty("type")) {
                n2[counter].type =  n1[key].type;
            }
            l1[key] = counter;
            counter++;
        };
    } else {
        for (var key in n1) {
            n2[counter] = {"id": key}
            l1[key] = counter;
            counter++;
        };
    }
    l2 = []
    var counter = 0
    rawdata.forEach(function(value) {
        l2[counter] = {"source": l1[value.source], "target": l1[value.target], "value": +value.value }
        counter++;
    });
    console.log(n2);
    return {"nodes": n2, "links": l2 }
};

var linkZoom1 = function(d) {
    d3.select("#backbtn").style("display","block");
    var source = d.source.id;
    var target  = d.target.id;
    var sankeydata = d3.json("/api/industries?industry=" + encodeURIComponent(source) + "&party=" + encodeURIComponent(target) )
    sankeydata.then(function(d){
        //console.log(d)
        var clean_data = generateNL(d, true, true, true, true)
        var sankey = lib.sankeyModule("full", false, "#sankey", "sankey-content", false);
        sankey.industry_data(clean_data)
        sankey.plot_by_industry()
    });
};

var linkZoom2 = function(industry) {
    d3.select("#backbtn").style("display","block");
    //console.log(encodeURIComponent(industry));
    var sankeydata2 = d3.json("/api/industries?industry=" + encodeURIComponent(industry));
    sankeydata2.then(function(d){
        var clean_data = generateNL(d, true, true, true, true)
        var industryzoom = lib.sankeyModule("full", false, "#sankey", "sankey-content", false);
        industryzoom.industry_data(clean_data)
        industryzoom.plot_by_industry();
    });
};

var linkZoom3 = function(d) {
    d3.select("#backbtnsp").style("display","block");
    var source = d.source.id;
    var target  = d.target.id;
    var sankeydata = d3.json("/api/superpacs?superpac=" + encodeURIComponent(target) )
    sankeydata.then(function(d){
        console.log("superpac cand data");
        console.log(d);
        var clean_data = generateNL(d, true, true, true, false)
        var sankey = lib.sankeyModule("full", false, "#sankey", "sankey-content", true);
        sankey.industry_data(clean_data)
        sankey.plot_by_industry()
    });
};

var goback = function() {
    d3.select("#backbtn").style("display","none");
    var sankeydata = d3.json("/api/industries")
    sankeydata.then(function(d){
        var clean_data = generateNL(d, false, false, true, true)
        var sankey = lib.sankeyModule("full", true, "#sankey", "sankey-content", false);
        sankey.industry_data(clean_data)
        sankey.plot_by_industry()
    });
}
var gobacksp = function() {
    d3.select("#backbtnsp").style("display","none");
    var sankeydata = d3.json("/api/superpacs/sankey")
    sankeydata.then(function(d){
        var clean_data = generateNL(d, false, false, true, true)
        var sankey = lib.sankeyModule("full", true, "#sankey", "sankey-content", false);
        sankey.industry_data(clean_data)
        sankey.plot_by_industry()
    });

}


var sankeydata = d3.json(data_endpoint)
sankeydata.then(function(d){
    if (data_endpoint.startsWith("/api/candidates")) {
        var clean_data = generateNL(d, false, false, true, false)
        var sankey = lib.sankeyModule("tree", false, "#sankey", "sankey-content", false);
        $('#sankey').siblings('img').remove();
        $('#sankey2').siblings('img').remove();
    } else if (data_endpoint.startsWith("/api/industries")){
        var clean_data = generateNL(d, false, false, true, true)
        var sankey = lib.sankeyModule("full", true, "#sankey","sankey-content", false);
    } else if (data_endpoint.startsWith("/api/superpacs")){
        var clean_data = generateNL(d, false, false, true, false)
        console.log(clean_data);
        var sankey = lib.sankeyModule("full", false, "#sankey", "sankey-content", true);
    } else {
        return
    }
    sankey.industry_data(clean_data)
    sankey.plot_by_industry()
});

if (typeof industry_endpoint !== 'undefined') {
    var sankeydata = d3.json(industry_endpoint)
    sankeydata.then(function(d){
        var clean_data = generateNL(d, false, false, true, true)
        var sankey = lib.sankeyModule("tree", false, "#sankey2", "sankey-content2", false);
        sankey.industry_data(clean_data)
        sankey.plot_by_industry()
    });
}
