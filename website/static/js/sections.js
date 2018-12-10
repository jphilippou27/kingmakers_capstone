
/**
 * scrollVis - encapsulates
 * all the code for the visualization
 * using reusable charts pattern:
 * http://bost.ocks.org/mike/chart/
 */
var scrollVis = function () {
  // constants to define the size
  // and margins of the vis area.
  var width = 1000;
  var height = 1000;
  var margin = { top: 0, left: 20, bottom: 40, right: 10 };

  // Keep track of which visualization
  // we are on and which was the last
  // index activated. When user scrolls
  // quickly, we want to call all the
  // activate functions that they pass.
  var lastIndex = -1;
  var activeIndex = 0;

  // Sizing for the grid visualization
  var squareSize = 6;
  var squarePad = 2;
  var numPerRow = width / (squareSize + squarePad);

  // main svg used for visualization
  var svg = null;

  // d3 selection that will be used
  // for displaying visualizations
  var g = null;

  // We will set the domain when the
  // data is processed.
  // @v4 using new scale names
  var xBarScale = d3.scaleLinear()
    .range([0, width]);

  // The bar chart display is horizontal
  // so we can use an ordinal scale
  // to get width and y locations.
  // @v4 using new scale type
  var yBarScale = d3.scaleBand()
    .paddingInner(0.08)
    .domain([0, 1, 2])
    .range([0, height - 50], 0.1, 0.1);

  // Color is determined just by the index of the bars
  var barColors = { 0: '#008080', 1: '#399785', 2: '#5AAF8C' };

  // The histogram display shows the
  // first 30 minutes of data
  // so the range goes from 0 to 30
  // @v4 using new scale name
  var xHistScale = d3.scaleLinear()
    .domain([0, 30])
    .range([0, width - 20]);

  // @v4 using new scale name
  var yHistScale = d3.scaleLinear()
    .range([height, 0]);

  // The color translation uses this
  // scale to convert the progress
  // through the section into a
  // color value.
  // @v4 using new scale name
  var coughColorScale = d3.scaleLinear()
    .domain([0, 1.0])
    .range(['#008080', 'red']);

  // You could probably get fancy and
  // use just one axis, modifying the
  // scale, but I will use two separate
  // ones to keep things easy.
  // @v4 using new axis name
  var xAxisBar = d3.axisBottom()
    .scale(xBarScale);

  // @v4 using new axis name
  var xAxisHist = d3.axisBottom()
    .scale(xHistScale)
    .tickFormat(function (d) { return d + ' min'; });

  // When scrolling to a new section
  // the activation function for that
  // section is called.
  var activateFunctions = [];
  // If a section has an update function
  // then it is called while scrolling
  // through the section with the current
  // progress through the section.
  var updateFunctions = [];

  /**
   * chart
   *
   * @param selection - the current d3 selection(s)
   *  to draw the visualization in. For this
   *  example, we will be drawing it in #vis
   */
  var chart = function (selection) {
    selection.each(function (rawData) {
      // create svg and give it a width and height
      svg = d3.select(this).selectAll('svg').data([wordData]);
      var svgE = svg.enter().append('svg');
      // @v4 use merge to combine enter and existing selection
      svg = svg.merge(svgE);

      svg.attr('width', width + margin.left + margin.right);
      svg.attr('height', height + margin.top + margin.bottom);

      svg.append('g');


      // this group element will be used to contain all
      // other elements.
      g = svg.select('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      // perform some preprocessing on raw data
      var wordData = getWords(rawData);
      // filter to just include filler words
      var fillerWords = getFillerWords(wordData);

      // get the counts of filler words for the
      // bar chart display
      var fillerCounts = groupByWord(fillerWords);
      // set the bar scale's domain
      var countMax = d3.max(fillerCounts, function (d) { return d.value;});
      xBarScale.domain([0, countMax]);

      // get aggregated histogram data

      var histData = getHistogram(fillerWords);
      // set histogram's domain
      var histMax = d3.max(histData, function (d) { return d.length; });
      yHistScale.domain([0, histMax]);

      setupVis(wordData, fillerCounts, histData);

      setupSections();
    });
  };


  /**
   * setupVis - creates initial elements for all
   * sections of the visualization.
   *
   * @param wordData - data object for each word.
   * @param fillerCounts - nested data that includes
   *  element for each filler word type.
   * @param histData - binned histogram data
   */
  var setupVis = function (wordData, fillerCounts, histData) {
    // axis
    g.append('g')
      .attr('class', 'x axis')
      .attr('transform', 'translate(0,' + height + ')')
      .call(xAxisBar);
    g.select('.x.axis').style('opacity', 0);

    // count openvis title
    g.append('text')
      .attr('class', 'title openvis-title')
      .attr('x', width / 2)
      .attr('y', height / 3)
      .text('Network');

    g.append('text')
      .attr('class', 'sub-title openvis-title')
      .attr('x', width / 2)
      .attr('y', (height / 3) + (height / 5))
      .text('Visualizations');

    g.selectAll('.openvis-title')
      .attr('opacity', 0);

    // count filler word count title
    g.append('text')
      .attr('class', 'title count-title highlight')
      .attr('x', width / 2)
      .attr('y', height / 3)
      .text('Toy Example');


    g.selectAll('.count-title')
      .attr('opacity', 0);

    // square grid

    // barchart
    // @v4 Using .merge here to ensure
    // new and old data have same attrs applied
    var bars = g.selectAll('.bar').data(fillerCounts);
    var barsE = bars.enter()
      .append('rect')
      .attr('class', 'bar');
    bars = bars.merge(barsE)
      .attr('x', 0)
      .attr('y', function (d, i) { return yBarScale(i);})
      .attr('fill', function (d, i) { return barColors[i]; })
      .attr('width', 0)
      .attr('height', yBarScale.bandwidth());

    var barText = g.selectAll('.bar-text').data(fillerCounts);
    barText.enter()
      .append('text')
      .attr('class', 'bar-text')
      .text(function (d) { return d.key + '…'; })
      .attr('x', 0)
      .attr('dx', 15)
      .attr('y', function (d, i) { return yBarScale(i);})
      .attr('dy', yBarScale.bandwidth() / 1.2)
      .style('font-size', '110px')
      .attr('fill', 'white')
      .attr('opacity', 0);

    // histogram
    // @v4 Using .merge here to ensure
    // new and old data have same attrs applied
    var hist = g.selectAll('.hist').data(histData);
    var histE = hist.enter().append('rect')
      .attr('class', 'hist');
    hist = hist.merge(histE).attr('x', function (d) { return xHistScale(d.x0); })
      .attr('y', height)
      .attr('height', 0)
      .attr('width', xHistScale(histData[0].x1) - xHistScale(histData[0].x0) - 1)
      .attr('fill', barColors[0])
      .attr('opacity', 0);


    // arrowhead from
    // http://logogin.blogspot.com/2013/02/d3js-arrowhead-markers.html
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('refY', 2)
      .attr('markerWidth', 6)
      .attr('markerHeight', 4)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M 0,0 V 4 L6,2 Z');

    g.append('path')
      .attr('class', 'cough cough-arrow')
      .attr('marker-end', 'url(#arrowhead)')
      .attr('d', function () {
        var line = 'M ' + ((width / 2) - 10) + ' ' + 80;
        line += ' l 0 ' + 230;
        return line;
      })
      .attr('opacity', 0);
  };

  /**
   * setupSections - each section is activated
   * by a separate function. Here we associate
   * these functions to the sections based on
   * the section's index.
   *
   */
  var setupSections = function () {
    // activateFunctions are called each
    // time the active section changes
    activateFunctions[0] = showTitle;
    activateFunctions[1] = draw_toy_network;
	//showFillerTitle;
    activateFunctions[2] = demo_analysis_politicianI;
    activateFunctions[3] = demo_analysis_politicianII;
    activateFunctions[5] = draw_filtered_nodes;
    activateFunctions[4] = draw_politician_network;
    activateFunctions[6] = draw_individual_network;
    activateFunctions[7] = draw_committee_network;
    /*activateFunctions[7] = showCough;
    activateFunctions[8] = showHistAll;*/

    // updateFunctions are called while
    // in a particular section to update
    // the scroll progress in that section.
    // Most sections do not need to be updated
    // for all scrolling and so are set to
    // no-op functions.
    for (var i = 0; i < 9; i++) {
      updateFunctions[i] = function () {};
    }
    updateFunctions[7] = updateCough;
  };

  /**
   * ACTIVATE FUNCTIONS
   *
   * These will be called their
   * section is scrolled to.
   *
   * General pattern is to ensure
   * all content for the current section
   * is transitioned in, while hiding
   * the content for the previous section
   * as well as the next section (as the
   * user may be scrolling up or down).
   *
   */

  /**
   * showTitle - initial title
   *
   * hides: count title
   * (no previous step to hide)
   * shows: intro title
   *
   */
  function showTitle() {
    g.selectAll('.count-title')
      .transition()
      .duration(0)
      .attr('opacity', 0);

    g.selectAll('.openvis-title')
      .transition()
      .duration(600)
      .attr('opacity', 1.0);
	//removes network
	d3.selectAll(".node").remove();
	d3.selectAll("edge").remove();
	d3.selectAll('line.edge').remove();
	//removes legend
	d3.selectAll('rect').remove();
	d3.selectAll('tspan').remove();
	d3.selectAll('text.label').remove();
    //d3.selectAll('link').remove();

	//removes example analysis
	d3.selectAll('image').remove();
  }

  /**
   * showFillerTitle - filler counts
   *
   * hides: intro title
   * hides: square grid
   * shows: filler count title
   *
   */
  function showFillerTitle() {

    g.selectAll('.count-title')
      .transition()
      .duration(600)
      .attr('opacity', 1.0);
  }

  //Jen's Network Toy Example
    // @v4 Using .merge here to ensure
    // new and old data have same attrs applied
	function draw_toy_network(){
	//load the data
		//function find_data(){}

	//remove title stuff
   g.selectAll('.openvis-title')
      .transition()
      .duration(0)
      .attr('opacity', 0);
   g.selectAll('.openvis-title')
      .transition()
      .duration(0)
      .attr('opacity', 0);

    g.selectAll('.square')
      .transition()
      .duration(0)
      .attr('opacity', 0);

		//removes OLD network
	d3.selectAll(".node").remove();
	d3.selectAll("edge").remove();
	d3.selectAll('line.edge').remove();
	//removes example analysis
	d3.selectAll('image').remove();

		var color = d3.scaleOrdinal() // D3 Version 4
		  .domain(["D", "R", "I","Industry"])
		  .range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);

		var tooltip = d3.select("body")
			.append("div")
			.attr("class", "tooltip")
			.style("opacity", 0);

		const svg = d3.select('svg')
				//width = +svg.attr('width'),
					//height = +svg.attr('height');

		d3.json("/static/data_for_testing/toy_network.json", function(error, graph) {
		  if (error) throw error;


		  const simulation = d3.forceSimulation()
			.nodes(graph.nodes)
			.force('link', d3.forceLink().id(d => d.name))
			.force('charge', d3.forceManyBody().strength(-100))
			.force('center', d3.forceCenter(width / 2, height / 2))
			.on('tick', ticked);

		  simulation.force('link')
			.links(graph.links);

		  let link = svg.selectAll('line')
			.data(graph.links)
			.enter().append('line');

		  link
			.attr('class', 'edge')
			.on('mouseover.tooltip', function(d) {
				tooltip.transition()
					.duration(300)
					.style("opacity", .8);
				tooltip.html("Source:"+ d.source.name+
							 "<p/>Target:" + d.target.name +
							"<p/>Strength:"  + d.value )
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


				  node.append('circle')
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
						tooltip.html("Name:" + d.name + "<p/>Party:" + d.group + "<p/>Total Contributions: " + d.contribution_total)
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
							  ///legend colors scale
							  var sequentialScale = d3.scaleOrdinal() // D3 Version 4
														.domain(["D", "R", "I","Industry"])
														.range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);


							svg.append("g")
							  .attr("class", "legendSequential")
							  .attr("transform", "translate("+(width-860)+","+(height-300)+")");

							var legendSequential = d3.legendColor()
								.shapeWidth(30)
								.cells(11)
								.orient("vertical")
									.title("Group number by color:")
									.titleWidth(100)
								.scale(sequentialScale)

							svg.select(".legendSequential")
							  .call(legendSequential);
		})
	}
	function demo_analysis_politicianI(){

	//removes OLD network
	d3.selectAll(".node").remove();
	d3.selectAll("edge").remove();
	d3.selectAll('line.edge').remove();

	//removes legend
	d3.selectAll('rect').remove();
	d3.selectAll('tspan').remove();
	d3.selectAll('text.label').remove();

	//removes example analysis
	d3.selectAll('image').remove();

		const svg = d3.select('svg')

		var myimage = svg.append('image')
			.attr('xlink:href', 'https://s3.us-south.objectstorage.softlayer.net/staticassets2/Demo_network_analysis.png')
			.attr('width', 1000)
			.attr('height', 1000)


	}
	function demo_analysis_politicianII(){

	//removes OLD network
	d3.selectAll(".node").remove();
	d3.selectAll("edge").remove();
	d3.selectAll('line.edge').remove();

	//removes legend
	d3.selectAll('rect').remove();
	d3.selectAll('tspan').remove();
	d3.selectAll('text.label').remove();

	//removes example analysis
	d3.selectAll('image').remove();

		const svg = d3.select('svg')

		var myimage = svg.append('image')
			.attr('xlink:href', 'https://s3.us-south.objectstorage.softlayer.net/staticassets2/Demo_network_analysisII.png')
			.attr('width', 1000)
			.attr('height', 1000)


	}
  /**
   * showGrid - square grid
   *
   * hides: filler count title
   * hides: filler highlight in grid
   * shows: square grid
   *
   */

  function showGrid() {
  }
  /**
   * Draw full network map for Politicians
   *
   * hides: barchart, text and axis
   * shows: square grid and highlighted
   *  filler words. also ensures squares
   *  are moved back to their place in the grid
   */
  function draw_politician_network(){
	//load the data
		//function find_data(){}

	//remove title stuff
	g.selectAll('.openvis-title')
      .transition()
      .duration(0)
      .attr('opacity', 0);

    g.selectAll('.square')
      .transition()
      .duration(0)
      .attr('opacity', 0);

	  //remove toy network
	  d3.selectAll(".node").remove();
	  d3.selectAll("edge").remove();
	  d3.selectAll('line.edge').remove();

	  //removes example analysis
	d3.selectAll('image').remove();

		var color = d3.scaleOrdinal() // D3 Version 4
		  .domain(["D", "R", "I","Industry"])
		  .range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);

		var tooltip = d3.select("body")
			.append("div")
			.attr("class", "tooltip")
			.style("opacity", 0);

		const svg = d3.select('svg')
				//width = +svg.attr('width'),
					//height = +svg.attr('height');

		//updated
		//var networkdata = d3.json(data_endpoint)
		//networkdata.then(function( graph) {
		//d3.json("static/data_for_testing/industry_amt_winner_mini.json", function(error, graph) {
        var candName = $y('#search2').val();
        if (candName === "") {
            candName = "Sean Patrick Maloney (D)";
        }
        dataEndpoint = '/networkdata/' + candName;
        console.log(dataEndpoint);
		d3.json(dataEndpoint, function(error, graph) {
		  if (error) throw error;


		  const simulation = d3.forceSimulation()
			.nodes(graph.nodes)
			.force('link', d3.forceLink().id(d => d.name))
			.force('charge', d3.forceManyBody().strength(-100))
			.force('center', d3.forceCenter(width / 2, height / 2))
			.on('tick', ticked);

		  simulation.force('link')
			.links(graph.links);

		  let link = svg.selectAll('line')
			.data(graph.links)
			.enter().append('line');

		  link
			.attr('class', 'edge')
			.on('mouseover.tooltip', function(d) {
				tooltip.transition()
					.duration(300)
					.style("opacity", .8);
				tooltip.html("Source:"+ d.source.name+
							 "<p/>Target:" + d.target.name +
							"<p/>Strength:"  + d3.format(",.0f")(d.value ))
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


				  node.append('circle')
					.attr('r', function(d) {return(Math.sqrt(d.contribution_total)/125)}) //used to be R  //and function(d) {console.log(d.target.value)})
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
						tooltip.html("Name:" + d.name + "<p/>Party:" + d.group + "<p/>Total Contributions: " + d3.format(",.0f")(d.contribution_total))
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
							  ///legend colors scale
							  var sequentialScale = d3.scaleOrdinal() // D3 Version 4
														.domain(["D", "R", "I","Industry"])
														.range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);


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
			//d3.json("/networkdata", function(error, graph) {
		//  if (error) throw error;
        var candName = $y('#search2').val();
        if (candName === "") {
            candName = "Sean Patrick Maloney (D)";
        }
        dataEndpoint = '/networkdata/' + candName;
        console.log(dataEndpoint);
        graph = d3.json(dataEndpoint, function(error, graph) {
		//console.log(graph)
		var optArray = [];
		for (var i = 0; i < graph.nodes.length - 1; i++) {
			optArray.push(graph.nodes[i].name);
		}

		optArray = optArray.sort();

		$y(function () {
			$y("#search").autocomplete({
				source: optArray});
						});

		}); //end of find search

graph = d3.json('/networkNodeList', function(error, data) {
		//console.log(graph)
	var optArray = [];
	for (var i = 0; i < data.length; i++) {
		optArray.push( data[i].firstlastp);
	}
		//}

		optArray = optArray.sort();

		$y(function () {
			$y("#search2").autocomplete({
				source: optArray});
						});

		}); //end of find search

})//end of Data ??

$y("#button").on("click", function searchNode() {
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
})

// $("#button2").on("click", function() { console.log('hey'); })
$y("#button2").on("click", function() { draw_politician_network();});

}//end of draw politican network
  
 /**
   * filter_nodes
   *
   * hides: prior network w. committee data
   * shows: filtered network
   *
   *
   */

function draw_filtered_nodes() {

	//load the data
		//function find_data(){}

	//remove title stuff
	g.selectAll('.openvis-title')
      .transition()
      .duration(0)
      .attr('opacity', 0);
	g.selectAll('.openvis-title')
      .transition()
      .duration(0)
      .attr('opacity', 0);

    g.selectAll('.square')
      .transition()
      .duration(0)
      .attr('opacity', 0);
	//removes example analysis
	d3.selectAll('image').remove();

		function redraw_post_change() {

			//removes OLD network
			d3.selectAll(".node").remove();
			d3.selectAll("edge").remove();
			d3.selectAll('line.edge').remove();

			/*if (max_node_size == null){
			var max_node_size = 15000000}
			if (min_node_size ==  null){
				var min_node_size = 200000}*/

			console.log("starting Min " + min_node_size)
			console.log("starting max " + max_node_size)

			var color = d3.scaleOrdinal() // D3 Version 4
			  .domain(["D", "R", "I","Industry"])
			  .range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);

			var tooltip = d3.select("body")
				.append("div")
				.attr("class", "tooltip")
				.style("opacity", 0)


			const svg = d3.select('svg')


			/*  //add zoom capabilities
			var zoom_handler = d3.zoom()
				.on("zoom", zoom_actions);

			zoom_handler(svg);

			//Zoom functions
			function zoom_actions(){
				g.attr("transform", d3.event.transform)
			}*/
			//var  max_node = 0
			 var candName = $y('#search2').val();
			if (candName === "") {
			    candName = "Sean Patrick Maloney (D)";
			}
			dataEndpoint = '/networkdata/' + candName;
			console.log(dataEndpoint);
				d3.json(dataEndpoint, function(error, graph) {
			  if (error) throw error;
			  //console.log(d3.max(d3.values(graph.nodes.contribution_total)))
			  var max_node = d3.max(graph.nodes, function(d) { return d.contribution_total; })
				//console.log(max_node)
					console.log(graph.nodes)

					var largeNodes = [];
						graph.nodes
							.filter(function(d){
									if (d.group == "Industry"){largeNodes.push(d);}
							})

						graph.nodes
							 .filter(function(d){
									if (d.contribution_total > min_node_size && d.contribution_total < max_node_size ){
									largeNodes.push(d);}
									return d.contribution_total ;})

						//console.log(largeNodes)



			  const simulation = d3.forceSimulation()
				.nodes(graph.nodes)
				.force('link', d3.forceLink().id(d => d.name))
				.force('charge', d3.forceManyBody().strength(-100))
				.force('center', d3.forceCenter(width / 2, height / 2))
				.on('tick', ticked);

			  simulation.force('link')
				.links(graph.links);

			  let link = svg.selectAll('line')
				.data(graph.links)
				.enter().append('line');

				console.log(largeNodes)
			//matching_edges = []

			  link
				//.filter(function(d){if (largeNodes.indexOf(d.target) > -1){
					//matching_edges.push(d.target)
				//	return d}}) //I don't think I need this since I moved the filter higher up
				//.transition().duration(500)
				.attr('class', 'edge')
				.on('mouseover.tooltip', function(d) {
					tooltip.transition()
						.duration(300)
						.style("opacity", .8);
					tooltip.html("Source:"+ d.source.name+
								 "<p/>Target:" + d.target.name +
								"<p/>Strength:"  + d3.format(",.0f") (d.value))
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

			//console.log('edges ' +matching_edges)

			let node = svg.selectAll('.node')
				.data(graph.nodes)
				.enter().append('g')
				.attr('class', 'node')
				.call(d3.drag()
					.on("start", dragstarted)
				  .on("drag", dragged)
				  .on("end", dragended));;


			  node
				.filter(function(d){if ((d.contribution_total > min_node_size && d.contribution_total < max_node_size ) || (d.group == "Industry")) {return d.contribution_total; }})
				.append('circle')
				.attr('r', function(d) {return(Math.sqrt(d.contribution_total)/125)}) //used to be R  //and function(d) {console.log(d.target.value)})
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
					tooltip.html("Name:" + d.name + "<p/>Party:" + d.group + "<p/>Total Contributions: " + d3.format(",.0f")(d.contribution_total))
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
			  console.log(graph.links)
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
					var contributionsByName = d3.nest()
					  .key(function(g) { return g.contribution_total; })
					  .entries(d);
					this.setAttribute('fill-opacity', thisOpacity);
					return thisOpacity;
				  });

				  link.style('stroke-opacity', o => (o.source === d || o.target === d ? 1 : opacity));

				};
			  }
			  ///legend colors scale
			  var sequentialScale = d3.scaleOrdinal() // D3 Version 4
										.domain(["D", "R", "I","Industry"])
										.range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);


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
 var candName = $y('#search2').val();
        if (candName === "") {
            candName = "Sean Patrick Maloney (D)";
        }
        dataEndpoint = '/networkdata/' + candName;
        console.log(dataEndpoint);
		d3.json(dataEndpoint, function(error, graph) {
		console.log("searchbox qc " + graph)
		var optArray = [];
		for (var i = 0; i < graph.nodes.length - 1; i++) {
			optArray.push(graph.nodes[i].name);
		}

		optArray = optArray.sort();

		$y(function loadSearch() {
			$y("#search").autocomplete({
				source: optArray
				});
						});

		});//end of preload search box
}) //end of data access




} //end of redraw_post_change}



