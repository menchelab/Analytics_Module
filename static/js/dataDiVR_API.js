///////GLOBAL VARS vvvvvvv
var dbprefix = ""
//var dbprefix = ' http://127.0.0.1:1337';
//create the global ue4(...) helper function
"object"!=typeof ue||"object"!=typeof ue.interface?("object"!=typeof ue&&(ue={}),ue.interface={},ue.interface.broadcast=function(e,t){if("string"==typeof e){var o=[e,""];void 0!==t&&(o[1]=t);var n=encodeURIComponent(JSON.stringify(o));"object"==typeof history&&"function"==typeof history.pushState?(history.pushState({},"","#"+n),history.pushState({},"","#"+encodeURIComponent("[]"))):(document.location.hash=n,document.location.hash=encodeURIComponent("[]"))}}):function(e){ue.interface={},ue.interface.broadcast=function(t,o){"string"==typeof t&&(void 0!==o?e.broadcast(t,JSON.stringify(o)):e.broadcast(t,""))}}(ue.interface),(ue4=ue.interface.broadcast);
////  API DEFENITION
//// DONT TOUCH THIS FILE
function logger(message){
    console.log(message);
    ue4("log",message);
}

var CCResponse = ""



//// FUNCTIONS CALLED BY UE4

ue.interface.setPayload = function(payload)
{
    input = JSON.parse(payload);
    console.log("setPayload says:");
    console.log(input);

};

ue.interface.getSelection = function(data)
{
    //console.log(data);
   // i
    //dummydata = '{"node_ids":[12149,108],"selection_name":"somAARGrgARGagname"}';
    //input = JSON.parse(data);
    //console.log(input);
    SaveSelectionDB(data);
};

ue.interface.getRandomWalkResult = function(data)
{
    input = JSON.parse(data);
    console.log("getSelection triggered");
    console.log(input);
    reloadForceLayout (input);
};

// call a function named route + "Trigger" defined below for each input field
ue.interface.VRkeyboard = function(payload)
{
    input = JSON.parse(payload);
// Call function dynamically
    var fnName = input.route + "Trigger";;
    window[fnName](input);
    console.log("VRKeyboard triggered:"+ fnName);
};

// TEXT INPUT FIELDS
function searchInput1Trigger(data){
    //console.log(data);
    // SET BUTTON TEXT
    console.log("Yep, definitely running!");
    var element = "#" + data.route;
    $(element).html(data.content);
    //console.log(data.content);
    GetDbSearchTerms(data.content,$('#searchAttribute1').val());

/*     if (data.end == 1){
        console.log(data.route + " Event Fired");
    } */
}

function SaveSearchTrigger(data){
    console.log(data);
    // SET BUTTON TEXT
    //var element = "#" + data.route;
    //$(element).html(data.content);

    if (data.end == 1){
        ue4("getSelection", data.content);
        console.log(data.route + " Event Fired");
    }
}

function saveSelTrigger(data){
/*     console.log(data);
    var element = "#" + data.route;
    $(element).html(data.content); */


    if (data.end == 1){  //USER PRESST ENTER KEY
        // Get Selection from UE4 somehow
        ue4("getSelection", data.content);
        //var dummySelData =  {"selection_name": data.content,"node_ids":[1,2,3,4,5,99,666,1337]};
        console.log(data.route + " Event Fired");
    }
}





ue.interface.setFilenames = function(payload)
{
    input = JSON.parse(payload);
    //console.log("setFilenames says:");
    //console.log(input.nodes[1]);

        // POPULATE UI DROPDOWN
             input.nodes.forEach(function(item)
            {
                  $('#selections').append($('<option>', {
                  value: 1,
                  text: item}));
            });

};

var dbdata;
var thisNamespace;

//// Functions that POST to UE4 //////

function ActivateVRkeyboard(route){
    ue4("VRkeyboard", route);
    console.log("vrkeyboard");
}

////put functions that POST to Flask HERE vvv
function UpdateNamespace(name) {

    thisNamespace = dbdata.find(o => o.namespace === name);
    console.log(thisNamespace);

    GetDbSelections(); //LOAD SELECTION FILES FOR PROJECT
}

function GetDbFileNames1() {

    //var requestTxt = {"name": name};
    //payload = JSON.stringify(requestTxt)
    path = dbprefix + '/api/namespace/summary' ;
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        //data: payload,
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {
            //console.log(response);
        // POPULATE UI DROPDOWN
            dbdata = response.slice(); //DEEP COPY !!!!
            //console.log(dbdata)

            response[0].layouts.forEach(function(item)
            {
                 $('#layouts').append($('<option>', {value: item,text: item}));
            });

            $('#layouts').val(response[0].layouts[0]);   //SET ACTIVE SLOT
            $("#layouts").selectmenu("refresh");                          //AND SHOW


            response.forEach(function(item)
            {
                 $('#namespaces').append($('<option>', {value:  item.namespace, text:  item.namespace}));
            });

            $('#namespaces').val('ppi');
            $("#namespaces").selectmenu("refresh");
            UpdateNamespace('ppi');

        },

        error: function(err) {
        console.log(err);

        }
    });
