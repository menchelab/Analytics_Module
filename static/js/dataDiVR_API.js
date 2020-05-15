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



//// FUNCTIONS CALLED BY UE4

ue.interface.setPayload = function(payload)
{
    input = JSON.parse(payload);
    logger("setPayload says:");
    logger(input);

};

ue.interface.getSelection = function(data)
{
    //logger(data);
   // i
    //dummydata = '{"node_ids":[12149,108],"selection_name":"somAARGrgARGagname"}';
    //input = JSON.parse(data);
    //logger(input);
    SaveSelectionDB(data);
};

ue.interface.getRandomWalkResult = function(data)
{
    input = JSON.parse(data);
    logger("getSelection triggered");
    logger(input);
    reloadForceLayout (input);
};

// call a function named route + "Trigger" defined below for each input field
ue.interface.VRkeyboard = function(payload)
{
    input = JSON.parse(payload);
// Call function dynamically
    var fnName = input.route + "Trigger";;
    window[fnName](input);
    logger("VRKeyboard triggered:"+ fnName);
};

// TEXT INPUT FIELDS
function searchInput1Trigger(data){
    //logger(data);
    // SET BUTTON TEXT
    var element = "#" + data.route;
    $(element).html(data.content);
    //logger(data.content);
    GetDbSearchTerms(data.content,$('#searchAttribute1').val());

/*     if (data.end == 1){
        logger(data.route + " Event Fired");
    } */
}

function SaveSearchTrigger(data){
    logger(data);
    // SET BUTTON TEXT
    //var element = "#" + data.route;
    //$(element).html(data.content);

    if (data.end == 1){
        ue4("getSelection", data.content);
        logger(data.route + " Event Fired");
    }
}

function saveSelTrigger(data){
/*     logger(data);
    var element = "#" + data.route;
    $(element).html(data.content); */


    if (data.end == 1){  //USER PRESST ENTER KEY
        // Get Selection from UE4 somehow
        ue4("getSelection", data.content);
        //var dummySelData =  {"selection_name": data.content,"node_ids":[1,2,3,4,5,99,666,1337]};
        logger(data.route + " Event Fired");
    }
}





ue.interface.setFilenames = function(payload)
{
    input = JSON.parse(payload);
    //logger("setFilenames says:");
    //logger(input.nodes[1]);

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
    logger("vrkeyboard");
}

////put functions that POST to Flask HERE vvv
function UpdateNamespace(name) {

    thisNamespace = dbdata.find(o => o.namespace === name);
    logger(thisNamespace);

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
            //logger(response);
        // POPULATE UI DROPDOWN
            dbdata = response.slice(); //DEEP COPY !!!!
            //logger(dbdata)

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
        logger(err);

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
            //logger(response.["a"]);
            GetDbLabelList1(name);

/*             response.forEach(function(item)
            {

                 logger(item["a"][0])
            }); */
        },

        error: function(err) {
        logger(err);

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
                    logger("linklist loaded" + path);
            },
        error: function(err) {
        logger(err);
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
                    //logger(response);
            },
        error: function(err) {
        logger(err);
        }
    });
}



////Search and auto complete dynamic button factory
function GetDbSearchTerms(name, namespace) {


    path = dbprefix + "/api/ppi/attribute/?prefix="+ name + "&namespace="+ namespace;
    //logger(path);
    if (name.length > 1){
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {

        clearButtons("autocomp");

            response.forEach(function(item)
            {
                createButton(item.name,item.id,"autocomp");
                 //$('#layouts').append($('<option>', {value: item,text: item}));
            });

        logger(response);
        },

        error: function(err) {
        logger(err);

        }
    });
//event.preventDefault();
    }

}


function createButton(Bname,Bid,Parent) {

    var r=$('<input/>').attr({
        type: "button",
        id: Bid,
        value: Bname

    });
    var p = '#' + Parent;
    $(p).append(r);
    $(r).button();
    $(r).click(function() {
        $("#searchInput1").text(Bname);
        $("#searchInput1").attr("searchID",Bid);
        console.log(Bname + " " + Bid + " " + Parent);
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
    });
}


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

                 $('#selections').append($('<option>', {value: item.name, text: item.name}));
            });
            $('#selections').val( response[0].namespace);
            $("#selections").selectmenu("refresh");
        logger(response);
        },

        error: function(err) {
        logger(err);

        }
    });
//event.preventDefault();

}

function SimpleSearch(id) {

    path = dbprefix + "/api/"+ thisNamespace.namespace + "/node/search?subject0=attribute&object0=" + id ;
        $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {

            response.mode = $('#searchMode1').val();
            logger(response);
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
        logger(err);

        }
    });
//event.preventDefault();

}

function SaveSelectionDB(data) {

   payload = JSON.stringify(data);
    //logger(payload);
    path = dbprefix + "/api/ppi/selection/create";
    $.ajax({
        type: "POST",
        url: path,
        contentType: "application/json",
        data: payload,
        dataType: "json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        success: function(response) {

            logger(response);
            },
        error: function(err) {
        logger(err);
        }
    });
//event.preventDefault();
}
