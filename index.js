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
        $("#for-you").hide();
        adjustSearch();
        // playAudio("https://www.kozco.com/tech/organfinale.wav");
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
        $("#for-you").show();
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

    // $(".search-result").click(()=>{
    //     expand();
    // });

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
            // $("#for-you").hide();
            adjustSearch();
            $("#search-results").show();
            if($("#search").val().trim() !== ""){
                $("#inner").addClass("searching");
            }
        } else {
            // console.log(e.target);
            $("#search-results").hide();
            $("#inner").removeClass("searching");
            // $("#for-you").show();
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
            $(this).html(`<span class="material-icons">pause</span>`)
            // modifiedPosition = true;
        } else {
            audioElement.pause();
            $(this).html(`<span class="material-icons">play_arrow</span>`)
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
        // console.log("update");
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
        audioElement.play();
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

    $("#search").keydown(function(e){
        if(e.which === 38){
            let tempIndex = $(".search-result.selected").index();
            if(tempIndex <= 0){
                $(".search-result.selected").removeClass("selected");
                $(".search-result").eq($("#search-results").children().length - 1).addClass("selected");
            } else {
                $(".search-result.selected").removeClass("selected");
                $(".search-result").eq(tempIndex - 1).addClass("selected");
            }
        } else if(e.which === 40){
            let tempIndex = $(".search-result.selected").index();
            // console.log("Current Index: "+tempIndex);
            if(tempIndex >= $("#search-results").children().length - 1){
                $(".search-result.selected").removeClass("selected");
                $(".search-result").eq(0).addClass("selected");
            } else {
                $(".search-result.selected").removeClass("selected");
                $(".search-result").eq(tempIndex + 1).addClass("selected");
            }
        }
        setTimeout(function(){
            if($(".search-result.selected").length){
                $("#search-results").stop(true).animate({scrollTop: $(".search-result.selected").offset().top - $("#search-results").offset().top + $("#search-results").scrollTop() - $("#search-results").height()/2 + $(".search-result.selected").height()/2}, 200);
            }
        }, 10);
        if(e.which === 13){
            $(".search-result.selected").trigger("click");
        }
    });

    function updateQueue(first, list){
        $("#queue").html("");
        list.unshift(first);
        list.forEach(function(item, index){
            let templateHTML = `
            <div class="queue-item new ${index === 0?"selected":""}">
                <img src="${item.img}">
                <div class="song-description">
                    <div class="title">${item.name}</div>
                    <div class="artist">${item.artists}</div>
                </div>
            </div>
            `;
            $(".new").click(()=>{
                expand();
                $("#thumbnail").attr("src", "/assets/loading.svg");
                $("#thumbnail").addClass("loading");
                $("#card-title").text(item.name);
                $("#card-artist").text(item.artists);
                $.get(`/song?name=${item.name}&artists=${item.artists.replace(/\s/g, '')}&id=${item.id}`).done(function(response){
                    let responseObject = JSON.parse(response);
                    playAudio(responseObject.audio)
                    $("#thumbnail").attr("src", responseObject.img);
                    $("#thumbnail").removeClass("loading");

                });
            });
            $(".new").removeClass("new");
            $("#queue").append(templateHTML);
        });
    }




    function updateSearch(list){
        $("#search-results").html("");
        list.forEach(function(item, index){
            // console.log("Item: "+ item);
            let artistString = item.artists.length === 1 ? item.artists[0] : item.artists.slice(0, -1).join(", ") + ", "+ item.artists.slice(-1);
            let artistURI = item.artists.length === 1 ? item.artists[0] : item.artists.slice(0, -1).join(",") + ","+ item.artists.slice(-1);
            let templateHTML = `
            <div class="search-result new ${index === 0 ? "selected" : ""}" data-title="${item.name}" data-artists="${artistString}">
                <img src="${item.image}">
                <div class="song-description">
                    <div class="title">${item.name}</div>
                    <div class="artist">${artistString}</div>
                </div>
            </div>
            `;
            $("#search-results").append(templateHTML);
            $(".new").click(()=>{
                expand();
                $("#thumbnail").attr("src", "/assets/loading.svg");
                $("#thumbnail").addClass("loading");
                $("#card-title").text(item.name);
                $("#card-artist").text(artistString);
                $.get(`/song?name=${item.name}&artists=${artistURI}&id=${item.id}`).done(function(response){
                    let responseObject = JSON.parse(response);
                    playAudio(responseObject.audio)
                    $("#thumbnail").attr("src", responseObject.img);
                    $("#thumbnail").removeClass("loading");
                });
            });
            $(".new").one("click", function(){
                //Queue Limit?
                $.get(`/recommend?id=${item.id}&limit=20`, function(response){
                    console.log(response);
                    arrayResponse = JSON.parse("["+response+"]");
                    updateQueue({"name":item.name, "artists":artistString, "img":item.image, "id":item.id}, arrayResponse);
                });
            });
            $(".new").removeClass("new");
        });
    }


    $("#search").on("keyup", function(e){
        if(e.which !== 37 && e.which !== 38 && e.which !== 39 && e.which !== 40 && e.which !== 13){
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
                      // console.log("Response: "+doubleQuotes);
                      songList = JSON.parse(doubleQuotes.replaceAll("{{apostrophe}}", "'").replaceAll("{{double}}", "'"));
                      // console.log("list length: "+songList.length)
                      // console.log("Song List: "+songList);
                      updateSearch(songList);
                      // $("#")
                    });
                }
            }, 500);
        }
    });

    // $(document).click(function(){
    //     playAudio("https://www.w3schools.com/jsref/horse.ogg");
    // });


});
