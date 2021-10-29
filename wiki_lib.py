import requests

import config


def login(Session: requests.Session):
    "wiki登录函数"

    # 先检查是否已经登录同时获取登录令牌
    parms = {
        'format': 'json',
        'action': 'query',
        'meta': 'userinfo|tokens',
        'type': 'login',
    }

    response = Session.get(config.api_url, params=parms)
    data = response.json()

    # 已经登录则直接返回
    if data['query']['userinfo']['name'] == config.bot_username:
        print("已经登陆了！")
        return True

    login_token = data['query']['tokens']['logintoken']

    parms = {
        'format': 'json',
        'action': 'login',
        'lgname': config.bot_username,
        'lgpassword': config.bot_password,
        'lgtoken': login_token,
    }

    response = Session.post(config.api_url, data=parms)
    data = response.json()
    if data['login']['result'] == 'Success':
        print('Login successful!')
        return True
    else:
        print('Login failed!')
        print('错误信息：' + data['login']['result'])
        return None


def csrf_token(Session: requests.Session):
    "获取CSRF"
    parms = {
        "format": "json",
        "action": "query",
        "meta": "tokens",
    }

    response = Session.get(config.api_url, params=parms)
    data = response.json()

    print("已获取csrf。")
    return data['query']['tokens']['csrftoken']


def edit_token(Session: requests.Session, title: str):
    "获取编辑时所需的各种token和时间戳"
    ret = {}  # 存放数据的数组

    parms = {
        "format": "json",
        "curtimestamp": True,
        "action": "query",
        "titles": title,
        "meta": "tokens",
        "prop": "revisions",
        "rvprop": "timestamp",
        "rvlimit": 1
    }

    response = Session.get(config.api_url, params=parms)
    data = response.json()

    ret['csrf'] = data['query']['tokens']['csrftoken']
    ret['ctime'] = data['curtimestamp']

    # 遍历字典（其实就一个）获取页面信息
    for key in data['query']['pages']:
        ret['id'] = key
        ret['btime'] = data['query']['pages'][key]['revisions'][0]['timestamp']

    print('获取编辑信息成功！')
    return ret


def edit_section(Session: requests.Session, title: str, section: int, text: str, summary: str, minor: bool = False):
    "编辑页面指定段落"
    # 操作确认
    print('----------Confirm------------')
    print('Action: Edit section')
    print('Title:' + title)
    print('Section:' + str(section))
    print('Minor:' + str(minor))
    print('------------Text-------------')
    print(text)
    print('-----------Summary-----------')
    print(summary)
    print('-----------------------------')
    confirm = input('Confirm?(Y/N)')

    # 不确认则直接结束
    if confirm != "Y":
        print("Aborted, no changes have been made.")
        return False

    # 登录
    if not login(Session):
        return False

    data = edit_token(Session, title)

    # 执行编辑操作
    parms = {
        "format": "json",
        "action": "edit",
        "nocreate": True,
        "pageid": data['id'],
        "basetimestamp": data['btime'],
        "starttimestamp": data['ctime'],
        "watchlist": 'nochange',
        "section": section,
        "tags": "Bot",
        "text": text,
        "summary": summary,
        "token": data['csrf'],
    }
    if minor:
        parms['minor'] = True
    response = Session.post(config.api_url, data=parms)
    data = response.json()
    if 'edit' in data and data['edit']['result'] == 'Success':
        print("编辑已完成！")
        return True
    else:
        print("编辑失败！")
        print(data)
        return False


def check_page_exist(Session: requests.Session, title: str):
    "检查页面是否存在"
    parms = {
        "format": "json",
        "action": "query",
        "prop": "info",
        "titles": title,
    }

    response = Session.get(config.api_url, params=parms)
    data = response.json()

    # 遍历字典（其实就一个）获取页面信息
    for key in data['query']['pages']:
        return int(key)  # 无页面返回-1，否则返回页面id
    return -1


def get_section_id(Session: requests.Session, title: str, section_title: str):
    "根据段落标题获取段落id"
    parms = {
        "format": "json",
        "action": "parse",
        "prop": "sections",
        "page": title,
    }

    response = Session.get(config.api_url, params=parms)
    data = response.json()

    for val in data['parse']['sections']:
        if val['line'] == section_title:
            print("已获取段落id：" + str(val['index']))
            return int(val['index'])

    print(data)
    return -1


def get_wikitext(Session: requests.Session, title: str, section=None):
    "获取页面wikitext"
    parms = {
        "format": "json",
        "action": "parse",
        "prop": "wikitext",
        "page": title,
    }

    # 若指定段落
    if section:
        parms['section'] = section

    response = Session.get(config.api_url, params=parms)
    data = response.json()
    print("已获取wikitext。")
    return data['parse']['wikitext']['*']


def get_text(Session: requests.Session, title: str):
    "获取页面HTML"
    parms = {
        "format": "json",
        "action": "parse",
        "prop": "text",
        "page": title
    }

    response = Session.get(config.api_url, params=parms)
    data = response.json()
    return data['parse']['text']['*']


def new_section(Session: requests.Session, title: str, section_title: str, text: str, summary: str, minor: bool = False):
    "在指定页面添加新段落"
    # 操作确认
    print('----------Confirm------------')
    print('Action: Edit new section')
    print('Title:' + title)
    print('Section Title:' + section_title)
    print('Minor:' + str(minor))
    print('------------Text-------------')
    print(text)
    print('-----------Summary-----------')
    print(summary)
    print('-----------------------------')
    confirm = input('Confirm?(Y/N)')

    # 不确认则直接结束
    if confirm != "Y":
        print("Aborted, no changes have been made.")
        return False

    # 登录
    if not login(Session):
        return False

    data = edit_token(Session, title)

    # 执行编辑操作
    parms = {
        "format": "json",
        "action": "edit",
        "nocreate": True,
        "pageid": data['id'],
        "basetimestamp": data['btime'],
        "starttimestamp": data['ctime'],
        "watchlist": 'nochange',
        "section": 'new',
        "tags": "Bot",
        "sectiontitle": section_title,
        "text": text,
        "summary": summary,
        "token": data['csrf'],
    }
    if minor:
        parms['minor'] = True
    response = Session.post(config.api_url, data=parms)
    data = response.json()
    if 'edit' in data and data['edit']['result'] == 'Success':
        print("编辑已完成！")
        return True
    else:
        print("编辑失败！")
        print(data)
        return False
