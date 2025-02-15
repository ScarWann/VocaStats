var submitApp = angular.module('singersSongsApp', []);
submitApp.controller('singersSongsController', function($scope) {
    document.getElementById("body").style.backgroundColor = "aliceblue"
    $scope.submit = async function() {
    const response = await fetch("/songAmounts.json", {
        method: "POST",
        body: JSON.stringify({
            type: "songs",
            subtype: document.getElementById("subtypeDropdown").value,
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