import redis
from readConfig import ReadConfig

HOST = ReadConfig().redis_host()
PWD = int(ReadConfig().redis_password())
# print(HOST,type(HOST), PWD,type(PWD))

pool = redis.ConnectionPool(host=HOST, port=6379, db=3, password=PWD, encoding='utf-8')
conn = redis.Redis(connection_pool=pool)


class DbOperate:
    def add(self, db, elem):
        if isinstance(elem, list):
            for el in elem:
                res = conn.sadd(db, el)
                print(res, el)
        if isinstance(elem, str):
            res = conn.sadd(db, elem)
            print(res, elem)

    def del_elem(self, db, elem):
        return conn.srem(db, elem)

    def get_length(self, db):
        return conn.scard(db)

    def is_member(self, db, elem):
        return conn.sismember(db, elem)

    def push(self, key, elem):
        if isinstance(elem, list):
            for el in elem:
                res = conn.sadd(key, el)
                print(res, el)
        if isinstance(elem, str):
            res = conn.sadd(key, elem)
            print(res, elem)
        if isinstance(elem, int):
            res = conn.sadd(key, elem)
            print(res, elem)

    def exists(self, key):
        return conn.scard(key)


def patent(res):
    # 专利
    keys_3 = ["patent_recheck", "patent_answer", "patent_warrant", "patent_stable"]
    keys_2 = ["patent_evaluate", "patent_clue", "patent_public"]
    keys_7 = ["patent", "utility", "oneday"]
    keys_6 = ["design"]
    patent_common = [u'PCT国际申请', u'电商侵权处理', u'专利权恢复', u'代缴专利年费', u'专利实施许可备案',
                     u'专利质押备案', u'集成电路布图设计']
    # res.add(trademark_db, patent_common)
    description_key = [[1, 2, 3], [1, 2], [1, 3], [2, 3], [1], [2], [3]]

    for key in keys_3:
        res.push(key, [num for num in range(1, 4)])

    for key in keys_2:
        res.push(key, [num for num in range(1, 3)])

    for key in keys_6:
        res.push(key, [num for num in range(1, 7)])

    for key in keys_7:
        res.push(key, [num for num in range(1, 8)])

    res.push("description", description_key)


def copyright(res):
    # 版权
    keys = ["computer", "art", "word", "compile", "photography", "music", "drama", "film"]
    values_6 = [1, 2, 3, 4, 5, 6]
    for key in keys:
        pp = res.push(key, values_6)

def trademark(res):
    trademark_db = "case"
    trademark_international = [u'美国商标注册', u'日本商标注册', u'韩国商标注册', u'台湾商标注册', u'香港商标注册',
                               u'德国商标注册', u'欧盟商标注册', u'马德里国际商标', u'非洲知识产权组织']

    trademark_national = [u'专属顾问注册', u'专属加急注册', u'专属双享注册', u'专属担保注册']

    trademark_common = [u'申请商标更正', u'出具商标注册证明申请', u'补发商标注册证申请', u'商标转让', u'商标注销',
                        u'商标变更', u'商标诉讼', u'证明商标注册', u'集体商标注册', u'驰名商标认定']

    test = [u'商标驳回复审', u'商标无效', u'商标续展', u'商标许可备案', u'商标异议', u'商标撤销']
    test2 = [u'商标撤销', u'商标异议', u'商标许可备案', u'商标续展', u'商标许可备案']
    res.add(trademark_db, u'商标驳回复审')
    for elem in [trademark_international, trademark_common, test, test2, trademark_national]:
        res.add(trademark_db, elem)
    print(res.get_length(trademark_db))


def clue(res):
    clue_db = "clue"

    clue_1_1 = [u'专利布局规划', u'研发立项支持', u'竞争对手监测', u'高价值专利培育', u'专利价值评估', u'专利尽职调查', u'专利侵权诉讼', u'优先审查', u'海外专利流程管理',
                u'知识产权海关备案', u'植物新品种']
    clue_1_2 = [u'新产品风险预警(FTO)', u'侵权风险分析', u'行业专利导航']
    clue_1_3 = [u'无效证据检索', u'专利无效宣告', u'专利无效答辩']
    clue_1_4 = [u'海外国家专利申请-其他国家', u'海外国家专利申请']
    clue_2 = [u'logo设计']
    clue_5 = [u'双软认证', u'ISO9001质量管理体系认证', u'软件产品登记测试报告', u'科技成果评价', u'贯标申请服务', u'知识产权保护', u'专利风险预警', u'专利侵权对抗',
              u'无效/异议提起', u'合同审核', u'知识产权维权', u'咨询分析报告', u'知识产权运营', u'知识产权顾问']
    clue_5_1 = [u'软件开发']

    for clue_type in [clue_1_1, clue_1_2, clue_1_3, clue_1_4, clue_2, clue_5, clue_5_1]:
        res.add(clue_db, clue_type)


if __name__ == "__main__":
    res = DbOperate()
    # 商标
    # trademark(res)

    # 专利
    # patent(res)

    # 版权
    # copyright(res)

    # 线索
    clue(res)