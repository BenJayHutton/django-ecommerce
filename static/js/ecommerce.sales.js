$(document).ready(function(){
    function renderChart(id, data, labels){
        var ctx = $('#' + id);
        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Sales',
                    data: data,
                    backgroundColor: 'rgba(100, 255, 34, .2)',
                    borderColor: 'rgba(100, 255, 34, .6)',
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                },
            }
        });
    }

    function getSalesData(id, type){
        var url = '/analytics/sales/data/'
        var method = 'GET'
        var data = {"type":type}

        $.ajax({
        url: url,
        method: method,
        data:data,
        success: function(responseData){
            renderChart(id, responseData.data, responseData.labels)
        },
        error: function(error){
            $.alert("An error occurred")
        }
        })
    }
    
    var chartsToRender = $('.bjh-render-chart')
    $.each(chartsToRender, function(index, html){
        var $this = $(this)
        if($this.attr('id') && $this.attr('data-type')){
            getSalesData($this.attr('id'), $this.attr('data-type'))
        }
    })
})