//event.preventDefault();

}


function GetDbNodeList1(name) {

    path = dbprefix + "/api/" + thisNamespace.namespace + "/layout/"  + name;
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {
            ue4("LoadDbNodeList", response);
            //console.log(response.["a"]);
            GetDbLabelList1(name);

/*             response.forEach(function(item)
            {

                 console.log(item["a"][0])
            }); */
        },

        error: function(err) {
        console.log(err);

        }
    });
//event.preventDefault();

}



function GetDbLinkList1() {

    path = dbprefix + "/api/"+ thisNamespace.namespace + "/edge";
        $.ajax({
            type: "GET",
            url: path,
            contentType: "application/json",

            headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
            dataType: "json",
                success: function(response) {
                    ue4("LoadDbLinkList", response);
                    console.log("linklist loaded" + path);
            },
        error: function(err) {
        console.log(err);
        }
    });
}




function GetDbLabelList1(name) {


    path = dbprefix + "/api/" + thisNamespace.namespace + "/label/" + name;
        $.ajax({
            type: "GET",
            url: path,
            contentType: "application/json",
            headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
            dataType: "json",
                success: function(response) {
                    ue4("LoadDbLabelList", response);
                    //console.log(response);
            },
        error: function(err) {
        console.log(err);
        }
    });
}


function setActiveSearchRow(row_num) {
  console.log("setting");
  if($("#search_bar").attr("active_row") != row_num) {
    $("#search_bar").attr("active_row", row_num)
    clearButtons("autocomp");
    clearButtons("taxonomy_bar");
    $('#search_txt').val("")
  }
}



////Search and auto complete dynamic button factory
function GetDbSearchTerms(name, namespace, search_attr_id) {
  console.log("running");
  // var search_attr_id = 1;


    path = dbprefix + "/api/ppi/attribute/?prefix="+ name + "&namespace="+ namespace;
    //console.log(path);
    if (name.length > 1){
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {

          //clearButtons("autocomp");

            response.forEach(function(item)
            {
                createButton(item.name,item.id,$("#autocomp"), search_attr_id);
            });

        console.log(response);
        },

        error: function(err) {
        console.log(err);

        }
    });
//event.preventDefault();
    }

}


function createButton(Bname,Bid,Parent, search_attr_id) {

    var r=$('<input/>').attr({
        type: "button",
        id: Bid,
        value: Bname

    });
    Parent.append(r);
    $(r).button();
    $(r).click(function() {
        $("#searchInput" + search_attr_id).text(Bname);
        $("#searchInput" + search_attr_id).attr("searchID",Bid);
    });
}

function createDropdownButton(Bname,Bid,Parent, depth, children, search_attr_id) {

    var r=$('<input/>').attr({
        type: "button",
        id: Bid,
        value: "\u25BC " + Bname

    });
    Parent.append(r);
    $(r).button();
    $(r).click(function() {
        $("#searchInput" + search_attr_id).text(Bname);
        $("#searchInput" + search_attr_id).attr("searchID",Bid);
      console.log(search_attr_id);
        AddChildren(children, depth, search_attr_id);
    });
}

function createNodeButton(Bname,Bsym,Bid,Parent) {
 //for resultList

    var r=$('<input/>').attr({
        type: "button",
        id: Bid,
        value:Bsym + " - " + Bname

    });
    var p = '#' + Parent;
    $(p).append(r);
    $(r).button();
    $(r).click(function() {
       // $("#searchInput1").text(Bname);
      //  $("#searchInput1").attr("searchID",Bid);
        console.log(Bname + " " + Bid + " " + Parent);
      path = dbprefix + "/api/"+ thisNamespace.namespace + "/attribute?node_id=" + Bid ;
      $.ajax({
          type: "GET",
          url: path,
          contentType: "application/json",
          //data: payload,
          dataType: "json",
        success: function(response) {
          for (var i = 0; i < 100 && i < response.length ; i++) {

            createAttributeButton(response[i].name,response[i].id,"tab_info");

          }
          $('#tabs').tabs( "option", "active", 5 );

        }
      });
  }
    )};

function createAttributeButton(name, id, Parent) {
 //for resultList

    var r=$('<input/>').attr({
        type: "button",
        id: id,
        value: name

    });
    var p = '#' + Parent;
    $(p).append(r);
    $(r).button();
    $(r).click(function() {
       // $("#searchInput1").text(Bname);
      //  $("#searchInput1").attr("searchID",Bid);
        console.log(name + " " + id + " " + Parent);

  }
    )};


