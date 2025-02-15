function changeStyle(mode) {
    if (mode == "Views") {
        document.getElementById("switchButton").style.backgroundColor = "aquamarine";
        document.getElementById("singersButton").href = "#"
        document.getElementById("artistsButton").href = "#"
        document.getElementById("main-sidebar").style.backgroundColor = "rgb(236, 131, 166)";
        document.getElementById("body").style.backgroundColor = "pink";
    } else {
        document.getElementById("switchButton").style.backgroundColor = "rgb(236, 131, 166)";
        document.getElementById("main-sidebar").style.backgroundColor = "aquamarine";
        document.getElementById("singersButton").href = "singers_songs"
        document.getElementById("artistsButton").href = "artists_songs"
        document.getElementById("body").style.backgroundColor = "aliceblue";
    }
}

var mainSidebarApp = angular.module('main-sidebar', []);
mainSidebarApp.controller('main-sidebar-controller', function($scope) {
    $scope.mode = "Views";
    $scope.switchMode = function() {
        console.log($scope.mode);
        if ($scope.mode == "Songs") { 
            document.getElementById("songsButton").style.display = "none";
            changeStyle("Views");
            $scope.mode = "Views";
        } else {
            document.getElementById("songsButton").style.display = "block";
            changeStyle("Songs");
            $scope.mode = "Songs";
        };
    };
});