$y("#button").on("click", function searchNode() {
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
})//end of search node

 	//redraw_post_change;
	 //node scroll filter
	$x(document).ready(function update_slider() {

            $x('#mySlider').slider({
				min: 0,
				max: 25000000,
                values: [200000, 250000],
                range: true,
                create: attachSlider_pre,
                slide: attachSlider_post,
				stop: sliderStop
            })


            function attachSlider_pre() {
				min_node_size = 200000
				max_node_size = 250000
                $x('#lowerlimit').val($x('#mySlider').slider("values", 0));
                $x('#upperlimit').val($x('#mySlider').slider("values", 1));
				redraw_post_change();
            }

			function attachSlider_post() {
                $x('#lowerlimit').val($x('#mySlider').slider("values", 0));
                $x('#upperlimit').val($x('#mySlider').slider("values", 1));
				redraw_post_change(min_node_size,max_node_size);
            }

			function sliderStop() {
					min_node_size = $x('#mySlider').slider("values", 0);
					console.log("lowerLimit " + min_node_size)
					max_node_size = ($x('#mySlider').slider("values", 1));
					console.log("upperLimit " + max_node_size)
					setTimeout(function(){
						attachSlider_post(); //update screen values
					}, 5000);
            }

        });//end of scroll filter



}//end of draw filtered nodes
	
	
	function draw_individual_network(){
	//load the data
		//function find_data(){}

	//remove title stuff
	g.selectAll('.openvis-title')
      .transition()
      .duration(0)
      .attr('opacity', 0);

    g.selectAll('.square')
      .transition()
      .duration(0)
      .attr('opacity', 0);

	  //remove toy network
	  d3.selectAll(".node").remove();
	  d3.selectAll("edge").remove();
	  d3.selectAll('line.edge').remove();

	  //removes example analysis
	d3.selectAll('image').remove();

		var color = d3.scaleOrdinal() // D3 Version 4
		  .domain(["D", "R", "I","Contributor"])
		  .range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);

		var tooltip = d3.select("body")
			.append("div")
			.attr("class", "tooltip")
			.style("opacity", 0);

		const svg = d3.select('svg')
				//width = +svg.attr('width'),
					//height = +svg.attr('height');

		//updated
		//var networkdata = d3.json(data_endpoint)
		//networkdata.then(function( graph) {
		//d3.json("static/data_for_testing/industry_amt_winner_mini.json", function(error, graph) {
        var candName = $y('#search4').val();
        if (candName === "") {
            candName = "Sean Patrick Maloney (D)";
        }
        dataEndpoint = '/networkIndividData/' + candName;
        console.log(dataEndpoint);
		d3.json(dataEndpoint, function(error, graph) {
		  if (error) throw error;


		  const simulation = d3.forceSimulation()
			.nodes(graph.nodes)
			.force('link', d3.forceLink().id(d => d.name))
			.force('charge', d3.forceManyBody().strength(-20))
			.force('center', d3.forceCenter(width / 2, height / 2))
			.on('tick', ticked);

		  simulation.force('link')
			.links(graph.links);

		  let link = svg.selectAll('line')
			.data(graph.links)
			.enter().append('line');

		  link
			.attr('class', 'edge')
			.on('mouseover.tooltip', function(d) {
				tooltip.transition()
					.duration(300)
					.style("opacity", .8);
				tooltip.html("Source:"+ d.source.name+
							 "<p/>Target:" + d.target.name +
							"<p/>Strength:"  + d3.format(",.0f")(d.value ))
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


				  node.append('circle')
					.attr('r', function(d) {return(Math.sqrt(d.contribution_total)/125)}) //used to be R  //and function(d) {console.log(d.target.value)})
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
						tooltip.html("Name:" + d.name + "<p/>Party:" + d.group + "<p/>Total Contributions: " + d3.format(",.0f")(d.contribution_total))
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
							  ///legend colors scale
							  var sequentialScale = d3.scaleOrdinal() // D3 Version 4
														.domain(["D", "R", "I","Industry"])
														.range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);


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
			//d3.json("/networkdata", function(error, graph) {
		//  if (error) throw error;
        var candName = $y('#search3').val();
        if (candName === "") {
            candName = "Sean Patrick Maloney (D)";
        }
        dataEndpoint = '/networkIndividData/' + candName;
        console.log(dataEndpoint);
        graph = d3.json(dataEndpoint, function(error, graph) {
		//console.log(graph)
		var optArray = [];
		for (var i = 0; i < graph.nodes.length - 1; i++) {
			optArray.push(graph.nodes[i].name);
		}

		optArray = optArray.sort();

		$y(function () {
			$y("#search3").autocomplete({
				source: optArray});
						});

		}); //end of find search

graph = d3.json('/networkNodeList', function(error, data) {
		//console.log(graph)
	var optArray = [];
	for (var i = 0; i < data.length; i++) {
		optArray.push( data[i].firstlastp);
	}
		//}

		optArray = optArray.sort();

		$y(function () {
			$y("#search4").autocomplete({
				source: optArray});
						});

		}); //end of find search

})//end of Data ??

$y("#button3").on("click", function searchNode_individ() {
    //find the node
    var selectedVal = document.getElementById('search3').value;
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
})

// $("#button2").on("click", function() { console.log('hey'); })
$y("#button4").on("click", function() { draw_individual_network();});

}//end of draw politican network

	
function draw_committee_network(){
	//load the data
		//function find_data(){}

	//remove title stuff
	g.selectAll('.openvis-title')
      .transition()
      .duration(0)
      .attr('opacity', 0);

    g.selectAll('.square')
      .transition()
      .duration(0)
      .attr('opacity', 0);

	  //remove toy network
	  d3.selectAll(".node").remove();
	  d3.selectAll("edge").remove();
	  d3.selectAll('line.edge').remove();

	  //removes example analysis
	d3.selectAll('image').remove();

		var color = d3.scaleOrdinal() // D3 Version 4
		  .domain(["D", "R", "I","Contributor"])
		  .range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);

		var tooltip = d3.select("body")
			.append("div")
			.attr("class", "tooltip")
			.style("opacity", 0);

		const svg = d3.select('svg')
				//width = +svg.attr('width'),
					//height = +svg.attr('height');

		//updated
		//var networkdata = d3.json(data_endpoint)
		//networkdata.then(function( graph) {
		//d3.json("static/data_for_testing/industry_amt_winner_mini.json", function(error, graph) {
        var candName = $y('#search6').val();
        if (candName === "") {
            candName = "Chris Collins (R)";
        }
        dataEndpoint = '/networkCommitteeData/' + candName;
        console.log(dataEndpoint);
		d3.json(dataEndpoint, function(error, graph) {
		  if (error) throw error;


		  const simulation = d3.forceSimulation()
			.nodes(graph.nodes)
			.force('link', d3.forceLink().id(d => d.name))
			.force('charge', d3.forceManyBody().strength(-20))
			.force('center', d3.forceCenter(width / 2, height / 2))
			.on('tick', ticked);

		  simulation.force('link')
			.links(graph.links);

		  let link = svg.selectAll('line')
			.data(graph.links)
			.enter().append('line');

		  link
			.attr('class', 'edge')
			.on('mouseover.tooltip', function(d) {
				tooltip.transition()
					.duration(300)
					.style("opacity", .8);
				tooltip.html("Source:"+ d.source.name+
							 "<p/>Target:" + d.target.name +
							"<p/>Strength:"  + d3.format(",.0f")(d.value ))
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


				  node.append('circle')
					.attr('r', function(d) {return(Math.sqrt(d.contribution_total)/125)}) //used to be R  //and function(d) {console.log(d.target.value)})
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
						tooltip.html("Name:" + d.name + "<p/>Party:" + d.group + "<p/>Total Contributions: " + d3.format(",.0f")(d.contribution_total))
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
							  ///legend colors scale
							  var sequentialScale = d3.scaleOrdinal() // D3 Version 4
														.domain(["D", "R", "I","Industry"])
														.range(["#0000FF","#FF0000" , "#009933" , "#FF8106"]);


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
			//d3.json("/networkdata", function(error, graph) {
		//  if (error) throw error;
        var candName = $y('#search5').val();
        if (candName === "") {
            candName = "Chris Collins (R)";
        }
        dataEndpoint = '/networkcommitteeData/' + candName;
        console.log(dataEndpoint);
        graph = d3.json(dataEndpoint, function(error, graph) {
		//console.log(graph)
		var optArray = [];
		for (var i = 0; i < graph.nodes.length - 1; i++) {
			optArray.push(graph.nodes[i].name);
		}

		optArray = optArray.sort();

		$y(function () {
			$y("#search5").autocomplete({
				source: optArray});
						});

		}); //end of find search

graph = d3.json('/networkNodeList', function(error, data) {
		//console.log(graph)
	var optArray = [];
	for (var i = 0; i < data.length; i++) {
		optArray.push( data[i].firstlastp);
	}
		//}

		optArray = optArray.sort();

		$y(function () {
			$y("#search6").autocomplete({
				source: optArray});
						});

		}); //end of find search

})//end of Data ??

$y("#button5").on("click", function searchNode_committee() {
    //find the node
    var selectedVal = document.getElementById('search5').value;
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
})

// $("#button2").on("click", function() { console.log('hey'); })
$y("#button6").on("click", function() { draw_committee_network();});

}//end of draw committee network


  /**
   * highlightGrid - show fillers in grid
   *
   * hides: barchart, text and axis
   * shows: square grid and highlighted
   *  filler words. also ensures squares
   *  are moved back to their place in the grid
   */
  function highlightGrid() {}
  function showBar() { }
  function showHistPart() {}
  function showHistAll() { }
  function showCough() { }
  function showAxis(axis) {
    g.select('.x.axis')
      .call(axis)
      .transition().duration(500)
      .style('opacity', 1); }

  function hideAxis() {
    g.select('.x.axis')
      .transition().duration(500)
      .style('opacity', 0); }

  /**
   * UPDATE FUNCTIONS
   *
   * These will be called within a section
   * as the user scrolls through it.
   *
   * We use an immediate transition to
   * update visual elements based on
   * how far the user has scrolled
   *
   */

  /**
   * updateCough - increase/decrease
   * cough text and color
   *
   * @param progress - 0.0 - 1.0 -
   *  how far user has scrolled in section
   */
  function updateCough(progress) {
    g.selectAll('.cough')
      .transition()
      .duration(0)
      .attr('opacity', progress);

    g.selectAll('.hist')
      .transition('cough')
      .duration(0)
      .style('fill', function (d) {
        return (d.x0 >= 14) ? coughColorScale(progress) : '#008080';
      });
  }

  /**
   * DATA FUNCTIONS
   *
   * Used to coerce the data into the
   * formats we need to visualize
   *
   */

  /**
   * getWords - maps raw data to
   * array of data objects. There is
   * one data object for each word in the speach
   * data.
   *
   * This function converts some attributes into
   * numbers and adds attributes used in the visualization
   *
   * @param rawData - data read in from file
   */
  function getWords(rawData) {
    return rawData.map(function (d, i) {
      // is this word a filler word?
      d.filler = (d.filler === '1') ? true : false;
      // time in seconds word was spoken
      d.time = +d.time;
      // time in minutes word was spoken
      d.min = Math.floor(d.time / 60);

      // positioning for square visual
      // stored here to make it easier
      // to keep track of.
      d.col = i % numPerRow;
      d.x = d.col * (squareSize + squarePad);
      d.row = Math.floor(i / numPerRow);
      d.y = d.row * (squareSize + squarePad);
      return d;
    });
  }

  /**
   * getFillerWords - returns array of
   * only filler words
   *
   * @param data - word data from getWords
   */
  function getFillerWords(data) {
    return data.filter(function (d) {return d.filler; });
  }

  /**
   * getHistogram - use d3's histogram layout
   * to generate histogram bins for our word data
   *
   * @param data - word data. we use filler words
   *  from getFillerWords
   */
  function getHistogram(data) {
    // only get words from the first 30 minutes
    var thirtyMins = data.filter(function (d) { return d.min < 30; });
    // bin data into 2 minutes chuncks
    // from 0 - 31 minutes
    // @v4 The d3.histogram() produces a significantly different
    // data structure then the old d3.layout.histogram().
    // Take a look at this block:
    // https://bl.ocks.org/mbostock/3048450
    // to inform how you use it. Its different!
    return d3.histogram()
      .thresholds(xHistScale.ticks(10))
      .value(function (d) { return d.min; })(thirtyMins);
  }

  /**
   * groupByWord - group words together
   * using nest. Used to get counts for
   * barcharts.
   *
   * @param words
   */
  function groupByWord(words) {
    return d3.nest()
      .key(function (d) { return d.word; })
      .rollup(function (v) { return v.length; })
      .entries(words)
      .sort(function (a, b) {return b.value - a.value;});
  }

  /**
   * activate -
   *
   * @param index - index of the activated section
   */
  chart.activate = function (index) {
    activeIndex = index;
    var sign = (activeIndex - lastIndex) < 0 ? -1 : 1;
    var scrolledSections = d3.range(lastIndex + sign, activeIndex + sign, sign);
    scrolledSections.forEach(function (i) {
      activateFunctions[i]();
    });
    lastIndex = activeIndex;
  };

  /**
   * update
   *
   * @param index
   * @param progress
   */
  chart.update = function (index, progress) {
    updateFunctions[index](progress);
  };

  // return chart function
  return chart;
};


/**
 * display - called once data
 * has been loaded.
 * sets up the scroller and
 * displays the visualization.
 *
 * @param data - loaded tsv data
 */
function display(data) {
  // create a new plot and
  // display it
  var plot = scrollVis();
  d3.select('#vis')
    .datum(data)
    .call(plot);

  // setup scroll functionality
  var scroll = scroller()
    .container(d3.select('#graphic'));

  // pass in .step selection as the steps
  scroll(d3.selectAll('.step'));

  // setup event handling
  scroll.on('active', function (index) {
    // highlight current step text
    d3.selectAll('.step')
      .style('opacity', function (d, i) { return i === index ? 1 : 0.1; });

    // activate current section
    plot.activate(index);
  });

  scroll.on('progress', function (index, progress) {
    plot.update(index, progress);
  });
}

// load data and display
d3.tsv('/static/data_for_testing/words.tsv', display);

function searchNodeII() { searchNode;}

/*function searchNode() {
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

}*/
