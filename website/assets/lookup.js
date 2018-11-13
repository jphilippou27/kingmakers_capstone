d3.select("#search").on('keyup', function(d) {
    var string = document.getElementById("search").value
    var possibilites = d3.json("/candidates?lookup=" + string);
    possibilites.then(function(d) { 
        console.log(d);
        d3.select("#dropdown").remove();
        var links = d3.select("#searchbox")
            .append("div")
            .attr("id", "dropdown")
            .attr("class", "w3-bar-block w3-border")
            .attr("style", "width:300px");


        links.selectAll("a")
            .data(d)
            .attr("href", d => "/candview?id=" + d.id)
            .attr("class", "w3-bar-item w3-button")
            .text(d => d.name)
            .enter()
            .append("a")
            .attr("href", d => "/candview?id=" + d.id)
            .attr("class", "w3-bar-item w3-button")
            .text(d => d.name)
            .exit().remove()
            
        //console.log(d);
    });

    //jif (this.value.length > 1) {
    //j    var xhttp = new XMLHttpRequest();
    //j    xhttp.onreadystatechange = function() {
    //j        if (this.readState == 4 && this.status == 200) {
    //j            dropdown(this);

    //j        }
    //j    }
    //j}
});

