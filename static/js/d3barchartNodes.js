

// needs some zoom
// https://stackoverflow.com/questions/16236600/d3-js-force-layout-auto-zoom-scale-after-loading

function clearNodeBarChart() {
    d3.selectAll("#NodeBarChart > *").remove();

}

function drawNodeBarChart(input) {
    // if (error) throw error;
    d3.selectAll("#NodeBarChart > *").remove();

    var data = input;

    // set the dimensions and margins of the graph
    var margin = {
        top: 50,
        right: 50,
        bottom: 50,
        left: 50
    },
    width = 512 - margin.left - margin.right,
    height = 512 - margin.top - margin.bottom;

    // set the ranges
    var y = d3.scaleBand()
        .range([0, height])
        .padding(0.1);

    var x = d3.scaleLinear()
        .range([0, width]);

    // append the svg object to the body of the page
    // append a 'r' element to 'svg'
    // moves the 'r' element to the top left margin
    var svg = d3.select("#NodeBarChart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "rotate(-90,200,200)");

    // Scale the range of the data in the domains
    x.domain([0, d3.max(data, function (d) {
                return d.value * 2;
            })])
    y.domain(data.map(function (d) {
            return d.symbol;
        }));
    //y.domain([0, d3.max(data, function(d) { return d.value; })]);

    // append the rectangles for the bar chart
    svg.selectAll(".bar")
    .data(data)
    .enter().append("rect")
    .attr("class", "bar")

    //.attr("x", function(d) { return x(d.value); })
    .attr("width", function (d) {
        return x(d.value + 0.0001);
    })
    //.attr("y", function(d) { return y(d.symbol); })
    .attr("y", function (d) {
        return y(d.symbol);
    })
    .attr("height", y.bandwidth())
    .attr("fill", function (d) {

        if (d.value == 0.00) {
            return "#616161";
        } else if (d.group == 0) {
            return "#fcba03";
        } else if (d.group == 1) {
            return "#00548c"; //#00548c"
        } else if (d.group == 2) {
            return "#fc5a03"; //#00548c"
        } else {
            return "#003047";
        }
    })
    .on("mousemove", function (d) {
        //console.log(d.symbol);
        $("#itisbox").text(d.symbol);

    })
    .on("click", function (d) {
        //console.log(d.symbol);

        //$("#itisbox").text(d.symbol);

    });

    // /*   // add the x Axis
    svg.append("g")
    .attr("transform", "translate(0," + height + ")")

    .style("stroke", "white")
    .call(d3.axisBottom(x))
    .selectAll("text")
    .attr("y", 0)
    .attr("x", 9)
    .attr("dy", ".35em")
    .attr("transform", "rotate(90)")
    .style("text-anchor", "start")
    .style("fill", "white");

    // add the y Axis
    svg.append("g")
    .call(d3.axisLeft(y))
    .selectAll("text")
    .attr("y", 10)
    .attr("x", 5)
    .attr("dy", ".15em")
    .attr("transform", "rotate(125)")
    .style("text-anchor", "start")
    .style("font-size", 6)
    .style("fill", "white");

    // .append("text")
    // .attr("class","label")
    // .attr("x", (function(d) { return x(d.symbol); }  ))
    // .attr("y", function(d) { return y(d.value) - 20; })
    // .attr("dy", ".75em")
    // .text(function(d) { return d.value; });

};