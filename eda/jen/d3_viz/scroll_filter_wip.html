<!DOCTYPE html>
<meta charset="utf-8">
<style>

	.link {
	  stroke: #c1c1c1;
    stroke-width: 2px;
    pointer-events: all;
	}

  .node circle {
	  pointer-events: all;
	  stroke: #777;
	  stroke-width: 1px;
	}
	
	div.tooltip {
    position: absolute;
    background-color: white;
    max-width; 200px;
    height: auto;
    padding: 1px;
    border-style: solid;
    border-radius: 4px;
    border-width: 1px;
    box-shadow: 3px 3px 10px rgba(0, 0, 0, .5);
    pointer-events: none;
  }
  
  /* Customize container for slider */
			.container {
				min-width: 640px;
			}
			@media (min-width: 768px) {
			  .container {
			    max-width: 1000px;
			  }
			}
			.container-narrow > hr {
			  margin: 30px 0;
			}

			
			.slider-example {
				padding-top: 10px;
				padding-bottom: 55px;
				margin: 35px 0;
			}

  
</style>

 <!-- core CSS slider -->
<link href="/~jennifer.p/capstone/filter/slidertest2/bootstrap.min.css" rel="stylesheet">
<link href="/~jennifer.p/capstone/filter/slidertest2/bootstrap-slider.css" rel="stylesheet">
    
<body>
<p> Double click on a node to pin it. A single click releases the node </p>
	
	<p>Range selector, options specified via data attribute.</p>
	<div class="well">
		Filter by price interval: <b>€ 10</b> <input id="ex2" type="text" class="span2" value="" data-slider-min="10" data-slider-max="1000" data-slider-step="5" data-slider-value="[250,450]"/> <b>€ 1000</b>
	</div>
      	


<svg width="1260" height="1260"></svg>
<div class="ui-widget">
   <input id="search">
    <button type="button" onclick="searchNode()">Search</button>
</div>

</body>
<script type='text/javascript' src="/~jennifer.p/capstone/filter/slidertest2/jquery.min.js" ></script>
<script>var $x = jQuery.noConflict();</script>
<script type='text/javascript' src="/~jennifer.p/capstone/filter/slidertest2/bootstrap-slider.js"></script>
<script type='text/javascript' src="/~jennifer.p/capstone/filter/slidertest2/highlight.min.js"></script>
<script>hljs.initHighlightingOnLoad();</script>

<script src="https://d3js.org/d3.v4.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3-legend/2.24.0/d3-legend.min.js"></script>
<script src="https://d3js.org/d3-scale-chromatic.v1.min.js"></script>



<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js">
<!--var $y = $( "#y" );</script>-->
<link type="text/css" href="http://code.jquery.com/ui/1.11.0/themes/smoothness/jquery-ui.css" rel="stylesheet" /> 
<script src="http://code.jquery.com/ui/1.10.2/jquery-ui.js" ></script> 



<script>
	$x(document).ready(function() {
		/* Example 1 */
		$x('#ex1').slider({
			formatter: function(value) {
			//var val = $('#ex').slider("option", "value");
			//console.log(val)
				return 'Current value: ' + value;
				}
			});
		/* Example 2 */
		  $x("#ex2").slider({});
		//var val = $x("#ex2").slider({});
		//console.log(val)
		/*function attachSlider() {
                var low = val($('#ex1').slider("values", 0));
                var high = val($('#ex1').slider("values", 1));
				console.log(low)
				console.log(high)
            }*/
	});
/*var val = document.getElementById('ex2').value;
$x("#ex2").slider();
$x("#ex2").on("slide", function(slideEvt) {
	var val = $("#data-slider-min").value;
	console.log(val)
//});

var Xslide =  Slider('#ex2'); 

Xslide.on('slideStop', function (value) { document.getElementById('xval').innerHTML = this.value; 

console.log(innerHTML)
})*/

/*var slider2 = document.getElementById("ex2");
var output = document.getElementById("data-slider-min");

// Update the current slider value (each time you drag the slider handle)
slider2.oninput = function() {
    output.innerHTML = this.value;
	console.log(output.innerHTML)}*/
	
//var val = $('#ex2').slider("option", "value");
//console.log(val)

/*$x('#ex2').slider({
    change: function(event, ui) { 
        alert(ui.value); 
		console.log(ui.value)
    } 
});​*/

var max_node_size = 200000


var color = d3.scaleOrdinal() // D3 Version 4
  .domain(["D", "R", "I","Industry"])
  .range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);
			
var tooltip = d3.select("body")
	.append("div")
	.attr("class", "tooltip")
	.style("opacity", 0);
 
const svg = d3.select('svg'),
        width = +svg.attr('width'),
  			height = +svg.attr('height');
  
  
/*  //add zoom capabilities 
var zoom_handler = d3.zoom()
    .on("zoom", zoom_actions);

zoom_handler(svg);

//Zoom functions 
function zoom_actions(){
    g.attr("transform", d3.event.transform)
}*/
  
