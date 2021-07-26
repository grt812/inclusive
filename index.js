$(()=>{
    let expanded = false;
    var audioElement = document.createElement('audio');

    //UI Stuff

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
        audioElement.pause();
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
            if($("#search").val().trim() !== ""){
                $("#inner").addClass("searching");
            }
        } else {
            // console.log(e.target);
            $("#search-results").hide();
            $("#inner").removeClass("searching");
            // $("#idk-container").show();
        }
        // if(!expanded){
        //
        // }
    });


    //Audio javascript
    // let modifiedPosition = false;

    let dragging = false;
    $("#pausePlay").click(function(){
        if(audioElement.paused){
            audioElement.currentTime = $("#seek").val();
            audioElement.play();
            // modifiedPosition = true;
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
        console.log("update");
    });

    function modifyCurrentTime(time){
        let tempSeconds = (Math.floor(time % 60).toLocaleString(undefined, {minimumIntegerDigits: 2}));
        let tempMinutes = Math.floor(time / 60);
        $("#current").text(tempMinutes+":"+tempSeconds);
    }

    $("#seek").mousedown(function(){
        audioElement.pause();
        dragging = true;
        // modifiedPosition = true;
        modifyCurrentTime($("#seek").val());
    });

    $("#seek").mouseup(function(){
        dragging = false;
    });

    $("#seek").mousemove(function(){
        modifyCurrentTime($("#seek").val());
    });

    function playAudio(source){
        audioElement.setAttribute("src", source);
        audioElement.load();
        audioElement.play();

    }

    let typingTimer;
    $("#search").on("input", function(){
        clearTimeout(typingTimer);
        $("#inner").addClass("searching");
        if($("#search").val().trim() == ""){
            $("#search-results").html("");
        }
    });

    function updateSearch(list){
        $("#search-results").html("");
        list.forEach(function(item){
            console.log("Item: "+ item);
            let artistString = item.artists.length === 1 ? item.artists[0] : item.artists.slice(0, -1).join(", ") + ", "+ item.artists.slice(-1);
            let templateHTML = `
            <div class="search-result" data-title="${item.name}" data-artists="${artistString}">
                <img src="${item.image}">
                <div class="song-description">
                    <div class="title">${item.name}</div>
                    <div class="artist">${artistString}</div>
                </div>
            </div>
            `;
            $("#search-results").append(templateHTML);
        });
    }


    $("#search").on("keyup", function(){
        clearTimeout(typingTimer);
        typingTimer = setTimeout(function(){
            if($("#search").val().trim() !== ""){
                $.get("/search?q="+$("#search").val(), function(response) {
                  let doubleQuotes = response.replace(/'/g, '"')
                  // stringList.map(function(e, i){
                  //     if(i === 0){
                  //         return e+"}";
                  //     } else if(i === stringList.length - 1){
                  //         return "{"+e;
                  //     } else {
                  //         return "{"+e+"}"
                  //     }
                  // });
                  // console.log(stringList);
                  // let songList = stringList.map(e => JSON.parse(e));
                  // updateSearch(songList);
                  console.log("Response: "+doubleQuotes);
                  songList = JSON.parse(doubleQuotes.replaceAll("{{apostrophe}}", "'").replaceAll("{{double}}", "'"));
                  console.log("list length: "+songList.length)
                  // console.log("Song List: "+songList);
                  updateSearch(songList);
                  // $("#")
                });
            }
        }, 500);
    });

    // $(document).click(function(){
    //     playAudio("https://www.w3schools.com/jsref/horse.ogg");
    // });


});