function clearButtons(parent){
  const myNode = document.getElementById(parent);
  while (myNode.firstChild) {
    myNode.removeChild(myNode.firstChild);
  }
}

function GetDbSelections() {

    path = dbprefix + "/api/"+ thisNamespace.namespace + "/attribute/?namespace=SELECTION" ;
    console.log(path)
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {



            response.forEach(function(item)
            {

                 $('#selections').append($('<option>', {value: item.id, text: item.name}));
            });
            $('#selections').val( response[0].namespace);
            $("#selections").selectmenu("refresh");
        console.log(response);
        },

        error: function(err) {
        console.log(err);

        }
    });
//event.preventDefault();

}

function SimpleSearch(id) {
    
    var input_string = ""
    for (var i = 1; i <=4; i++) {
      if ($("#searchInput" + i).text() != "INPUT" + i) {
        console.log("INPUT" + i);
        console.log($("#searchInput" + i).text());
        console.log($("#searchInput" + i).text() == "INPUT" + i);
        input_string = input_string.concat(
          "predicate", (i-1), "=",
          $("#searchPredicate" + i).val(),
          "&subject", i-1, "=attribute&object", i-1, "=",
          $("#searchInput" + i).attr("searchID"), "&"
        )
      }
    }
    path = dbprefix + "/api/"+ thisNamespace.namespace + "/node/search?" + input_string
  console.log(path);
        $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {

            response.mode = $('#searchMode1').val();
            console.log(response);
            document.getElementById("sResults").innerHTML = "FOUND " + response.nodes.length + " NODES FOR " + $('#searchInput1').text();
            ue4("LoadSelectionDB", response);

            document.getElementById("ResultsLabel").innerHTML = "FOUND " + response.nodes.length + " NODES FOR " + $('#searchInput1').text();
            clearButtons("ResultList");

/*             response.nodes.forEach(function(item)
            {

            }); */

            for (var i = 0; i < 100 && i < response.nodes.length ; i++) {

                createNodeButton(response.nodes[i].name,response.nodes[i].symbol,response.nodes[i].node_id,"ResultList");

            }
            // Open the results tab, which is 4 when 0-indexed.
            $('#tabs').tabs( "option", "active", 3 );


        },

        error: function(err) {
        console.log(err);

        }
    });
//event.preventDefault();

}

function AddChild(parent, child, depth, search_attr_id) {
  if(child.childnodes.length == 0) {
    createButton(child.name, child.id, parent, search_attr_id);
    $('#' +child.id).attr("depth", depth)
  } else {  //(child.childnodes.length >= 1){
    createDropdownButton(child.name, child.id, parent, depth, child.childnodes, search_attr_id);
  }
    if (depth%2 == 0) {$('#'+child.id).css("background-color", "#3e67ff")}

}

function AddChildren(children, depth, search_attr_id) {
  if (typeof depth == typeof undefined) {
    console.log("undefined depth of children")
  }
  depth = depth || 1
  $("#taxonomy_bar").children().each(function(i) {
    var child = $(this)
    var attr = $(this).attr('depth')
    if (typeof attr !== typeof undefined && attr !== false && attr > depth) {
       child.remove();
    };
  });
  new_bar = $('<p>');
  new_bar.addClass('taxo_display');
  new_bar.attr("depth", depth + 1)
  $("#taxonomy_bar").append(new_bar);
  children.forEach(function(child) {
    AddChild(new_bar, child, depth + 1, search_attr_id)});
}

function GetAttributeTaxonomy(name, search_attr_id) {
  $(".taxo_display").remove();

    path = dbprefix + "/api/"+ "ppi" + "/attribute_taxonomy?namespace=" + name ;
    var ajaxTime= new Date().getTime();
    console.log(path)
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        dataType: "json",
        success: function(response) {
          var totalTime = new Date().getTime()-ajaxTime;
          console.log("total time" , totalTime)

          new_bar = $('<p>');
          new_bar.addClass('taxo_display');
          $("#taxonomy_bar").append(new_bar)
          if (typeof response.childnodes !== typeof undefined) {
            response.childnodes.forEach(function(item) {
              AddChild(new_bar, item, 1, search_attr_id);
            });
            totalTime = new Date().getTime()-ajaxTime;
              console.log("total time" , totalTime)
          }
        },

        error: function(err) {
        console.log(err);

        }
    });
//event.preventDefault();

}

function SaveSelectionDB(data) {

   payload = JSON.stringify(data);
    //console.log(payload);
    path = dbprefix + "/api/ppi/selection/create";
    $.ajax({
        type: "POST",
        url: path,
        contentType: "application/json",
        data: payload,
        dataType: "json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        success: function(response) {

            console.log(response);
            },
        error: function(err) {
        console.log(err);
        }
    });
//event.preventDefault();
}
