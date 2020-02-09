function gen_chart_option(dataset_source,
                          title,
                          series,
                          extra_options = {},
                          tooltip = {
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

function gen_line_series(encode_x, encode_y, extra_params) {
    let rt_dict = {
        type: 'line',
        encode: {x: encode_x, y: encode_y},
        smoothMonotone: 'x',
        lineStyle: {
            width: 3
        },
        sampling: 'average',
    };

    for (let key in extra_params) rt_dict[key] = extra_params[key];

    return rt_dict;
}

function gen_map_series(encode_x, encode_y) {
    return {
        type: 'map',
        map: 'china',
    };
}


export function draw_all_charts() {


    let chart_infected = echarts.init(document.getElementById('infected'), 'main_theme');
    let chart_sceptical = echarts.init(document.getElementById('sceptical'), 'main_theme');
    let chart_death = echarts.init(document.getElementById('death'), 'main_theme');
    let chart_cured = echarts.init(document.getElementById('cured'), 'main_theme');
    let chart_total = echarts.init(document.getElementById('total'), 'main_theme');

    let host = window.location.host;
    let request_loc = 'http://api.' + host + '/get_history';

    $.getJSON(request_loc, (return_data) => {

        console.log(return_data['data']);

        let option_i = gen_chart_option(return_data['data'], 'Infected | 确诊',
            [gen_line_series('time', 'infected', {color: color_list[0]})]);
        let option_d = gen_chart_option(return_data['data'], 'Death | 死亡',
            [gen_line_series('time', 'death', {color: color_list[2]})]);
        let option_s = gen_chart_option(return_data['data'], 'Sceptical | 疑似',
            [gen_line_series('time', 'sceptical', {color: color_list[1]})]);
        let option_c = gen_chart_option(return_data['data'], 'Cured | 治愈',
            [gen_line_series('time', 'cured', {color: color_list[4]})]);


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

        chart_infected.setOption(option_i);
        chart_sceptical.setOption(option_s);
        chart_death.setOption(option_d);
        chart_cured.setOption(option_c);
        chart_total.setOption(option_total);
    })
}