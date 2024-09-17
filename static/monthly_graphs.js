window.addEventListener('DOMContentLoaded', event => {
var month = month
var amount = Object.values({{ month_data | tojson }});
var categories = amount.keys();

const ctx = document.getElementById('myChart');

new Chart(ctx, {
    type: 'bar',
    data: {
        labels: categories,
        datasets: [{
            label: 'Categories',
            data: amount,
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});