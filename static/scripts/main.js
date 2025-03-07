var submitApp = angular.module('singersSongsApp', []);
submitApp.controller('singersSongsController', function($scope) {
    $scope.submitArtist = async function() {
    const response = await fetch("/songAmounts.json", {
        method: "POST",
        body: JSON.stringify({
            type: "songs",
            subtype: document.getElementById("songSubtypeDropdown").value,
            artists: [$scope.artistName]
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });
    const json = await response.json();
    $scope.json = json;
    Plotly.newPlot( document.getElementById('amountChart'), 
                    [json.body[0]],
                    {paper_bgcolor: document.getElementById("body").style.backgroundColor,
                    plot_bgcolor: document.getElementById("body").style.backgroundColor},
                    {responsive: true});
    };
    $scope.submitSong = async function() {
        const response = await fetch("/songViews.json", {
            method: "POST",
            body: JSON.stringify({
                type: "views",
                subtype: document.getElementById("viewsSubtypeDropdown").value,
                songs: [$scope.songName]
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        });
        
    }
});