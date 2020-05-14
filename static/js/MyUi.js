/////// USER EDITABLE
/////// HERE ARE BUTTON MAPPINGS FROM HTML FILE
/////// AND CALLS TO FLASK AND DataDiVR_API

// add MAPPINGS TO UI ELEMENTS HERE //

$(document).ready(function () {


  //LOAD NAMESPACE MENU TAB 1
  $(function () {
    $("#namespaces").selectmenu();
  });

  $('#namespaces').on('selectmenuselect', function () {
    var name = $('#namespaces').find(':selected').text();
    //logger(name);
    console.log(name);
    UpdateNamespace(name);

  });

$(function () {
    $("#test").button();
    $("#test").click(function (event) {
        event.preventDefault();
        console.log("oggggoggogg");
    });
});




  $(function () {
    $("#tabs").tabs();
  });


  //selection menu tab-2

   $(function () {
        console.log("appending optiomns");
        $("#selectMode").selectmenu();
        $('#selectMode').append($('<option>', {value: "NEW",text: "NEW",}));
        $('#selectMode').append($('<option>', {value: "ADD",text: "ADD",}));
        $('#selectMode').append($('<option>', {value: "SUB",text: "SUB",}));
        $('#selectMode').val("NEW");   //SET ACTIVE SLOT
        $('#selectMode').hide();
        $('#selectMode').selectmenu("refresh");

    });

    $('#selectMode').on('selectmenuselect', function () {

        logger($('#selectMode').val());
    });




  $(function () {
    $("#selections").selectmenu();
  });

  $('#selections').on('selectmenuselect', function () {
    var name = $('#selections').find(':selected').text();
    ue4("loadSelection","loadSelection");
    logger(name);
  });


  $(function () {
    $("#LoadSelection").button();
        $("#LoadSelection").click(function (event) {
            event.preventDefault();
            logger($("#selectMode").val() + " " + $("#selections").val() );
            //ActivateVRkeyboard("test");
        });
    });




  $(function () {
    $("#saveSel").button();
    $("#saveSel").click(function (event) {
        event.preventDefault();

        ActivateVRkeyboard("saveSel");
        //ue4("GetSelection","oggggoggogg");
    });
  });

  // SLIDERS for tabs-3



  $(function () {
    $("#slider_scale").slider({
      range: "max",
      min: 0,
      max: 255,
      value: 128,
      slide: function (event, ui) {
        ue4("SetScale", ui.value);
      }
    });


    $("#slider-node_size").slider({
      range: "max",
      min: 0,
      max: 255,
      value: 128,
      slide: function (event, ui) {
        ue4("SetNodeSize", ui.value);
      }
    });

    $("#slider-link_size").slider({
      range: "max",
      min: 0,
      max: 255,
      value: 128,
      slide: function (event, ui) {
        ue4("SetLinkSize", ui.value);
      }
    });

    $("#slider-link_transparency").slider({
      range: "max",
      min: 0,
      max: 255,
      value: 128,
      slide: function (event, ui) {

        ue4("SetLinkAlpha", ui.value);
      }
    });

    $("#slider-light").slider({
      range: "max",
      min: 0,
      max: 255,
      value: 128,
      slide: function (event, ui) {

        ue4("SetLight", ui.value);

      }
    });
    ue4("Init", "init");
  });



  // Tabs-3


  $(function () {
    $("#morph_button").button();
    $("#morph_button").click(function (event) {
      event.preventDefault();
      logger("ihatemylife")
      ue4("Morph", "bla");
    });
  });


  $(function () {
    $("#left_handed").checkboxradio({
      icon: false,
    });
  });

  // SLIDERS FOR RANDOMWALK tab-6


  $(function () {
    $("#slider-restart_probability").slider({
      range: "max",
      min: 1,
      max: 100,
      value: 20,
      slide: function (event, ui) {
        $("#restart_probability").html(ui.value / 100);
      }
    });
    $("#restart_probability").val($("#slider-range-min").slider("value"));
  });



// TAB4 SEARCH
    $(function () {
        $("#searchAttribute1").selectmenu();
        $('#searchAttribute1').append($('<option>', {value: "DISEASE",text: "DISEASE",}));
        $('#searchAttribute1').append($('<option>', {value: "PATHWAY",text: "PATHWAY",}));
        $('#searchAttribute1').append($('<option>', {value: "molecular_function",text: "molecular_function",}));
        $('#searchAttribute1').append($('<option>', {value: "cellular_component",text: "cellular_component",}));
        $('#searchAttribute1').append($('<option>', {value: "biological_process",text: "biological_process",}));
        $('#searchAttribute1').append($('<option>', {value: "TISSUE",text: "TISSUE",}));
        $('#searchAttribute1').append($('<option>', {value: "HUMAN_PHENOTYPE",text: "HUMAN_PHENOTYPE",}));
        $('#searchAttribute1').val("TISSUE");   //SET ACTIVE SLOT
        $("#searchAttribute1").selectmenu("refresh");
    });

    $('#searchAttribute1').on('selectmenuselect', function () {
        var name = $('#searchAttribute1').find(':selected').text();
        logger("Attribute says: "+ name);
    });




  $(function () {
    $("#searchInput1").button();
    $("#searchInput1").attr("searchID", -1);
    $("#searchInput1").click(function (event) {
      event.preventDefault();
      ActivateVRkeyboard("searchInput1");

      //GetDbSearchTerms("af", $('#searchAttribute1').val());

    });
  });

  //desktop version input field1
   $("#search_txt").keyup(function(){
       GetDbSearchTerms($(this).val(),$('#searchAttribute1').val());
   });



    $(function () {
        $("#searchMode1").selectmenu();
        $('#searchMode1').append($('<option>', {value: "NEW",text: "NEW",}));
        $('#searchMode1').append($('<option>', {value: "ADD",text: "ADD",}));
        $('#searchMode1').append($('<option>', {value: "SUB",text: "SUB",}));
        $('#searchMode1').val("NEW");   //SET ACTIVE SLOT
        $('#searchMode1').hide();
        $('#searchMode1').selectmenu("refresh");

    });




 $(function () {
    $("#searchGO").button();
    $("#searchGO").click(function (event) {
        event.preventDefault();
        var id = $("#searchInput1").attr("searchID");

        SimpleSearch(id);
    });
 });

  $(function () {
    $("#SaveSearch").button();
    $("#SaveSearch").click(function (event) {
        event.preventDefault();
        ActivateVRkeyboard("SaveSearch");
    });
 });

  //buttons fuer randomwalk

  $(function () {
    $("#start_randomwalk_button").button();
    $("#start_randomwalk_button").click(function (event) {
      event.preventDefault();
      var span_Text = document.getElementById("restart_probability").innerText;
      logger(span_Text)
      ue4("StartRandomWalk", span_Text);
      reloadForceLayout (inputdata1);
    });
  });

  $(function () {
    $("#clear_randomwalk_button").button();
    $("#clear_randomwalk_button").click(function (event) {
      event.preventDefault();
      ue4("ClearRandomWalk", "bla");
      clearForceLayout (inputdata);
    });
  });

  ///////INIT HERE

 GetDbFileNames1();
  console.log("running myui")




    //drawit(input);





  // INITIALIZE STUFF HERE
  //read files and populate ui's



  /*     document.getElementById("SendButton").onclick = function() {
          postFlask("/_receive_json/", nodes)
      };
      document.getElementById("ReadButton").onclick = function() {
          postFlask("/_request_json/", requestTxt)
      }; */


  /*     $( "#slider-6" ).slider({
                 range:false,
                 min: 0,
                 max: 500,
                 values: [250],

                 slide: function( event, ui ) {
                    // $( "#slidevalue" )
                       //.val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
                        logger(ui.values[ 0 ] );
                        ue4("print", ui.values[ 0 ]);
                 }
       }); */



});
