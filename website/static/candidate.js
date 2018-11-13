
var lib = lib || {};

lib.barChartModule = function() {
    var data = [];
    var height = 250;
    var contentDiv = document.getElementById("content")
    var width = contentDiv.clientWidth;
    var data = [];
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    const politicolor = d3.scaleSequential(d3.interpolateRdBu);

    function data_(_) {
        var that = this;
        if (!arguments.length) return data;
        data = _;
        console.log(data.length)
        data = data.filter(function(d) {
            return d.date > "2017-01";
        });
        console.log(data.length)
        return that;
    }

    function plot_net_horizontal(name, chart, accessor_x, accessor_y, color) {
        var svg = d3.select(chart)
            .attr("height", height)
            .attr("width", width);

        var margin = {top: 30, right: 20, bottom: 40, left: 120};

        var barchartwidth = +svg.attr("width") - margin.left - margin.right,
            barchartheight = +svg.attr("height") - margin.top - margin.bottom;

        var g = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var y = d3.scaleLinear().range([barchartheight, 0]),
            x = d3.scaleBand().rangeRound([barchartwidth, 0]).padding(0.1);

        // must be linear
        y.domain(d3.extent(data, accessor_y));

        // must be categorical
        //x.domain(data.map(accessor_x));
        x.domain(['2018-09', '2018-08', '2018-07', '2018-06', '2018-05', '2018-04', '2018-03', '2018-02', '2018-01','2017-12', '2017-11', '2017-10',  '2017-09', '2017-08', '2017-07', '2017-06', '2017-05', '2017-04', '2017-03', '2017-02', '2017-01']);

        //g.select(".title").remove();
        //g.append("text")
        //  .attr("class", "title")
        //  .attr("font-size", "20")
        //  .attr("x", 150)
        //  .attr("y", 50)
        //  .text(name);

        g.selectAll("g.axis").remove();
        g.attr("transform", "translate(75,10)");

        g.append("g")
            .attr("class", "axis axisx")
            .attr("transform", "translate(0," + (barchartheight + 10) + ")")
            .call(d3.axisBottom(x))
            .selectAll("text")
            .attr("y", 0)
            .attr("x", 9)
            .attr("dy", ".35em")
            .attr("transform", "rotate(90)")
            .style("text-anchor", "start");

        g.append("g")
            .attr("class", "axis axisy")
            .call(d3.axisLeft(y).ticks(10));

        var bars = g.selectAll("rect")
          .data(data);

        bars.transition().duration(300)
          .attr("id", accessor_x)
          .attr("datum", accessor_y)
          .attr("x", function(d) { return x(accessor_x(d)); })
          .attr("y", function(d) {return y(Math.max(0, accessor_y(d))); })
          .attr("width", x.bandwidth())
          .attr("height", function(d) { return Math.abs(y(accessor_y(d)) - y(0)); });


        bars.enter().append("rect")
            .attr("class", "bar")
            .attr("datum", accessor_y)
            .attr("id", function(d) {return accessor_x(d); })
            .attr("x", function(d) { return x(accessor_x(d)); })
            .attr("y", function(d) { return y(Math.max(0, accessor_y(d))); })
            .attr("width", x.bandwidth())
            .attr("height", function(d) { return Math.abs(y(accessor_y(d)) - y(0)); })
            .attr("fill", color);

        bars.exit().transition().duration(300).remove();
        //g.select(".axisx").selectAll("g").attr("transform", function(d) {
          //return this.getAttribute("transform") + " rotate(90)";
        //g.selectAll(".tick").attr("transform", "translate(0, 5)"
        //});

    }
    return {
        "data": data_,
        "plot_net_horizontal": plot_net_horizontal,
    };
};


var candfor = d3.json("/candidates/" + cand_id + "/ts/for");
candfor.then(function(d){
    console.log(d);
    var bars = lib.barChartModule();
    bars.data(d);
    bars.plot_net_horizontal("spending for cand", "#timeseries_for", d => d.date, d => d.total, "#062F4F");
    //sankey.industry_data(clean_data)
    //sankey.plot_by_industry()
});
var candagainst = d3.json("/candidates/" + cand_id + "/ts/against");
candagainst.then(function(d){
    console.log(d);
    var bars = lib.barChartModule();
    bars.data(d);
    bars.plot_net_horizontal("spending against cand", "#timeseries_against", d => d.date, d => d.total, "#B82601");
    //sankey.industry_data(clean_data)
    //sankey.plot_by_industry()
});
