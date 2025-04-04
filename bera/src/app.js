import $ from 'jquery';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
//default locations for top bar
const defaultLoc1 = 'W8EDU';
const defaultLoc2 = 'NA8SA';
//funcs
function changeLocs(loc1, loc2){
    $('#loc1').text(loc1);
    $('#loc2').text(loc2);
}
window.toggleChart = function toggleChart(divID){
    $(divID).toggle();
}
/*
!!! document ready function !!!
*/
$(document).ready(function() {
    //set default locations
    changeLocs(defaultLoc1, defaultLoc2);
    //set checkboxes to unchecked
    $('input[type=checkbox]').prop('checked', false);
});