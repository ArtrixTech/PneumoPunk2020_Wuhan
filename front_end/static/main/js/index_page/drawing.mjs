function gen_chart_option(dataset_source,
                          title,
                          series,
                          extra_options = {}, tooltip = {
        trigger: 'axis',
        axisPointer: {
            type: 'line'
        }
    }) {

    let option = {
        dataset: {source: dataset_source},
        title: {
            text: title,
            textStyle: {
                color: '#4a4a4a',
                fontFamily: 'alibold',
            }
        },
        tooltip: tooltip,
        dataZoom: [{
            type: 'inside',
            filterMode: 'weakFilter',
            //startValue: return_data['start_time']
        }],
        xAxis: {
            type: 'time',
            scale: true,
            min: function (value) {
                return value.min - 1000;
            },
            max: function (value) {
                return value.max + 1000;
            },
        },
        yAxis: {
            min: function (value) {
                let v = value.min - ((value.max - value.min) * 0.1).toFixed(0);
                return v >= 0 ? v : 0;
            },
        },
        series: series
    };
    for (let key in extra_options) option[key] = extra_options[key];
    return option;

}

function gen_line_series(encode_x, encode_y) {
    return {
        type: 'line',
        encode: {x: encode_x, y: encode_y},
        smoothMonotone: 'x',
        lineStyle: {
            width: 3
        },
        sampling: 'average',
    };
}


export function draw_all_charts() {


    let chart_infected = echarts.init(document.getElementById('infected'), 'main_theme');
    let chart_sceptical = echarts.init(document.getElementById('sceptical'), 'main_theme');
    let chart_death = echarts.init(document.getElementById('death'), 'main_theme');
    let chart_cured = echarts.init(document.getElementById('cured'), 'main_theme');
    let chart_total = echarts.init(document.getElementById('total'), 'main_theme');

    $.getJSON('/get_history', (return_data) => {

        console.log(return_data['data']);

        let test_opt = gen_chart_option(return_data['data'], 'Test',
            [gen_line_series('time', 'infected')]);


        let option_i = {
            dataset: {source: return_data['data']},
            title: {
                text: 'Infected | 感染',
                textStyle: {
                    color: '#4a4a4a',
                    fontFamily: 'alibold',
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'line'
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    filterMode: 'weakFilter',
                    startValue: return_data['start_time']
                },

            ],
            xAxis: {
                type: 'time',
                scale: true,
                min: function (value) {
                    return value.min - 1000;
                },
                max: function (value) {
                    return value.max + 1000;
                },
            },
            yAxis: {
                min: function (value) {
                    let v = value.min - ((value.max - value.min) * 0.1).toFixed(0);
                    return v >= 0 ? v : 0;
                },
            },
            series: [{
                type: 'line', encode: {x: 'time', y: 'infected'}, smoothMonotone: 'x', lineStyle:
                    {
                        width: 3
                    }
            }]
        };
        console.log(option_i)
        let option_s = {
            dataset: {source: return_data['data']},
            title: {
                text: 'Sceptical | 疑似',
                textStyle: {
                    color: '#4a4a4a',
                    fontFamily: 'alibold',
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'line'
                }
            },
            xAxis: {
                type: 'time',
                scale: true,
                min: function (value) {
                    return value.min - 1000;
                },
                axisLine: {onZero: false},
                max: function (value) {
                    return value.max + 1000;
                },
            },
            yAxis: {
                min: function (value) {
                    let v = value.min - ((value.max - value.min) * 0.1).toFixed(0);
                    return v >= 0 ? v : 0;
                },
            },
            series: [
                {
                    type: 'line', encode: {x: 'time', y: 'sceptical'}, smoothMonotone: 'x', itemStyle: {
                        color: color_list[1]
                    }, lineStyle: {
                        width: 3
                    }
                }

            ]
        };

        let option_d = {
            dataset: {source: return_data['data']},
            title: {
                text: 'Death | 死亡',
                textStyle: {
                    color: '#4a4a4a',
                    fontFamily: 'alibold',
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'line'
                }
            },
            xAxis: {
                type: 'time',
                min: function (value) {
                    return value.min - 1000;
                },
                max: function (value) {
                    return value.max + 1000;
                },
            },
            yAxis: {
                min: function (value) {
                    let v = value.min - ((value.max - value.min) * 0.1).toFixed(0);
                    return v >= 0 ? v : 0;
                },
            },
            series: [
                {
                    type: 'line', encode: {x: 'time', y: 'death'}, smoothMonotone: 'x', itemStyle: {
                        color: color_list[2]
                    }, lineStyle: {
                        width: 3
                    }
                }

            ]
        };

        let option_c = {
            dataset: {source: return_data['data']},
            title: {
                text: 'Cured | 治愈',
                textStyle: {
                    color: '#4a4a4a',
                    fontFamily: 'alibold',
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'line'
                }
            },
            xAxis: {
                type: 'time',
                scale: true,
                min: function (value) {
                    return value.min - 1000;
                },
                max: function (value) {
                    return value.max + 1000;
                },
            },
            yAxis: {
                min: function (value) {
                    let v = value.min - ((value.max - value.min) * 0.1).toFixed(0);
                    return v >= 0 ? v : 0;
                },
            },
            series: [
                {
                    type: 'line', encode: {x: 'time', y: 'cured'}, smoothMonotone: 'x', itemStyle: {
                        color: color_list[3],
                    }, lineStyle: {
                        width: 3
                    }
                },
            ]
        };


        let option_total = {
            dataset: {source: return_data['data']},
            title: {
                text: 'Total | 综合',
                textStyle: {
                    color: '#4a4a4a',
                    fontFamily: 'alibold',
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'line'
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    filterMode: 'weakFilter',
                    startValue: return_data['start_time']
                },

            ],

            xAxis: {
                type: 'time'
            },
            yAxis: {
                min: function (value) {
                    let v = value.min - ((value.max - value.min) * 0.1).toFixed(0);
                    return v >= 0 ? v : 0;
                },
            },
            series: [
                {
                    name: '感染',
                    type: 'line',
                    encode: {x: 'time', y: 'infected'},
                    smoothMonotone: 'x',
                    lineStyle: {
                        width: 3
                    }
                },
                {
                    name: '疑似',
                    type: 'line',
                    encode: {x: 'time', y: 'sceptical'},
                    smoothMonotone: 'x',
                    lineStyle: {
                        width: 3
                    }
                },
                //{type: 'line', encode: {x: 'time', y: 'death'}, smoothMonotone: 'x'},
                //{type: 'line', encode: {x: 'time', y: 'cured'}, smoothMonotone: 'x'},
            ]
        };

        chart_infected.setOption(test_opt);
        chart_sceptical.setOption(option_s);
        chart_death.setOption(option_d);
        chart_cured.setOption(option_c);
        chart_total.setOption(option_total);
    })
}