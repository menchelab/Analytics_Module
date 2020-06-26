

 // needs some zoom
// https://stackoverflow.com/questions/16236600/d3-js-force-layout-auto-zoom-scale-after-loading

function clearNodeBarChart(){
  d3.selectAll("#NodeBarChart > *").remove();  
    
}
    
function drawNodeBarChart(input) {
     // if (error) throw error;
d3.selectAll("#NodeBarChart > *").remove();
     
     
     
/*      var svg111 = d3.select("#NodeBarChart"),
     width = +svg111.attr("width"),
     height = +svg111.attr("height"); */
//logger(input);    
var data = input;
//console.log(data);
//var data = [{"id":"Bob","r":33},{"id":"Robin","r":12},{"id":"Anne","r":41},{"id":"Mark","r":16},{"id":"Joe","r":59},{"id":"Eve","r":38},{"id":"Karen","r":21},{"id":"Kirsty","r":25},{"id":"Chris","r":30},{"id":"Lisa","r":47},{"id":"Tom","r":5},{"id":"Stacy","r":20},{"id":"Charles","r":13},{"id":"Mary","r":29}];

// set the dimensions and margins of the graph
var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

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
    .attr("transform", 
          "translate(" + margin.left + "," + margin.top + ")");
//var tooltip = svg.append("div").attr("class", "toolTip");
  // format the data
 /*  data.forEach(function(d) {
    d.frequency = +d.frequency;
  }); */

  // Scale the range of the data in the domains
  x.domain([0, d3.max(data, function(d){ return d.frequency *2; })])
  y.domain(data.map(function(d) { return d.symbol; }));
  //y.domain([0, d3.max(data, function(d) { return d.frequency; })]);

  // append the rectangles for the bar chart
  svg.selectAll(".bar")
      .data(data)
      .enter().append("rect")
      .attr("class", "bar")
      
      //.attr("x", function(d) { return x(d.frequency); })
      .attr("width", function(d) {return x(d.frequency + 0.0001); } )
      //.attr("y", function(d) { return y(d.symbol); })
      .attr("y", function(d) { return y(d.symbol); })
      .attr("height", y.bandwidth())
      .attr("fill", function(d) {
          
            if (d.frequency == 0.00) { 
              return "#616161";
            } else if (d.group == 0) {
              return "#fcba03";
            } else if (d.group == 1) {
              return "#00548c";  //#00548c"
            } else if (d.group == 2) {
              return "#fc5a03";  //#00548c"
            } else {
            return "#003047";
            }
      })
        .on("mousemove", function(d){
            
            //console.log(d.symbol);
            $("#NodeBarChartdisplay").text(d.symbol);
            
/*             tooltip
              .style("left", d3.event.pageX - 50 + "px")
              .style("top", d3.event.pageY - 70 + "px")
              .style("display", "inline-block")*/
              
        })
        .on("click", function(d){
              console.log(d.symbol);
        });
    	//.on("mouseout", function(d){ tooltip.style("display", "none");});
// /*   // add the x Axis
  svg.append("g")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x))
      .selectAll("text")
      .attr("y", 0)
      .attr("x", 9)
      .attr("dy", ".35em")
      .attr("transform", "rotate(90)")
      .style("text-anchor", "start");

  // add the y Axis
  svg.append("g")
      .call(d3.axisLeft(y))
      .selectAll("text")
    .attr("y", 0)
    .attr("x", 9)
    .attr("dy", ".35em")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end")
    .style("fill", "red"); 
      

  // .append("text")
  // .attr("class","label")
  // .attr("x", (function(d) { return x(d.symbol); }  ))
  // .attr("y", function(d) { return y(d.frequency) - 20; })
  // .attr("dy", ".75em")
  // .text(function(d) { return d.value; });   

    };
  

