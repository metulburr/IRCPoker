import sys
import socket
import string
import time, os
import random
#import crapdealer_commands
#import imp
from card_game import Poker


    

argv_flag = {'-c':None, '-h':None, '-p':None, '-k':None}
flag_help = {'-c':'channel ',
             '-h':'host',
             '-p':'port',
             '-k':'character to call on bot'}
show_help = 'Icorrect argument, "{} -help" for help'.format(sys.argv[0])

def cmd_arg():
    '''return IrcBot object based on values supplied by sys.argv'''
    arguments = sys.argv
    if len(sys.argv) == 1:
        connect = IrcBot()
    elif len(sys.argv) == 2:
        if sys.argv[1] == '-help':
            print('')
            for key in flag_help.keys():
                print('\t{0} -- {1}'.format(key, flag_help[key]))
            sys.exit()
        else:
            print(show_help)
    else:
        h, p, c , k = None, None, None, None
        for flag in argv_flag.keys():
            for user_flag in arguments:
                if flag == user_flag:
                    index = arguments.index(user_flag)
                    value = arguments[index + 1]
                    argv_flag[flag] = value
        connect = IrcBot(h=argv_flag['-h'], p=argv_flag['-p'], c=argv_flag['-c'],
                          k=argv_flag['-k'])
    return connect

