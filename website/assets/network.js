
var color = d3.scaleOrdinal() // D3 Version 4
  .domain(["D", "R", "I","Industry"])
  .range(["#0000FF","#FF0000" , "#009933" , "#C0C0C0"]);
			


/*var color = d3.scaleOrdinal(d3.schemeCategory10);
color(4);
  color(3);
  color(2);
  color(1);
  color(0);
  color(5);
  color(6);
  color(7);
  color(8);
  color(9);
  color(10);*/
  
  

var tooltip = d3.select("body")
	.append("div")
	.attr("class", "tooltip")
	.style("opacity", 0);

//d3.json("function_test_names.json", function(error, graph) {
var contentDiv = document.getElementById("content")
var contentWidth = contentDiv.clientWidth - 40;
var networkdata = d3.json("/networkdata")
networkdata.then(function( graph) {
 	const svg = d3.select('svg').attr("width", contentWidth).attr("height", 800);

        const width = +svg.attr('width'),
  		height = +svg.attr('height');
    

  
//  const width = 960;
//   const height = 700;

  const simulation = d3.forceSimulation()
    .nodes(graph.nodes)
    .force('link', d3.forceLink().id(d => d.name))
    .force('charge', d3.forceManyBody())
    .force('center', d3.forceCenter(width / 2, height / 2))
    //.force('center', d3.forceCenter())
    .on('tick', ticked);

  simulation.force('link')
    .links(graph.links);

  const R = 6;

 

  let link = svg.selectAll('line')
    .data(graph.links)
    .enter().append('line');

  link  
    .attr('class', 'link')
  	.on('mouseover.tooltip', function(d) {
      	tooltip.transition()
        	.duration(300)
        	.style("opacity", .8);
      	tooltip.html("Source:"+ d.source.id + 
                     "<p/>Target:" + d.target.id +
                    "<p/>Strength:"  + d.value)
        	.style("left", (d3.event.pageX) + "px")
        	.style("top", (d3.event.pageY + 10) + "px");
    	})
    	.on("mouseout.tooltip", function() {
	      tooltip.transition()
	        .duration(100)
	        .style("opacity", 0);
	    })
  		.on('mouseout.fade', fade(1))
	    .on("mousemove", function() {
	      tooltip.style("left", (d3.event.pageX) + "px")
	        .style("top", (d3.event.pageY + 10) + "px");
	    });
;

  let node = svg.selectAll('.node')
    .data(graph.nodes)
    .enter().append('g')
    .attr('class', 'node')
    .call(d3.drag()
    	.on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));;

  node.append('circle')
    .attr('r', R)
  	.attr("fill", function(d) { return color(d.group);}) 	
    .on('mouseover.tooltip', function(d) {
      	tooltip.transition()
        	.duration(300)
        	.style("opacity", .8);
      	tooltip.html("Name:" + d.name + "<p/>group:" + d.group)
        	.style("left", (d3.event.pageX) + "px")
        	.style("top", (d3.event.pageY + 10) + "px");
    	})
  	.on('mouseover.fade', fade(0.1))
    .on("mouseout.tooltip", function() {
        tooltip.transition()
	        .duration(100)
	        .style("opacity", 0);
	    })
  	.on('mouseout.fade', fade(1))
	    .on("mousemove", function() {
	      tooltip.style("left", (d3.event.pageX) + "px")
	        .style("top", (d3.event.pageY + 10) + "px");
	    })
  	.on('dblclick',releasenode)
    
	
 //Jen removed

  function ticked() {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

    node
      .attr('transform', d => `translate(${d.x},${d.y})`);
  }

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0);
  //d.fx = null;
  //d.fy = null;
}
function releasenode(d) {
    d.fx = null;
    d.fy = null;
}
  
  const linkedByIndex = {};
  graph.links.forEach(d => {
    linkedByIndex[`${d.source.index},${d.target.index}`] = 1;
  });

  function isConnected(a, b) {
    return linkedByIndex[`${a.index},${b.index}`] || linkedByIndex[`${b.index},${a.index}`] || a.index === b.index;
  }

  function fade(opacity) {
    return d => {
      node.style('stroke-opacity', function (o) {
        const thisOpacity = isConnected(d, o) ? 1 : opacity;
        this.setAttribute('fill-opacity', thisOpacity);
        return thisOpacity;
      });

      link.style('stroke-opacity', o => (o.source === d || o.target === d ? 1 : opacity));

    };
  }
  var sequentialScale = d3.scaleOrdinal() // D3 Version 4
							.domain(["D", "R", "I","Industry"])
							.range(["#0000FF","#FF0000" , "#009933" , "#C0C0C0"]);

svg.append("g")
  .attr("class", "legendSequential")
  .attr("transform", "translate("+(width-140)+","+(height-300)+")");

var legendSequential = d3.legendColor().shapeWidth(30).cells(11).scale(sequentialScale).title("Group number by color").orient("vertical");
//.orient("vertical").title("Group number by color:").titleWidth(100).scale(sequentialScale);
//var legendSequential = d3.legendColor().title("Group number by color:").titleWidth(100).scale(sequentialScale);

svg.select(".legendSequential").call(legendSequential); 

  
})
//trying to add search
//var optArray = [];
//for (var i = 0; i < graph.nodes.length - 1; i++) {
//    optArray.push(graph.nodes[i].name);
//}
//optArray = optArray.sort();
//$(function () {
//    $("#search").autocomplete({
//        source: optArray
//    });
//});
//function searchNode() {
//    //find the node
//    var selectedVal = document.getElementById('search').value;
//    var node = svg.selectAll(".node");
//    if (selectedVal == "none") {
//        node.style("stroke", "white").style("stroke-width", "1");
//    } else {
//        var selected = node.filter(function (d, i) {
//            return d.name != selectedVal;
//        });
//        selected.style("opacity", "0");
//        var link = svg.selectAll(".link")
//        link.style("opacity", "0");
//        d3.selectAll(".node, .link").transition()
//            .duration(5000)
//            .style("opacity", 1);
//    }
//}