import os
import json


# UPDATE THIS WITH ANY COGS ADDED TO INCLUDE COMMANDS THAT YOU WANT TO BE ADDED BY DEFAULT #
default_guild_auths = {
    'roleadd': ['everyone'],
    'ping': ['everyone'],
    'pong': ['admin'],
    'play': ['everyone'],
    'pause': ['everyone'],
    'resume': ['everyone'],
}


class Authenticator:
    
    def __init__(self, json_file_path):
    
        self.json_file = json_file_path
        
        if os.path.exists(json_file_path):
        
            with open(json_file_path) as file:
        
                self.authentication_dictionary = json.load(file)
        else:
        
            with open(json_file_path, 'w') as file:
        
                self.authentication_dictionary = {}
                json.dump(self.authentication_dictionary, file, indent=4)
    
    
    ### --- Commits changes to permissions for ALL GUILDS --- ###
    ### --- THIS COMMAND MUST BE RUN FOR CHANGES TO PERMS TO BE SAVED!!! --- ###
    
    def update_config_file(self):
        
        with open(self.json_file, 'w') as file:
            json.dump(self.authentication_dictionary, file, indent=4)
    
    
    
    #Return True if role is allowed to use command, False if not.
    def authenticate(self, guild_id, roles, command):
        
        if guild_id in self.authentication_dictionary.keys():
            
            if command in self.authentication_dictionary[guild_id].keys():
            
                # Checks to see if everyone is allowed to use command
                if 'everyone' in self.authentication_dictionary[guild_id][command]:
            
                    return True
                
                # Checks to see if user has a role allowing it to use this command
                for role in roles:
                    if role.name.lower() in self.authentication_dictionary[guild_id][command]:
                        return True
            
                # Returns false if both check conditions fail
                return False
                
            else:
            
                self.authentication_dictionary[guild_id][command] = ['admin']
                
                for role in roles:
                    if role.name.lower() in self.authentication_dictionary[guild_id][command]:
                        return True
                
                return False
                
        else:
        
            self.authentication_dictionary[guild_id] = default_guild_auths
            
            if command in self.authentication_dictionary[guild_id].keys():
            
                # Checks to see if everyone is allowed to use command
                if 'everyone' in self.authentication_dictionary[guild_id][command]:
            
                    return True
                
                # Checks to see if user has a role allowing it to use this command
                for role in roles:
                    if role.name.lower() in self.authentication_dictionary[guild_id][command]:
                        return True
            
                # Returns false if both check conditions fail
                return False
                
            else:
            
                self.authentication_dictionary[guild_id][command] = ['admin']
                
                for role in roles:
                    if role.name.lower() in self.authentication_dictionary[guild_id][command]:
                        return True
                
                return False
            
            
            

    
    def add_role(self, guild_id, role, command):
    
        if guild_id in self.authentication_dictionary.keys():
            
            if command in self.authentication_dictionary[guild_id].keys():
            
                
                self.authentication_dictionary[guild_id][command].append(role.lower())
            
                
            else:
                print('UNABLE TO FIND COMMAND, ADDING IT TO ADMIN ROLE')
                self.authentication_dictionary[guild_id][command] = ['admin', role]
        else:
        
            print('UNABLE TO FIND GUILD ID IN AUTH TABLE. ADDING TO TABLE.')
            self.authentication_dictionary[guild_id] = default_guild_auths
            #self.authentication_dictionary[guild_id][command] = ['admin', role]