class IrcBot:
    def __init__(self, h=None, p=None, c=None, k=None):
        '''adjust values based on sys.argv'''
        if h is None:
            self.host = "irc.freenode.net"
        else:
            self.host = h
        if p is None:
            self.port = 6667
        else:
            self.port = p
        if c is None:
            self.channel = '#robgraves'
        else:
            if c[:1] != '#':
                c = '#'+c
            self.channel = c
        if k is None:
            self.contact = ':'
        else:
            self.contact = k
            
        self.nick = "Texas_Hold_Em"
        self.ident = "MetulBot"
        self.realname = "MetulBot"
        self.list_cmds = {
            'help':(lambda:self.help()),
            'lick':lambda:self.lick(),
            'join':lambda:self.joingame(),
            'players':lambda:self.players(),
            'deal':lambda:self.deal(),
            'table':lambda:self.table(),
            'showhands':lambda:self.showhands(),
            'flop':lambda:self.flop(),
            'turn':lambda:self.turn(),
            'river':lambda:self.river(),
            'newhand':lambda:self.newhand(),
            'fold':lambda:self.fold(),
            'check':lambda:self.check(),
            'call':lambda:self.call(),
            'raise':lambda:self.raises(),
            'bet':lambda:self.bet()
            }
        
        self.op = ['metulburr','Awesome-O', 'robgraves','corp769',
                  'metulburr1', 'robgravesny', 'Optichip', 'Craps_Dealer']
        self.data = None
        self.operation = None
        self.addrname = None
        self.username = None
        self.text = None
        self.timer= None
        
        self.game = Poker()
        
        
        self.sock = self.irc_conn()
        self.wait_event()
        
    def irc_conn(self):
        '''connect to server/port channel, send nick/user '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('connecting to "{0}/{1}"'.format(self.host, self.port))
        sock.connect((self.host, self.port))
        print('sending NICK "{}"'.format(self.nick))
        sock.send("NICK {0}\r\n".format(self.nick).encode())
        sock.send("USER {0} {0} bla :{0}\r\n".format(
            self.ident,self.host, self.realname).encode())
        print('joining {}'.format(self.channel))
        sock.send(str.encode('JOIN '+self.channel+'\n'))
        return sock
    
    def say(self, string):
        '''send string to irc channel with PRIVMSG '''
        self.sock.send('PRIVMSG {0} :{1}\r\n'.format(self.channel, string).encode())
    
    def send_operation(self, operation=None, msg=None, username=None):
        '''send operation to irc with operation arg'''
        if msg is None:
            #send ping pong operation
            self.sock.send('{0} {1}\r\n'.format(operation, self.channel).encode())
        elif msg != None:
            #send private msg to one username
            self.sock.send('PRIVMSG {0} :{1}\r\n'.format(self.username,msg).encode())
    def get_user(self, stringer):
        start = stringer.find('~')
        end = stringer.find('@')
        user = stringer[start +1:end]
        return user
        
    def format_data(self):
        '''get data from server:
        self.operation = EXAMPLE: PRIVMSG, JOIN, QUIT
        self.text = what each username says
        self.addrname = the first name on address
        self.username = the username
        self.timer = time 
        '''
        data=self.sock.recv(1042) #recieve server messages
        data = data.decode('utf-8') #data decoded
        self.data = data.strip('\n\r') #data stripped
        try:
            self.operation = data.split()[1]
            textlist = data.split()[3:]
            text = ' '.join(textlist)
            self.text = text[1:]
            self.addrname = self.get_user(data) 
            self.username = data[:data.find('!')][1:]
        except IndexError:
            pass
        self.timer = time.asctime(time.localtime(time.time()))
        
    def print_console(self):
        '''print to console '''
        #print('{0} ({1}): {2}'.format(self.username, self.timer, self.text))
        print(self.data)
        
    def ping_pong(self):
        '''server ping pong handling'''
        try:
            if self.data[:4] == 'PING':
                self.send_operation('PONG')
        except TypeError: #startup data
            pass
        
    def upon_join(self):
        '''when someone joins the channel'''
        if self.operation == 'JOIN':
            pass
    
    def upon_leave(self):
        '''when someone leaves the channel'''
        if self.operation == 'QUIT' or self.operation == 'PART':
            pass
        
    def test(self):
        try:
            pass
            #self.say('self.data is: {}'.format(self.data))
            #self.say('self.operation is: {}'.format(self.operation))
            #self.say('self.addrname is: {}'.format(self.addrname))
            #self.say('self.username is: {}'.format(self.username))
            #self.say('self.text is: {}'.format(self.text))
            #self.say('self.timer is: {}'.format(self.timer))
        except:
            pass
        
    def wait_event(self):
        #time.sleep(10) #wait to connect before starting loop
        while True:
            self.ping_pong()
            self.format_data()
            self.print_console()
            self.upon_join()
            self.upon_leave()
            self.check_cmd()
            
    def not_cmd(self, cmd):
        return '{0}: "{1}" is not one of my commands'.format(self.username, cmd)

    def check_cmd(self):
        '''check if contact is first char of text and send in cmd and its args to crapdealer_commands.commands'''
        if self.text[:1] == self.contact:
            
            
            #imp.reload(crapdealer_commands)
            #returner = crapdealer_commands.commands(self.text.split()[0][1:], self.text.split()[1:])
            returner = self.commands(self.text.split()[0][1:], self.text.split()[1:])
            if returner != None:
                self.say(returner)

    def commands(self, cmd, *args):
        try:
            arg1 = args[0][0]
        except IndexError:
            arg1 = ''
        try:
            arg2 = args[0][1]
        except IndexError:
            arg2 = ''

        if cmd in self.list_cmds:
            if not arg1: #if no arguments
                self.list_cmds[cmd]()
            else: #argument with function, run function directly
                if cmd == 'help':# and arg1 in self.list_cmds.keys():
                    self.help(arg1)
                elif cmd == 'bet':
                    try:
                        arg1 = int(arg1)
                        self.bet(arg1)
                    except:
                        pass
                elif cmd == 'raise':
                    try:
                        arg1 = int(arg1)
                        self.raises(arg1)
                    except:
                        pass
                elif arg1 not in self.list_cmds:
                    self.say(self.not_cmd(arg1))
                    
            #self.say('cmd is: {}'.format(cmd))
            #self.say('first two args are: {0} {1}'.format(arg1, arg2))
        elif cmd != '':
            self.say(self.not_cmd(cmd))
            
    def help(self, arg=None):
        helper = '{0}: {1}help  --show all commands'.format(self.username,self.contact)
        lick = '{0}: {1}lick  -- +1 to times licked'.format(self.username,self.contact)
        deal = '{0}: {1}deal  -- deal 2 cards to each player after everyone has joined'.format(self.username,self.contact)
        table = '{0}: {1}table  -- view cards on table'.format(self.username,self.contact)
        join = '{0}: {1}join  -- join the Poker game (while a game is not in progress)'.format(self.username,self.contact)
        newhand = '{0}: {1}newhand  -- reset table, players hand, after each hand'.format(self.username,self.contact)
        turn = '{0}: {1}turn  -- flip the turn card (4th card)'.format(self.username,self.contact)
        flop = '{0}: {1}flop  -- flip the first 3 cards of each hand'.format(self.username,self.contact)
        river = '{0}: {1}river  -- flip the river card (5th and final card)'.format(self.username,self.contact)
        players = '{0}: {1}players  -- show each player in the game and their bankroll'.format(self.username,self.contact)
        fold = '{0}: {1}fold  -- fold your hand)'.format(self.username,self.contact)
        
        check = '{0}: {1}check  -- match previous bet when no bet is made)'.format(self.username,self.contact)
        call = '{0}: {1}call  -- match previous bet made)'.format(self.username,self.contact)
        raises = '{0}: {1}raise [amount] -- after a bet is made raise the bet by [amount])'.format(self.username,self.contact)
        bet = '{0}: {1}bet [amount]  -- if no bet is made the option to bet with [amount])'.format(self.username,self.contact)
        
        if arg is None:
            tmp = []
            for key in self.list_cmds.keys():
                tmp.append(key)
            self.say('{0}help [cmd] for desc. cmds = {1}'.format(self.contact,tmp))
        else:
            if arg == 'help':
                self.say(helper)
            if arg == 'lick':
                self.say(lick)
            if arg == 'deal':
                self.say(deal)
            if arg == 'table':
                self.say(table)
            if arg == 'join':
                self.say(join)
            if arg == 'newhand':
                self.say(newhand)
            if arg == 'players':
                self.say(players)
            if arg == 'flop':
                self.say(flop)
            if arg == 'turn':
                self.say(turn)
            if arg == 'river':
                self.say(river)
            if arg == 'fold':
                self.say(fold)
            if arg == 'check':
                self.say(check)
            if arg == 'call':
                self.say(call)
            if arg == 'raise':
                self.say(raises)
            if arg == 'bet':
                self.say(bet)
    def lick(self):
        filer = open('/home/metulburr/Documents/licks.txt')
        lines = filer.readlines()
        for line in lines:
            line1 = line
        
        line1 = int(line1) + 1
        filer.close()
        
        filer = open('/home/metulburr/Documents/licks.txt', 'w')
        filer.write(str(line1))
        filer.close()
        self.say('pussy has been licked {} times'.format(line1))
    
    def get_a_card(self):
        #self.say('running msg function')
        cards = [2,3,4,5,6,7,8,9,10,'Jack','Queen','King','Ace']
        types = ['clubs', 'spades', 'diamonds', 'hearts']
        
        c = random.randint(0,12)
        t = random.randint(0,3)
        
        self.sock.send(
            'PRIVMSG {} :your card is {} of {}\r\n'.format(
                self.username,cards[t], types[t]).encode())
        self.say('{}: I sent your card, check your private messages'.format(self.username))
        #self.send_operation('MSG', name='metulburr', other='test message 1')
        
    def joingame(self):
        returner = self.game.join(self.username)
        if returner is not None:
            self.say(returner)
    
    def players(self):
        self.say(self.game.show_players())
    
    def deal(self):
        #self.say('self.game.deck is: {}'.format(self.game.deck))
        if len(self.game.players) > 0:
            if self.game.gameon == False:
                deck = self.game.new_hand()
                for player in self.game.players:
                    cards = self.game.deal(deck, player)
                    self.sock.send('PRIVMSG {} :Your cards: {}\r\n'.format(
                        player, cards).encode())
                self.game.gameon = True
                self.say('All players have been delt 2 cards. Check your private messages')
            else:
                self.say('{}: A game is already in progress'.format(self.username))
        else:
            self.say('{}: No players have joined'.format(self.username))
            
    def table(self):
        self.say(self.game.propertable)
        
    def showhands(self):
        self.say(self.game.showhands())
    
    def flop(self):
        if self.game.deck: #if empty
            if not self.game.table: #if not empty
                self.game.flop()
                self.say(self.game.propertable)
            else:
                self.say('{}: The flop is already out'.format(self.username))
        else:
            self.say('{}: No one has been delt yet'.format(self.username))
    
    def river(self):
        if len(self.game.table) == 4:
            self.game.turn_river()
            self.say(self.game.propertable)
        elif len(self.game.table) < 4:
            self.say('{}: It is not time for the river'.format(self.username))
        elif len(self.game.table) == 5:
            self.say('{}: The river is already out'.format(self.username))
        
    def turn(self):
        if len(self.game.table) == 3:
            self.game.turn_river()
            self.say(self.game.propertable)
        elif len(self.game.table) < 3:
            self.say('{}: It is not time for the turn'.format(self.username))
        elif len(self.game.table) > 4:
            self.say('{}: The turn is already out'.format(self.username))
            
    def newhand(self):
        if self.game.deck:
            if self.game.gameon is False or len(self.game.table) == 5:
                self.game.reset()
                self.game.new_hand() #reset values
                self.say('Game table cleared, deck shuffled')
            else:
                self.say('{}: A game is already in progress'.format(self.username))
        else:
            self.say('{}: The cards have not been delt'.format(self.username))
            
    def fold(self):
        if self.game.gameon is True:
            if self.username in self.game.players:
                self.game.fold(self.username)
                self.say('{} has folded'.format(self.username))
            else:
                self.say('{}: You are not in the game'.format(self.username))
                
    def check(self):
        self.game.check()
        self.say('{} checks'.format(self.username))
    def call(self):
        self.game.call()
        self.say('{} calls'.format(self.username))
    def raises(self, amt=None):
        if amt is None:
            self.help('raise')
            return
        self.game.raises(amt)
        self.say('{}: raises {}'.format(self.username, amt))
    def bet(self, amt=None):
        if amt is None:
            self.help('bet')
            return
        self.game.bet(amt)
        self.say('{}: bets {}'.format(self.username, amt))
        

    



if __name__ == '__main__':
    connect = cmd_arg()
    try:
        print('channel: ', connect.channel)
        print('port: ', connect.port)
        print('host: ', connect.host)
        print('contact: ', connect.contact)
    except NameError:
        print(show_help)