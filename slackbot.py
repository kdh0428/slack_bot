# -*- coding: utf-8 -*-

import time,re,sys,urllib,urlparse,random,sympy,math
reload(sys)
sys.setdefaultencoding('utf-8')
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from bs4 import BeautifulSoup
from slackclient import SlackClient 



sc = SlackClient(token)
bot_alert_channel = "C02SG4F9V" 


def handler(message):
    print message
    try:
        type = message['type']
    except:
        return
    type_factory(type,message)
    
def message_handler(message):
    if not 'text' in message.keys():
        return
    text = message['text']
    channel = message['channel']
    match = re.findall(r"!(\S+)",message['text'])
    if not match:
        return

    command = match[0]
    args = text.replace("!%s" % command, '')
    command = command.lower()

    try:
        bot_command_factory[command](channel,args)
    except:
        pass


def youtube(channel,search):
    def youtube_random(hrefs):
        print hrefs
        return random.choice(hrefs)['href']
    def youtube_search(hrefs):
        return hrefs[0]['href']
    youtube_option = {
            'search' : youtube_search,
            'random' : youtube_random,
            }
    option = search.split(' ')[1] if search.split(' ')[1] in youtube_option.keys() else 'search'
    print search
    search = re.findall(r'".*"',search)
    print search
    if not search:
        sc.rtm_send_message(channel,'Usage: !youtube <search(default)/random> "찾는 영상(따옴표 안에 넣어주세요)"')
        return
    search = search[0]

    hrefs = youtube_parser(search)
    if not hrefs:
        sc.rtm_send_message(channel,'해당 주제의 영상이 없습니다')
    else:
        youtube_uri = "http://www.youtube.com"
        search_uri = youtube_uri+youtube_option[option](hrefs)
        sc.rtm_send_message(channel,search_uri)

def youtube_repeat(channel,search):
    youtube_repeat_uri = "http://listenonrepeat.com"
    search_uri = youtube_repeat_uri+youtube_search(search)
    sc.rtm_send_message(channel,search_uri)

def youtube_parser(youtube_topic):
    youtube_searh_uri = "http://www.youtube.com/results?search_query="
    request = urllib.urlopen(iriToUri(youtube_searh_uri+youtube_topic))
    search = BeautifulSoup(request)
    hrefs = search.find_all('a',href=True)
    video_hrefs = filter(lambda href: href['href']\
            if re.findall('watch',href['href']) else False,hrefs)
    #return random.choice(video_hrefs)['href'] 
    return video_hrefs

def init(message):
    sc.rtm_send_message(bot_alert_channel,'봇이 켜졌네?')


def type_factory(type,message):
    function = {
        "hello" : init,
        "message" : message_handler,
        }

    allowed_type = ['hello','message']
    if type in allowed_type:
        function[type](message)

def username2userid(name):
    return sc.server.users[name]

def call(channel,message):
    def precede(message):
        match = re.findall(r'@(\S+)[: ]',message)
        if not match:
            return message
        username = match[0].replace(':','')
        userid = username2userid(username)
        return message.replace('@{0}'.format(username),
                '<@{0}>'.format(userid))
    message = precede(message)
    print message
    sc.rtm_send_message(channel,message)

integers_regex = re.compile(r'\b[\d\.]+\b')

def calculate(expr, advanced=False):
   def safe_eval(expr, symbols={}):
       return eval(expr, dict(__builtins__=None), symbols)
   def whole_number_to_float(match):
       group = match.group()
       if group.find('.') == -1:
           return group + '.0'
       return group
   expr = expr.replace('^','**')
   expr = integers_regex.sub(whole_number_to_float, expr)
   if advanced:
       return safe_eval(expr, vars(math))
   else:
       return safe_eval(expr)

def calc(channel,message):
    message = message.strip()
    calc_result = calculate(message,True)
    print calc_result
    if calc_result:
        sc.rtm_send_message(channel,str(calc_result))
    else:
        sc.rtm_send_message(channel,"안해줘 돌아가")

def command_info(channel,message):
    sc.rtm_send_message(channel,"사용가능한 명령어는 %r 입니다" % bot_command_factory.keys())
  

bot_command_factory = {
        "command" : command_info,
        "youtube" : youtube,
        #"youtuberepeat" : youtube_repeat,
        #"imgur" : imgur_search,
        #"call" : call,
        "calc" : calc,
        }

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

if sc.rtm_connect():
    while True:
        for message in sc.rtm_read():
            handler(message)
        time.sleep(1)

   
