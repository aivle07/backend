
// var ctx = document.getElementById("myChart").getContext("2d");
var param = document.getElementById("param").innerText;

var now_value = document.querySelector("#now-value");
var today_volume = document.querySelector("#today-volume");
var before_day = document.querySelector("#before-day");
var today_high = document.querySelector("#today-high");

var price_change = document.querySelector("#price-change");
var today_change_rate =document.querySelector("#today-change-rate");
var today_open = document.querySelector("#today-open");
var today_low = document.querySelector("#today-low");

var chart = document.querySelector("#chart");

// var graphData = {
//     type: "line",
//     data: {
//         labels: ["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
//         "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
//         "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
//         "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
//         "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
//         ],
//         datasets: [{
//             label: "최근 100일간 차트",
//             data: [],
//             backgroundColor: [
//                 'rgba(73, 198, 230, 0.5)',
//             ],
//             borderWidth: 1
//         }]
//     },
//     options: {} 
// }

// var myChart = new Chart(ctx, graphData);

var socket = new WebSocket("ws://localhost:8000/ws/graph/?"+param);

socket.onopen = function(e){
    console.log('open');
}

socket.onmessage = function(e){
    var djangoData = JSON.parse(e.data);
    // var djangoData = JSON.stringify(e.data);
    console.log(djangoData);
    // console.log(typeof djangoData.value[0]);
    // console.log(djangoData.value[0]);
    $('#chart').html(djangoData.value[0]);
    // chart.innerHTML = djangoData.value[0];
    // graphData.data.datasets[0].data = djangoData.value[0];
    // now.innerText = djangoData.value[1];
    // 현재가격
    now_value.innerText = (djangoData.value[1].now_value).toLocaleString();
    now_value.style = "color:" + djangoData.value[1].now_value_color + ";";

    // 거래량
    today_volume.innerText = (djangoData.value[1].today_volume).toLocaleString();

    // 전날 종가
    before_day.innerText = (djangoData.value[1].before_day).toLocaleString();

    // 오늘 고가
    today_high.innerText = (djangoData.value[1].today_high).toLocaleString();
    today_high.style = "color:" + djangoData.value[1].today_high_color + ";";

    // 전일대비 가격
    price_change.innerText = (djangoData.value[1].price_change).toLocaleString();
    price_change.style = "color:" + djangoData.value[1].price_change_color + ";";

    //등락율
    today_change_rate.innerText = djangoData.value[1].today_change_rate;
    today_change_rate.style = "color:" + djangoData.value[1].today_change_rate_color + ";";

    //시작가격
    today_open.innerText = (djangoData.value[1].today_open).toLocaleString();
    today_open.style = "color:" + djangoData.value[1].today_open_color + ";";

    // 오늘 저가
    today_low.innerText = (djangoData.value[1].today_low).toLocaleString();
    today_low.style = "color:" + djangoData.value[1].today_low_color + ";";


    // 매수 폼 hidden
    input_now_value = document.getElementById("input-now-value");
    input_now_value.value = djangoData.value[1].now_value;

    // myChart.update();

}

document.addEventListener('DOMContentLoaded', function() {
    var usernames = document.querySelectorAll('.username');
    usernames.forEach(function(userElement) {
        var fullname = userElement.textContent.trim();
        var maskedName = fullname.substring(0, fullname.length - 1) + '*';
        userElement.textContent = maskedName + '님 반갑습니다.';
    });
});
