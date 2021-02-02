from enum import Enum

class Signup:
  def __init__(self, role, memberID, isRequired):
    self.role = role
    self.memberID = memberID
    self.isRequired = isRequired


class Role(Enum):
  Tank = 1
  Healer = 2
  DD = 3
  Runner = 4
  Reserve = 5



  @classmethod
  def GetPrettyString(cls, value):
    if(value in PrettyStringDic):
      return PrettyStringDic[value]
    else:
      return "Unknown"

  @classmethod
  def GetEmoji(cls, value):
    if value in EmojiDic:
      return EmojiDic[value]
    else:
      return '❌'

  @classmethod
  def GetRoleFromEmoji(cls, value):
    return next((k for k,v in EmojiDic.items() if v == value), None)
    
  @classmethod
  def IsRoleEmoji(cls, value):
    return (value in EmojiDic.values())

PrettyStringDic = {
  Role.Tank: "Tank", 
  Role.Healer: "Healer", 
  Role.DD: "DD", 
  Role.Runner: "Runner/Portals",
  Role.Reserve: "Reserve"}

EmojiDic = {
  Role.Tank: '🛡️',
  Role.Healer: '🚑',
  Role.DD: '⚔',
  Role.Runner: '🏃',
  Role.Reserve: '⏲️'}

