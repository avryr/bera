import $ from 'jquery';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
var defaultLoc1 = 'CWRU';
var defaultLoc2 = 'NASA';
function changeLocs(loc1, loc2){
    $('#loc1').text(loc1);
    $('#loc2').text(loc2);
}

$(document).ready(function() {
    changeLocs(defaultLoc1, defaultLoc2);
});