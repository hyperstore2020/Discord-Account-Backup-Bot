import requests, random, time, sys, os

token = '' # Your Discord token.

def save_friends():
    saved_friends = 0

    friends = requests.get('https://discord.com/api/v6/users/@me/relationships', headers = headers)
    for friend in friends.json():
        if friend['type'] == 1:
            username = 'Username: %s#%s | User ID: %s\n' % (friend['user']['username'], friend['user']['discriminator'], friend['id'])
            sys.stdout.write(username)
            with open('Discord Friends.txt', 'a', encoding = 'UTF-8') as f:
                f.write('%s' % (username))
            saved_friends += 1

    with open('Discord Friends.txt', 'r', encoding = 'UTF-8') as f:
        fixed = f.read()[:-1]
    with open('Discord Friends.txt', 'w', encoding = 'UTF-8') as f:
        f.write(fixed)

    sys.stdout.write('\n> Successfully saved all %s Discord friends.\n\n' % (saved_friends))

def save_servers():
    saved_servers = 0
    attempts = 0
    server_info_all = ''

    servers = requests.get('https://discordapp.com/api/v6/users/@me/guilds', headers = headers)
    for server in servers.json():
        server_info_all += '%s|||%s\n' % (server['id'], server['name'])

    payload = {
        'max_age': '0',
        'max_uses': '0',
        'temporary': False
    }

    for server_info in server_info_all.splitlines():
        server_id = server_info.split('|||')[0]
        server_name = server_info.split('|||')[1]

        channels = requests.get('https://discord.com/api/v6/guilds/%s/channels' % (server_id), headers = headers)
        for channel in channels.json():
            if channel['type'] == 0:
                channel_id = channel['id']
                invite = requests.post('https://discord.com/api/v6/channels/%s/invites' % (channel_id), json = payload, headers = headers)
                
                if invite.status_code == 403:
                    attempts += 1
                    sys.stdout.write('Discord Server: %s | Channel ID: %s | Retrying . . .\n' % (server_name, channel_id))
                    if attempts == 5:
                        sys.stdout.write('%s has a Vanity URL.\n' % (server_name))
                        with open('Discord Servers.txt', 'a', encoding = 'UTF-8') as f:
                            f.write('Discord Server: %s | Vanity URL\n' % (server_name))
                        saved_servers += 1
                        attempts = 0
                        break
                    else:
                        pass
                    time.sleep(4)
                
                elif invite.status_code == 429:
                    sys.stdout.write('Rate limited.\n')
                    time.sleep(9)
                
                else:
                    invite_url = 'https://discord.gg/%s' % (str(invite.json()['code']))
                    sys.stdout.write('Discord Server: %s | Invite Link: %s\n' % (server_name, invite_url))
                    with open('Discord Servers.txt', 'a', encoding = 'UTF-8') as f:
                        f.write('Discord Server: %s | Channel ID: %s | Invite Link: %s\n' % (server_name, channel_id, invite_url))
                    saved_servers += 1
                    time.sleep(4)
                    break

    sys.stdout.write('\n> Successfully saved all %s Discord servers.\n\n' % (saved_servers))

def add_friends():
    added_friends = 0

    if os.path.exists('Discord Friends.txt'):
        with open('Discord Friends.txt', 'r', encoding = 'UTF-8') as f:
            for line in f.readlines():
                while True:
                    try:
                        line = line.replace('\n', '')
                        user_id = line.split('User ID: ')[1]
                        user_name = line.split(' |')[0]
                    except IndexError:
                        sys.stdout.write('Invalid syntax at line: %s\n' % (line))
                        break
                    
                    add = requests.put('https://discord.com/api/v6/users/@me/relationships/%s' % (user_id), json = {}, headers = headers)
                    if add.status_code == 429:
                        sys.stdout.write('Rate limited.\n')
                        time.sleep(10)
                    elif add.status_code == 204:
                        sys.stdout.write('Sent Friend Request to: %s\n' % (user_name))
                        added_friends += 1
                        break
                    elif add.status_code == 400:
                        sys.stdout.write('User has disabled Friend Requests: %s\n' % (user_name))
                        break
                    elif add.status_code == 403:
                        sys.stdout.write('Verify your Discord account.\n')
                        break
                    else:
                        sys.stdout.write('Error: %s\n' % (add.text))
                        break

                delay = random.randint(30, 35)
                time.sleep(delay)
        
        sys.stdout.write('\n> Successfully added %s Discord friends.\n\n' % (added_friends))
    
    else:
        sys.stdout.write('> You have not saved any friends.\n\n')

def join_servers():
    joined_servers = 0

    if os.path.exists('Discord Servers.txt'):
        with open('Discord Servers.txt', 'r', encoding = 'UTF-8') as f:
            for line in f.readlines():
                while True:
                    try:
                        line = line.replace('\n', '')
                        if 'Vanity URL' in line:
                            sys.stdout.write('Server has a Vanity URL.\n')
                            break
                        else:
                            invite_code = line.split('https://discord.gg/')[1]
                            server_name = line.split('Discord Server: ')[1].split(' | Channel ID')[0]
                    except IndexError:
                        sys.stdout.write('Invalid syntax at line: %s\n' % (line))
                        break
                    
                    join = requests.post('https://discord.com/api/v6/invites/%s' % (invite_code), headers = headers)
                    if join.status_code == 429:
                        sys.stdout.write('Rate limited.\n')
                        time.sleep(10)
                    elif join.status_code == 200:
                        sys.stdout.write('Successfully Joined: %s\n' % (server_name))
                        joined_servers += 1
                        break
                    elif join.status_code == 403:
                        sys.stdout.write('Verify your Discord account.\n')
                        break
                    else:
                        sys.stdout.write('Error: %s\n' % (join.text))
                        break

                delay = random.randint(40, 45)
                time.sleep(delay)

        sys.stdout.write('\n> Successfully joined %s Discord servers.\n\n' % (joined_servers))

    else:
        sys.stdout.write('> You have not saved any servers.\n\n')

while True:
    os.system('title [Discord Account Backup Bot] - Main Menu')
    headers = { 'authorization': token }
    connect = requests.get('https://canary.discordapp.com/api/v6/users/@me', headers = headers)

    if connect.status_code == 200:
        option = str(input('[1] Save Friends\n[2] Save Servers\n\n[3] Add Friends\n[4] Join Servers\n\n> Select an option: '))
        sys.stdout.write('\n')
        if option == '1' or option == 'Save Friends':
            os.system('title [Discord Account Backup Bot] - Save Friends')
            save_friends()
        elif option == '2' or option == 'Save Servers':
            os.system('title [Discord Account Backup Bot] - Save Servers')
            save_servers()
        elif option == '3' or option == 'Add Friends':
            os.system('title [Discord Account Backup Bot] - Add Friends')
            add_friends()
        elif option == '4' or option == 'Join Servers':
            os.system('title [Discord Account Backup Bot] - Join Servers')
            join_servers()
        else:
            sys.stdout.write('> Invalid option.\n\n')

    else:
        sys.stdout.write('> Invalid Discord token.\n')
        token = str(input('Discord token: '))
        sys.stdout.write('\n')
