var formatName = function(d) {
    d.cand_name = d.cand_name.toLowerCase();
    lastfirst = d.cand_name.split(",");
    lastname = lastfirst[0].toLowerCase();
    lastname = lastname.charAt(0).toUpperCase() + lastname.slice(1);
    var firstmiddle = "";
    if (lastfirst.length > 1) {
        firstmiddle = lastfirst[1].toLowerCase();
        firstmiddle = firstmiddle.replace(/(^\w|\"\w|\s\w)/g, function(word) {
            return word.toUpperCase();
        });
    }

    var raceType = d.cand_id.charAt(0);
    var str = "";
    switch(raceType) {
        case "P":
            str = firstmiddle + " " + lastname + " - Presidency - " + d.cand_id;
            break;
        case "H":
            str = firstmiddle + " " + lastname + " - House - " + d.cand_id;
            break;
        case "S":
            str = firstmiddle + " " + lastname + " - Senate - " + d.cand_id;
            break;
        default:
            str = firstmiddle + " " + lastname;
            break;
    }
    return str;

}

document.addEventListener('DOMContentLoaded', function() {
    var all_cands = d3.json("/api/candidates");
    all_cands.then(function(data) {
        var formatted = data.map(d => formatName(d));
        var cData = {}
        formatted.forEach(d => cData[d] = null  );
        var elems = document.querySelectorAll('.autocomplete');
        M.Autocomplete.init(elems, {data:cData, limit: 10, onAutocomplete: function(choice) {
            var cand_id = choice.split("-")[2].trim();
            window.location.href = "/candview?id=" + cand_id;
        }});
    });
});

// d3.select("#search").on("click", function(d){
//     d3.select(this).attr("value", "")
// });
// 
// d3.select("#search").on('keyup', function(d) {
//     var string = document.getElementById("search").value
//     if (string == "") {
//         d3.select("#searchbox").selectAll("a").remove();
//     } else if (string.length < 2){
//         return
//     }  
//     var possibilites = d3.json("/candidates?lookup=" + string);
//     possibilites.then(function(d) { 
//         console.log(d);
//         d.map(function(d) {
//             d.name = d.name.toLowerCase();
//             lastfirst = d.name.split(",");
//             lastname = lastfirst[0].toLowerCase();
//             lastname = lastname.charAt(0).toUpperCase() + lastname.slice(1);
//             var firstmiddle = "";
//             if (lastfirst.length > 1) {
//                 firstmiddle = lastfirst[1].toLowerCase();
//                 firstmiddle = firstmiddle.replace(/(^\w|\"\w|\s\w)/g, function(word) {
//                     return word.toUpperCase();
//                 });
//             }
//             raceType = d.id.charAt(0);
//             console.log(raceType)
//             switch(raceType) {
//                 case "P":
//                     d.name = firstmiddle + " " + lastname + " (Pres. Candidate)";
//                     break;
//                 case "H":
//                     d.name = firstmiddle + " " + lastname + " (House Candidate)";
//                     break;
//                 case "S":
//                     d.name = firstmiddle + " " + lastname + " (Senate Candidate)";
//                     break;
//                 default:
//                     d.name = firstmiddle + " " + lastname;
//                     break;
//             }
// 
//         });
// 
//         d3.select("#dropdown").remove();
//         var links = d3.select("#searchbox")
//             .append("select")
//             .attr("id", "dropdown")
//             .attr("autofocus", "true")
//             //.attr("class", "w3-bar-block w3-border")
//             .attr("style", "width:300px");
// 
//         links.selectAll("option")
//             .data(d)
//             //.attr("href", d => "/candview?id=" + d.id)
//             .attr("value", d => d.id)
//             //.attr("class", "w3-bar-item w3-button")
//             .text(d => d.name)
//             .enter()
//             .append("option")
//             .attr("value", d =>  d.id)
//             //.attr("href", d => "/candview?id=" + d.id)
//             //.attr("class", "w3-bar-item w3-button")
//             .text(d => d.name)
//             .exit().remove();
//             
//         //console.log(d);
//     });
// 
//     //jif (this.value.length > 1) {
//     //j    var xhttp = new XMLHttpRequest();
//     //j    xhttp.onreadystatechange = function() {
//     //j        if (this.readState == 4 && this.status == 200) {
//     //j            dropdown(this);
// 
//     //j        }
//     //j    }
//     //j}
// });

