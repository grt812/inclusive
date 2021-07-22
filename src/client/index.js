$(()=>{
    let expanded = false;
    // $("#search").focus(()=>{
    //
    // });

    function expand(){
        expanded = true;
        $("#inner").addClass("expand");
        $("#search-results").show(0);
        // $("#player").show();
        // $("#or").hide();
        $("#idk").text("Play Something New");
        $("#exit-expanded").show(0);
    }

    function contract(){
        expanded = false;
        $("#inner").removeClass("expand");
        // $("#player").hide();
        $("#search-results").hide();
        // $("#or").show();
        $("#idk").text("I Don't Know");
        $("#exit-expanded").hide(0);
    }

    function init(){
        contract();
    }

    init();

    $(".search-result").click(()=>{
        expand();
    });

    $("#idk").click(()=>{
        expand();
    });

    $("#exit-expanded").click(()=>{
        contract();
    });



    $(document).on("focus click",(e)=>{
        if(!expanded){
            if(e.target === document.getElementById("search")){
                // $("#idk-container").hide();
                $("#search-results").show();
            } else {
                // console.log(e.target);
                $("#search-results").hide();
                // $("#idk-container").show();
            }
        }
    });


});
