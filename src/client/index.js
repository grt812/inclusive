$(()=>{
    let expanded = false;

    var audioElement = document.createElement('audio');
    // $("#search").focus(()=>{
    //
    // });

    // $(".svg-icon").each(()=>{
    //
    // });
    $(".svg-container").mouseenter(function(){
        let tempSrc = $(this).find("img").attr("src");
        $(this).find("img").attr("src", tempSrc.slice(0, tempSrc.indexOf(".") - 1) + "2.svg");
    });
    $(".svg-container").mouseleave(function(){
        let tempSrc = $(this).find("img").attr("src");
        $(this).find("img").attr("src", tempSrc.slice(0, tempSrc.indexOf(".") - 1) + "1.svg");
    });

    function expand(){
        expanded = true;
        $("#inner").addClass("expand");
        // $("#search-results").show(0);
        // $("#player").show();
        // $("#or").hide();
        // $("#idk").text("Play Something New");
        $("#exit-expanded").show(0);
        // $("#left-container").show();
        $("#queue").show(0);
        $("#idk-container").hide();
        adjustSearch();
        playAudio("https://www.kozco.com/tech/organfinale.wav");
    }

    function contract(){
        expanded = false;
        $("#inner").removeClass("expand");
        // $("#player").hide();
        // $("#search-results").hide();
        // $("#or").show();
        // $("#idk").text("I Don't Know");
        $("#exit-expanded").hide(0);
        $("#queue").hide(0);
        $("#idk-container").show();
        adjustSearch();
    }

    function adjustSearch(){
        $("#search-results").width($("#search").width());
        if(expanded){
            $("#search-results").css("left", $("#search").offset().left);
        } else {
            $("#search-results").css("left", 0);
        }
    }

    function init(){
        contract();
        $("#search-results").hide();
        adjustSearch();
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

    $(window).resize(()=>{
        adjustSearch();
    });


    $(document).on("focus click",(e)=>{
        if(e.target === document.getElementById("search")){
            // $("#idk-container").hide();
            adjustSearch();
            $("#search-results").show();
        } else {
            // console.log(e.target);
            $("#search-results").hide();
            // $("#idk-container").show();
        }
        // if(!expanded){
        //
        // }
    });


    //Audio javascript
    let modifiedPosition = false;
    $("#pausePlay").click(function(){
        if(audioElement.paused){
            audioElement.currentTime = $("#seek").val();
            audioElement.play();
            modifiedPosition = true;
        } else {
            audioElement.pause();
        }
    });

    audioElement.addEventListener("canplay",function(){
        let tempSeconds = (Math.floor(audioElement.duration % 60)).toLocaleString(undefined, {minimumIntegerDigits: 2});
        let tempMinutes = Math.floor(audioElement.duration / 60);
        $("#duration").text(tempMinutes+":"+tempSeconds);
        $("#seek").attr("max", audioElement.duration);
        this.play();
    });

    audioElement.addEventListener("timeupdate",function(){
        let tempSeconds = (Math.floor(audioElement.currentTime % 60).toLocaleString(undefined, {minimumIntegerDigits: 2}));
        let tempMinutes = Math.floor(audioElement.currentTime / 60);
        $("#current").text(tempMinutes+":"+tempSeconds);
        $("#seek").val(audioElement.currentTime);
    });

    $("#seek").mousedown(function(){
        audioElement.pause();
        modifiedPosition = true;
    });

    function playAudio(source){
        audioElement.setAttribute("src", source);
        audioElement.load();
        audioElement.play();

    }

    // $(document).click(function(){
    //     playAudio("https://www.w3schools.com/jsref/horse.ogg");
    // });


});
