#TODO
#

import json
import os

from ..ybdata import (Clan_group,User)
from .exception import (ClanBattleError, GroupError, GroupNotExist, InputError,
                        UserError, UserNotInGroup)                        

path = os.path.dirname(os.path.abspath(__file__))

# dict多层更新方法
def dict_update(raw, new):
    dict_update_iter(raw, new)
    dict_add(raw, new)
    
def dict_update_iter(raw, new):
    for key in raw:
        if key not in new.keys():
            continue
        if isinstance(raw[key], dict) and isinstance(new[key], dict):
            dict_update(raw[key], new[key])
        else:
            raw[key] = new[key]

def dict_add(raw, new):
    update_dict = {}
    for key in new:
        if key not in raw.keys():
            update_dict[key] = new[key]
    raw.update(update_dict)
                   
# 读取设置
def rLoadSettings(group_id=None, key=None):
    '''
    returns:
        无参返回全部，有参返回键值
    '''
    with open(f'{path}/r_settings.json', 'r') as f:
            settings = json.load(f)
    if not group_id:
        return settings
    else:
        try:
            return settings[str(group_id)][key]
        except:
            print('获取不到额外设置')
            return None

# 保存设置        
def rSaveSettings(group_id:int, key:str, value:any):
    group = Clan_group.get_or_none(group_id)
    if group is None:
        raise GroupNotExist
    group_id = str(group_id)
    settings = rLoadSettings()
    new = {
            group_id: {
                key: value
            }
        }
    dict_update(settings, new)
    with open(f'{path}/r_settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

# 读取申请出刀数据
def rLoadChallenge(group_id=None):
    '''
    returns:
        无参返回全部，
        有参返回[0]id列表[1]备注列表
    '''
    with open(f'{path}/r_data_challenging.json', 'r') as f:
            data = json.load(f)
    if not group_id:
        return data    
    elif str(group_id) not in data:
        return {}.keys(),{}.values()
    else:
        info = data[str(group_id)]
        return info.keys(),info.values()

# 申请出刀
def rApplyForChallenge(group_id:int, qqid:int, extra_msg:str=None):
    '''
    args:
        group_id: group id
        qqid: qq id
        extra_msg: message
    returns:
        [0]msg: apply result
        [1]qqid: to query nickname
    '''
    # 检查
    group = Clan_group.get_or_none(group_id)
    if group is None:
        raise GroupNotExist
    user = User.get_or_none(qqid=qqid, clan_group_id=group_id)
    if user is None:
        raise UserNotInGroup
    # 检查是否已锁定 昵称由battle.py获取
    if group.boss_lock_type == 2 and group.challenging_member_qq_id:
        msg = f'申请失败，boss被锁定\n留言：{group.challenging_comment}'
        return msg,group.challenging_member_qq_id
    group_id = str(group_id)
    data = rLoadChallenge()
    # 检查是否重复申请
    if group_id in data and str(qqid) in data[group_id]:
        return '您已在挑战boss，请勿重复申请',None
    if not extra_msg:
        extra_msg = ""
    new = {
            group_id:{
                str(qqid):extra_msg
            }
        }    
    dict_update(data, new)
    with open(f'{path}/r_data_challenging.json', 'w') as f:
        json.dump(data, f, indent=4)
    return '申请成功',qqid
    
# 删除申请
def rCancleChallenge(group_id, qqid=None):
    group_id = str(group_id)
    data = rLoadChallenge()
    # 删除单个与删除全部
    if qqid and str(qqid) in data[group_id]:
        del data[group_id][str(qqid)]
    elif not qqid and group_id in data:
        del data[group_id]  
    with open(f'{path}/r_data_challenging.json', 'w') as f:
        json.dump(data, f, indent=4)

# 更新申请
def rUpdateForChallenge(group_id, qqid, message):
    group_id = str(group_id)
    qqid = str(qqid)
    data = rLoadChallenge()
    if group_id in data and qqid in data[group_id]:
        new = {
            group_id:{
                qqid:message
            }
        }
        dict_update(data, new)
        with open(f'{path}/r_data_challenging.json', 'w') as f:
            json.dump(data, f, indent=4)
        return '更新出刀成功'
    else:
        return '尚未申请出刀'