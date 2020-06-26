
var inputdata = {
    "nodes": [
      {"id": 111,"symbol": "ASS1", "col": "#00548c","frequency": 0.1},
      {"id": 123,"symbol": "ASS1", "col": "#007dd1","frequency": 0.2},
      {"id": 234, "symbol": "ASS1", "col": "#007dd1","frequency": 0.3},
      {"id": 7856,"symbol": "ASS1", "col": "#007dd1","frequency": 0.4},
      {"id": 5,"symbol": "ASS1", "col": "#007dd1","frequency": 0.5},
      {"id": 678,"symbol": "ASS1", "col": "#007dd1","frequency": 0.6},
      {"id": 36, "symbol": "ASS1", "col": "#007dd1","frequency": 0.7},
      {"id": 88, "symbol": "ASS1", "col": "#007dd1","frequency": 0.8},
      {"id": 678, "symbol": "ASS1", "col": "#007dd1","frequency": 0.9},
      {"id": 666, "symbol": "ASS1", "col": "#007dd1","frequency": 0.95},
      {"id": 656, "symbol": "ASS1", "col": "#007dd1","frequency": 0.99}
    ],
    "links": [
      {"source": 656, "target": 111, "value": 4},
      {"source": 656, "target":123, "value": 6},
      {"source": 656, "target": 5, "value": 2},
      {"source": 656, "target":7856, "value": 1},
      {"source": 36, "target":7856, "value": 1},
      {"source": 88, "target":7856, "value": 1},
      {"source": 656, "target": 666, "value": 99}
    ]
  };
  


 // needs some zoom
// https://stackoverflow.com/questions/16236600/d3-js-force-layout-auto-zoom-scale-after-loading
    
function drawit(data) {
     // if (error) throw error;
    d3.selectAll("#forceLayout > *").remove();

     var svg = d3.select("#forceLayout"),
     width = +svg.attr("width"),
     height = +svg.attr("height");
    
    var color = d3.scaleOrdinal(d3.schemeCategory20);
    
    var simulation = d3.forceSimulation()
        
        .force("link", d3.forceLink().id(function(d) { return d.id; }))
        .force("charge", d3.forceManyBody().strength(-10.5))
        //.force("size",[width, height])
        .force("center", d3.forceCenter(width / 2, height / 2));


    var link = svg.append("g")
          .attr("class", "links")
        .selectAll("line")
        .data(data.links)
        .enter().append("line")
          .attr("stroke-width", function(d) { return Math.sqrt(d.value) + 2; });
    
    var node = svg.append("g")
          .attr("class", "nodes")
        .selectAll("circle")
        .data(data.nodes)
        .enter().append("circle")
        // .attr("r", function(d) { return d.frequency * data.numSeeds * 10 + 2; })
          .attr("r",5)
        .attr("fill", function(d) {
            if (d.group == 0) {
              return "#fcba03";
            } else if (d.group == 1) {
              return "#00548c";  //#00548c"
            } else if (d.group == 2) {
              return "#fc5a03";  //#00548c"
            } else {
            return "#003047";
            }
          })
         // .attr("fill", function(d) { return "#007dd1"; })
          .call(d3.drag()
              .on("start", dragstarted)
              .on("drag", dragged)
              .on("end", dragended));
    
      node.append("title")
        .style("text-anchor", "middle")
        .style("fill", "white")
        .attr("dy", "1.3em")
        .text(function(d) { return d.label; });
    
      simulation
          .nodes(data.nodes)
          .on("tick", ticked);
    
      simulation.force("link")
          .links(data.links);
    
                      function ticked() {
                        

                      
                        link
                            .attr("x1", function(d) { return d.source.x; })
                            .attr("y1", function(d) { return d.source.y; })
                            .attr("x2", function(d) { return d.target.x; })
                            .attr("y2", function(d) { return d.target.y; });
                    
                        node
                            .attr("cx", function(d) { return d.x; })
                            .attr("cy", function(d) { return d.y; });
                      }
      
      logger("drawit ran");
      
          function dragstarted(d) {
          if (!d3.event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
          logger( d.id);
          $("#graphDisplay").text(d.symbol);
        }
        
        function dragged(d) {
          d.fx = d3.event.x;
          d.fy = d3.event.y;
        }
        
        function dragended(d) {
          if (!d3.event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }
     

     
    };
  
    function reloadForceLayout (data){
        drawit(data);
    }  
    
    function clearForceLayout (data){
        d3.selectAll("svg > *").remove();
    }  
