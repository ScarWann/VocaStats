const SONGS = 0;
const VIEWS = 1;
const YEARLY = 4
const MONTHLY = 7;
const DAILY = 10;
const AT = 0;
const PER = 1;
const INCR = 2;
const modes = {
    "songsPerDay": [SONGS, PER, DAILY],
    "songsAtMonth": [SONGS, AT, MONTHLY],
    "songsPerMonth": [SONGS, PER, MONTHLY],
    "songsIncrMonth": [SONGS, INCR, MONTHLY],
    "songsAtYear": [SONGS, AT, YEARLY],
    "songsPerYear": [SONGS, PER, YEARLY],
    "songsIncrYear": [SONGS, INCR, YEARLY]
}

var submitApp = angular.module('singersSongsApp', []);
submitApp.controller('singersSongsController', function($scope) {
    document.getElementById("body").style.backgroundColor = "aliceblue"
    $scope.submit = async function() {
    const response = await fetch("/songAmounts.json", {
        method: "POST",
        body: JSON.stringify({
            type: modes[document.getElementById("subtypeDropdown").value][0],
            subtype: modes[document.getElementById("subtypeDropdown").value].slice(1),
            artists: [$scope.name]
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });
    const json = await response.json();
    $scope.json = json;
    Plotly.newPlot( document.getElementById('chart'), 
                    [json.body[0]],
                    {paper_bgcolor: document.getElementById("body").style.backgroundColor,
                    plot_bgcolor: document.getElementById("body").style.backgroundColor},
                    {responsive: true});
    };
});