fund_c_names=\
['易方达蓝筹精选',
'易方达中小盘',
'易方达消费行业',
'易方达科翔',
'易方达行业领先',
'易方达安心回报A',
'广发稳健增长A',
'广发创新升级',
'广发多策略',
'汇添富全球移动互联',
'汇添富价值精选A',
'汇添富创新医药',
'汇添富成长焦点',
'华夏回报A',
'华夏移动互联人民币',
'富国消费主题A',
'富国天惠精选成长A',
'富国高新技术产业',
'南方科技创新A',
'南方绩优成长A',
'嘉实泰和',
'嘉实新消费',
'中欧医疗健康A',
'中欧时代先锋A',
'中欧新蓝筹A',
'中欧行业成长A',
'中欧价值发现A',
'兴全趋势投资',
'兴全合润',
'兴全合宜A',
'兴全商业模式优选',
'景顺长城鼎益',
'景顺长城优选',
'景顺长城核心竞争力A',
'景顺长城动力平衡',
'交银新生活力',
'交银新成长',
'交银阿尔法',
'鹏华养老产业',
'鹏华研究精选',
'华安升级主题',
'工银瑞信文体产业A',
'工银瑞信金融地产A',
'工银瑞信医疗保健行业',
'东方红睿满沪港深',
'银华盛世精选',
'银华富裕主题',
'泓德远见回报',
'泓德优选成长',
'前海开源国家比较优势A',
'民生加银策略精选A',
'上投摩根科技前沿',
'万家行业优选',
'农银汇理研究精选']

from fund_analysis.tools.data_utils import load_fund_list

from Levenshtein import distance

funds = load_fund_list()

result = {}
name_map = {}
for fund in funds:
    for fund_c_name in fund_c_names:
        if distance(fund.name,fund_c_name)<=4:
            if result.get(fund_c_name,None):
                print(fund_c_name,"已经有了code：",result[fund_c_name])
            else:
                print(">> ",fund_c_name,"=>",fund.name," : ",fund.code)
                result[fund_c_name] = fund.code
                name_map[fund_c_name] = fund.name

for fund_c_name in fund_c_names:
    code = result.get(fund_c_name,'')
    fund_name = name_map.get(fund_c_name, '')
    print(fund_c_name,'=>',fund_name,',',code)
    # print(str(code))

# python -m test.test_get_fund_code
