var submitApp = angular.module('singersSongsApp', []);
submitApp.controller('singersSongsController', function($scope) {
    $scope.submitArtistFetching = async function() {
    const response = await fetch("/songAmounts.json", {
        method: "POST",
        body: JSON.stringify({
            subtype: document.getElementById("songSubtypeDropdown").value,
            artists: [$scope.artistName]
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });
    const json = await response.json();
    $scope.amountsjson = json;
    Plotly.newPlot( document.getElementById('amountChart'), 
                    [json.body[0]],
                    {paper_bgcolor: document.getElementById("body").style.backgroundColor,
                    plot_bgcolor: document.getElementById("body").style.backgroundColor},
                    {responsive: true});
    };
    $scope.submitSongFetching = async function() {
    const response = await fetch("/songViews.json", {
        method: "POST",
        body: JSON.stringify({
            subtype: document.getElementById("viewsSubtypeDropdown").value,
            songs: [$scope.viewsSongName]
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });
    const json = await response.json();
    $scope.viewsjson = json;
    Plotly.newPlot( document.getElementById('viewChart'), 
                [json.body[0]],
                {paper_bgcolor: document.getElementById("body").style.backgroundColor,
                plot_bgcolor: document.getElementById("body").style.backgroundColor},
                {responsive: true});
    }
    $scope.submitSongTracking = async function() {
    const response = await fetch("/trackingResponse.json", {
        method: "POST",
        body: JSON.stringify({
            song: $scope.trackedSongName
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
    alert(response.json()["message"])
    }
});