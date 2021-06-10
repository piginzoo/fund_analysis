//各页面的输入输出参数项
page_param_json = {
    "idcard.ocr.v1": {
        "title": "身份证识别",
        "url": "/idcard/ocr.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            }
        ],
        "output_type": "idcard",
        "output": {}
    },
    "case.compare": {},
    "case.diff": {
        "title": "两case比较",
        "url": "/case/diff.ajax",
        "input": [
            {
                "name": "flow_no1",
                "name_zh": "流水号1",
                "type": "input",
            },
            {
                "name": "flow_no2",
                "name_zh": "流水号2",
                "type": "input",
            },
            {
                "name": "show_diff_only",
                "name_zh": "只展示不同",
                "type": "bool",
                "default": false
            }
        ],

        "output_type": "text",
        "output": {}
    },
    "demo.query": {
        "title": "Demo结果查询",
        "url": "/case/demo/query.ajax",
        "input": [
            {
                "name": "case_type",
                "name_zh": "用例类型",
                "type": "select",
                "value": case_type_config
            },
            {
                "name": "ip_address",
                "name_zh": "调用用户IP",
                "type": "input",
            }
        ],
        "output_type": "text",
        "output": {}
    },
}
//"output_type": "text_only"

var g_page_type = "ocr"

function init_page(page_type) {
    var page_param = page_param_json[page_type]
    init_query_page('toolbar', page_param)
    if (page_param.title) {
        $("#result_title").html(page_param.title)
    }
    $("#request_url").html("请求url：" + page_param.url)
}

function init_image(image_id, image_name) {
    $("#" + image_id).change(function () {
        var v = $(this).val();
        var reader = new FileReader();
        reader.readAsDataURL(this.files[0]);
        reader.onload = function (e) {
            var result = reader.result.split(",")[1]
            $("input[name='" + image_name + "']").val(result)
        };
    });
}


function submit_ocr() {
    //清空
    $("#small_table  tr:not(:first)").empty("");
    $("#big_image").attr("src", "")

    var page_param = page_param_json[g_page_type]
    var param = get_query_param(page_param)
    param['do_verbose'] = true
    param['sid'] = 'page_sid'

    $.ajax({
        url: page_param.url,
        type: 'post',
        dataType: 'json',
        contentType: "application/json",
        data: JSON.stringify(param),
        success: function (res) {
            if ('9999' === res.code) {
                alert(res.message)
                $('#result_json').html(syntaxHighlight(res));
                return
            }
            // 成功处理逻辑
            load_result(res)
        },
        error: function (res) {
            // 错误时处理逻辑
            //debugger
        }
    });
}


function load_result(result) {
    var output_type = page_param_json[g_page_type].output_type
    // #TODO 输出格式不同，如何做到统一。
    if ("text" == output_type) {
        $("#detail").html(result)
        return
    } else {
        alert("程序有异常，需要制定展示方式！")
    }
    //展示json
    delete result['debug_info']
    $('#result_json').html(syntaxHighlight(result));
}

function syntaxHighlight(json) {
    if (typeof json != 'string') {
        json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
        function (match) {
            var cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        }
    );
}

function get_case_compare_param() {
    var case_type_param = {
        "name": "case_type",
        "name_zh": "用例类型",
        "type": "select",
        "value": {}
    }
    var channel_param = {
        "name": "channel",
        "name_zh": "测试渠道",
        "type": "select",
        "parent_node": "case_type",
        "value": {}
    }
    var data_type_param = {
        "name": "data_type_list",
        "name_zh": "数据类型",
        //多选框
        "type": "multi_select",
        "is_array": true,
        "parent_node": "case_type",
        "value": {}
    }
    var field_list_param = {
        "name": "field_list",
        "name_zh": "比较字段",
        //多选框
        "type": "multi_select",
        "is_array": true,
        "parent_node": "case_type",
        "value": {}
    }
    var prob_list_param = {
        "name": "prob_list",
        "name_zh": "概率筛选",
        //多选框
        "type": "multi_select",
        "is_array": true,
        "value": {
            '1': '认为正确',
            '2': '需要确认',
            '3': '认为错误',
        }
    }
    var show_diff_param = {
        "name": "show_diff_only",
        "name_zh": "只展示不同",
        "type": "bool",
    }
    var extra_param_list = []
    for (var key in case_all_config) {
        var item = case_all_config[key]
        // item = case_all_config.vrc
        case_type_param.value[key] = item.name_ch
        channel_param.value[key] = item.channel
        data_type_param.value[key] = item.data_list
        field_list_param.value[key] = item.field_list
        var field_map = item.field_map
        if (field_map != undefined && field_map != null) {
            for (var p_name in field_map) {
                var parent_value = item.field_list[p_name]
                var p_value = field_map[p_name]
                var extra_value = {}
                extra_value[p_name] = p_value
                var extra_param = {
                    "name": p_name + "_detail",
                    "name_zh": parent_value + "详情",
                    //多选框
                    "type": "multi_select",
                    "is_array": true,
                    "parent_node": "field_list",
                    "value": extra_value
                }
                extra_param_list.push(extra_param)
            }
        }
    }

    var case_compare_param = {
        "title": "用例正确率测试",
        "url": "/case/compare.ajax",
        "input": [],
        "output_type": "text",
        "output": {}
    }
    case_compare_param.input.push(case_type_param)
    case_compare_param.input.push(channel_param)
    case_compare_param.input.push(data_type_param)
    case_compare_param.input.push(field_list_param)
    case_compare_param.input = case_compare_param.input.concat(extra_param_list)
    case_compare_param.input.push(prob_list_param)
    case_compare_param.input.push(show_diff_param)
    return case_compare_param
}

function init_main(name) {
    g_page_type = name
    page_param_json["case.compare"] = get_case_compare_param()
    init_page(g_page_type)
    $('#submit_ocr').click(function () {
        return submit_ocr();
    });
}

function init_case_diff(flow_no1, flow_no2) {
    init_main('case.diff')
    $("input[name='flow_no1']").val(flow_no1)
    $("input[name='flow_no2']").val(flow_no2)
    submit_ocr()
}


$(document).ready(function () {
    $("body").on("click", ".select_ip_address", function () {
            let ip_value = $(this).text();
            $("input[name='ip_address']").val(ip_value)
            submit_ocr()
        }
    );
    $("body").on("click", "#clear_address_btn", function () {
            // 清空并返回
            $("input[name='ip_address']").val("")
            submit_ocr()
        }
    );

});
// a = ["123", "456"]
// a = [{"img": "123"}, {"img": "456"}]

