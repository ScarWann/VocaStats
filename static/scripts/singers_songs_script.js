function changeStyle(mode) {
    if (mode == "Songs") {
        document.getElementById("artistsButton").href = "http://127.0.0.1:5000/artists_songs/"
        document.getElementById("switchButton").style.backgroundColor = "rgb(236, 131, 166)";
        document.getElementById("main-sidebar").style.backgroundColor = "aquamarine";
        document.getElementById("body").style.backgroundColor = "aliceblue";
    } else {
        document.getElementById("artistsButton").href = "#"
        document.getElementById("switchButton").style.backgroundColor = "aquamarine";
        document.getElementById("main-sidebar").style.backgroundColor = "rgb(236, 131, 166)";
        document.getElementById("body").style.backgroundColor = "pink";
    }
}

var submitApp = angular.module('singersSongsApp', []);
submitApp.controller('singersSongsController', function($scope) {
    document.getElementById("body").style.backgroundColor = "aliceblue"
    $scope.submit = async function() {
    const response = await fetch("/songAmounts.json", {
        method: "POST",
        body: JSON.stringify({
            type: "singer_songs",
            subtype: document.getElementById("subtypeDropdown").value,
            artists: [$scope.name]
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });
    const json = await response.json();
    $scope.json = json;
    document.getElementById("singerOutput").style.display = "block";
    //document.getElementById("songsAmount").innerHTML = songsAmount;
    //document.getElementById("singer").innerHTML = $scope.name;
    console.log(document.getElementById("body").style.backgroundColor);
    Plotly.newPlot( document.getElementById('chart'), 
                    [json.body[0]],
                    {paper_bgcolor: document.getElementById("body").style.backgroundColor,
                    plot_bgcolor: document.getElementById("body").style.backgroundColor},
                    {responsive: true});
    };

    $scope.mode = "Songs";
    $scope.switchMode = function() {
        console.log($scope.mode);
        if ($scope.mode == "Songs") { 
            document.getElementById("songsButton").style.display = "none";
            document.getElementById("singersButton").style.display = "none";
            changeStyle("Views");
            $scope.mode = "Views";
        } else {
            document.getElementById("songsButton").style.display = "block";
            document.getElementById("singersButton").style.display = "block";
            changeStyle("Songs");
            $scope.mode = "Songs";
        };
        Plotly.newPlot( document.getElementById('chart'), 
                    [$scope.json.body[0]],
                    {paper_bgcolor: document.getElementById("body").style.backgroundColor,
                    plot_bgcolor: document.getElementById("body").style.backgroundColor},
                    {responsive: true});
    };
});