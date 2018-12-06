var lib = lib || {};

lib.waterfallModule = function() {
    var contentDiv = document.getElementById("waterfall-content")
    var width = contentDiv.clientWidth;
    var height = 1000;
    var margin = {top: 20, right: 30, bottom: 30, left: 40}, 
        width = width - margin.left - margin.right, 
        height = 500 - margin.top - margin.bottom,
        padding = 0.3;
    var data = [];
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    const politicolor = d3.scaleSequential(d3.interpolateRdBu);
    var svg = d3.select("#chart1");
    let links = svg.append("g");
    var nodes = svg.append("g");
    var titles  = svg.append("g")
    window.addEventListener("resize", plot_)

    function data_(_) {
        var that = this;
        if (!arguments.length) return data;
        data = _;
        return that;
    }

    function plot_() {

        var x = d3.scaleBand()
            .range([0, width])
            .round([padding]);

        var y = d3.scaleLinear()
            .range([height, 0]);

        var xAxis = d3.axisBottom(x);

        var yAxis = d3.axisLeft(y);

        var chart = d3.select("#waterfall")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        // Transform data (i.e., finding cumulative values and total) for easier charting
        var cumulative = 0;
        console.log(data)
        for (var i = 0; i < data.length; i++) {
            data[i].start = cumulative;
            cumulative += data[i].amt;
            data[i].end = cumulative;
            data[i].class = ( data[i].amt >= 0 ) ? 'positive' : 'negative'
        }
        data.push({
        group: 'Total',
        end: cumulative,
        start: 0,
        class: 'total'
        });

        x.domain(data.map(function(d) { return d.group; }));
        y.domain([0, d3.max(data, function(d) { return d.amt; })]);

        chart.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

        chart.append("g")
          .attr("class", "y axis")
          .call(yAxis);

        var bar = chart.selectAll(".bar")
          .data(data)
        .enter().append("g")
          .attr("class", function(d) { return "bar " + d.class })
          .attr("transform", function(d) { return "translate(" + x(d.group) + ",0)"; });

        bar.append("rect")
          .attr("y", function(d) { return y( Math.max(d.start, d.end) ); })
          .attr("height", function(d) { return Math.abs( y(d.start) - y(d.end) ); })
          .attr("width", x.bandwidth());

        bar.append("text")
          .attr("x", x.bandwidth() / 2)
          .attr("y", function(d) { return y(d.end) + 5; })
          .attr("dy", function(d) { return ((d.class=='negative') ? '-' : '') + ".75em" });
          //.text(function(d) { return dollarFormatter(d.end - d.start);});

        bar.filter(function(d) { return d.class != "total" }).append("line")
          .attr("class", "connector")
          .attr("x1", x.bandwidth() + 5 )
          .attr("y1", function(d) { return y(d.end) } )
          .attr("x2", x.bandwidth() / ( 1 - padding) - 5 )
          .attr("y2", function(d) { return y(d.end) } );
    }

    return {
        "data": data_,
        "plot": plot_
    };
};


var waterfallData = d3.json(wf_endpoint)
waterfallData.then(function(d){
    var waterfall = lib.waterfallModule();
    waterfall.data(d)
    waterfall.plot();
});
