
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

var graphData = {
    type: "line",
    data: {
        labels: ["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
        "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
        "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
        "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
        "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
        ],
        datasets: [{
            label: "최근 100일간 차트",
            data: [],
            backgroundColor: [
                'rgba(73, 198, 230, 0.5)',
            ],
            borderWidth: 1
        }]
    },
    options: {} 
}

// var myChart = new Chart(ctx, graphData);

var socket = new WebSocket("ws://localhost:8000/ws/graph/?"+param);

socket.onopen = function(e){
    console.log('open');
}

socket.onmessage = function(e){
    var djangoData = JSON.parse(e.data);
    // var djangoData = JSON.stringify(e.data);
    console.log(djangoData);
    console.log(typeof djangoData.value[0]);
    console.log(djangoData.value[0]);
    
    chart.innerHTML = djangoData.value[0];
    // graphData.data.datasets[0].data = djangoData.value[0];
    // now.innerText = djangoData.value[1];
    // 현재가격
    now_value.innerText = "현재가격 : " + djangoData.value[1].now_value;
    now_value.style = "color:" + djangoData.value[1].now_value_color + ";";

    // 거래량
    today_volume.innerText = "거래량 : " + djangoData.value[1].today_volume;

    // 전날 종가
    before_day.innerText = "전일종가 : " + djangoData.value[1].before_day;

    // 오늘 고가
    today_high.innerText = "고가 : " + djangoData.value[1].today_high;
    today_high.style = "color:" + djangoData.value[1].today_high_color + ";";

    // 전일대비 가격
    price_change.innerText = "전일대비 " + djangoData.value[1].price_change;
    price_change.style = "color:" + djangoData.value[1].price_change_color + ";";

    //등락율
    today_change_rate.innerText = "등락율" + djangoData.value[1].today_change_rate;
    today_change_rate.style = "color:" + djangoData.value[1].today_change_rate_color + ";";

    //시작가격
    today_open.innerText = "시작가격 : " + djangoData.value[1].today_open;
    today_open.style = "color:" + djangoData.value[1].today_open_color + ";";

    // 오늘 저가
    today_low.innerText = "저가 : " + djangoData.value[1].today_low;
    today_low.style = "color:" + djangoData.value[1].today_low_color + ";";


    // 매수 폼 hidden
    input_now_value = document.getElementById("input-now-value")
    input_now_value.value = djangoData.value[1].now_value;

    // myChart.update();

}