d3.json("industry_amt_winner_mini.json", function(error, graph) {
  if (error) throw error;
		var largeNodes = [];  
		
			graph.nodes
				 .filter(function(d){
						if (d.contribution_total > max_node_size){
						largeNodes.push(d);}
						return d.contribution_total > max_node_size; })
			//console.log(largeNodes)
			
    

  const simulation = d3.forceSimulation()
    .nodes(graph.nodes)
    .force('link', d3.forceLink().id(d => d.name))
    .force('charge', d3.forceManyBody().strength(-225))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .on('tick', ticked);

  simulation.force('link')
    .links(graph.links);

  let link = svg.selectAll('line')
    .data(graph.links)
    .enter().append('line');
	
	//console.log(largeNodes)
	//console.log(graph)
	

  link  
	.filter(function(d){if (largeNodes.indexOf(d.target) > -1){return d}})
    .attr('class', 'link')
  	.on('mouseover.tooltip', function(d) {
      	tooltip.transition()
        	.duration(300)
        	.style("opacity", .8);
      	tooltip.html("Source:"+ d.source.name+ 
                     "<p/>Target:" + d.target.name +
                    "<p/>Strength:"  + d.value)
        	.style("left", (d3.event.pageX) + "px")
        	.style("top", (d3.event.pageY + 10) + "px");
    	})
    	.on("mouseout.tooltip", function() {
	      tooltip.transition()
	        .duration(100)
	        .style("opacity", 0);
	    })
  		.on('click.fade', fade(1))
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
	  
	
  node
	.filter(function(d){
						if (d.contribution_total > max_node_size){
						largeNodes.push(d);}
						return d.contribution_total > max_node_size; })
	.append('circle')
	.attr('r', function(d) {return(Math.sqrt(d.contribution_total)/25)}) //used to be R  //and function(d) {console.log(d.target.value)}) 
	.attr("fill", function(d) {return color(d.group);})
	///trying to add winner highlight 	
	.style("stroke-width", function(d) {
			if (d.winner_ind == "W"){return 4}
			else {return 0};})
	.style("stroke", function(d) {
		   if (d.winner_ind == "W" ){return "#32CD32"};})
    .on('mouseover.tooltip', function(d) {
      	tooltip.transition()
        	.duration(300)
        	.style("opacity", .8);
      	tooltip.html("Name:" + d.name + "<p/>Party:" + d.group)
        	.style("left", (d3.event.pageX) + "px")
        	.style("top", (d3.event.pageY + 10) + "px");
    	})
  	.on('dblclick.fade', fade(0.1))
    .on("mouseout.tooltip", function() {
        tooltip.transition()
	        .duration(100)
	        .style("opacity", 0);
	    })
  	.on('click.fade', fade(1))
	.on("mousemove", function() {
	  tooltip.style("left", (d3.event.pageX) + "px")
		.style("top", (d3.event.pageY + 10) + "px");
	})
  	.on('click',releasenode)
	//.on('dblclick', isConnected) //Added code 

	
	
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
		
		console.log(d)
		console.log(o)
		 var new_data = d3.nest()
		  .key(function(j) { return j.group;})
		  .rollup(function(j) {
		   return d3.sum(j, function(g) {return g.contribution_total; });
		  }).map(d); //.entries(d);
		  //new_data
		  //console.log(new_data)
		  
		  var expensesByName = d3.nest()
		  .key(function(g) { return g.group; })
		  .entries(d);
		  //.forEach(node);
			//console.log(expensesByName )
			
		var contributionsByName = d3.nest()
		  .key(function(g) { return g.contribution_total; })
		  .entries(d);
		  //.forEach(node);
		//console.log(contributionsByName)
	
		//var numbers = d
		//console.log(d3.sum(d.contribution_total)) //d.value
		//var total_j = numbers.reduce(function(sum, value) {
		//return sum + value;
		//}, 0);
//console.log(total_j);
        this.setAttribute('fill-opacity', thisOpacity);
        return thisOpacity;
      });

      link.style('stroke-opacity', o => (o.source === d || o.target === d ? 1 : opacity));

    };
  }
  ///legend colors scale
  var sequentialScale = d3.scaleOrdinal() // D3 Version 4
							.domain(["D", "R", "I","Industry"])
							.range(["#0000FF","#FF0000" , "#009933" , "#C0C0C0"]);


svg.append("g")
  .attr("class", "legendSequential")
  .attr("transform", "translate("+(width-140)+","+(height-300)+")");

var legendSequential = d3.legendColor()
    .shapeWidth(30)
    .cells(11)
    .orient("vertical")
		.title("Group number by color:")
		.titleWidth(100)
    .scale(sequentialScale) 

svg.select(".legendSequential")
  .call(legendSequential); 
  
 

//trying to add search
graph = d3.json('industry_amt_winner_mini.json', function(error, graph) {
		//console.log(graph)
var optArray = [];
for (var i = 0; i < graph.nodes.length - 1; i++) {
    optArray.push(graph.nodes[i].name);
}

optArray = optArray.sort();

$(function () {
    $("#search").autocomplete({
        source: optArray
    });
});

});

}) //data closer

//} //slider closer

function searchNode() {
    //find the node
    var selectedVal = document.getElementById('search').value;
    var node = svg.selectAll(".node");
    if (selectedVal == "none") {
        node.style("stroke", "white").style("stroke-width", "1");
    } else {
        var selected = node.filter(function (d, i) {
            return d.name != selectedVal;
        });
        selected.style("opacity", "0");
        var link = svg.selectAll(".link")
        link.style("opacity", "0");
        d3.selectAll(".node, .link").transition()
            .duration(5000)
            .style("opacity", 1);
    }
}



</script>
