from packages.convert_dict import convert_dict
from packages.isPswdValid import is_valid_pswd
from packages.hash_pswd import hash_pswd,isPswdCorrect
department_mapping = {
    "media": "媒体运营部",
    "workshop": "翼工坊",
    "product": "产品经理与产品运营部",
    "tech": "技术研发部",
    "video": "音视频文化工作室",
    "HR": "行政人事部",# human resource
    "ER": "外宣部",  # external relationships
    "wechat": "微信推文部",
    "news": "新闻通讯社",
    "CPPR": "企划公关部",  # corporate planning and public relations
    "design": "设计部",
    "president": "主席团"
}

# 职位参数映射
role_in_depart_mapping = {
    4:"正主席/团支书",
    3:"分管主席",
    2:"正部长",
    1:"副部长",
    0:"干事"
}

role_in_depart_mapping_reverse = {
    "正主席/团支书":4,
    "分管主席":3,
    "正部长":2,
    "副部长":1,
    "干事":0
}
