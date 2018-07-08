#!/usr/bin/python3
# ======================================================================== #
# pyprsync: pyprsync.py Version: 0.1.1.0                                   #
#                                                                          #
# Copyright 2018 PeopleRelay Team                                          #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License");          #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
# ======================================================================== #

#Configuration file
SYNC_CONFIG = "/etc/pyprsync.config"
#SYNC_CONFIG = "pyprsync.config"

#Database connection default parameters
SYNC_DEF_HOST = "127.0.0.1"
SYNC_DEF_PORT = 3050
SYNC_DEF_PATH = "peoplerelay.fb"
SYNC_DEF_SQL_DIALECT = 3
SYNC_DEF_CHARSET = "UTF8"

#Synchronization default parameters
SYNC_DEF_USER = "p_syncbot"
SYNC_DEF_PW = "PeopleRelay"
#Interval between synchronizations
SYNC_DEF_INTER = 30
#Interval between connections
SYNC_DEF_CON_INTER = 60
SYNC_DEF_RECON_AF = 3

#Synchronization procedure name
SYNC_FUNC_NAME = "P_Sync"

#Error messages
SYNC_MSG_EF = "Error while loading config file!"
SYNC_MSG_EC = "Error while connecting to database!"
SYNC_MSG_ES = "Error while executing synchronization!"
SYNC_MSG_ER = "Error while running!"

#Misc messages
SYNC_MSG_ST = "Stopped"

#Configuration file keys
SYNC_CFG_SECT = "sync"
SYNC_CFG_HOST = "db_host"
SYNC_CFG_PORT = "db_port"
SYNC_CFG_PATH = "db_path"
SYNC_CFG_USER = "user"
SYNC_CFG_PW = "password"
SYNC_CFG_SQL_DIALECT = "sql_dialect"
SYNC_CFG_CHARSET = "charset"
SYNC_CFG_INTER = "sync_interval"
SYNC_CFG_CON_INTER = "connection_interval"
SYNC_CFG_RECON_AF = "reconnect_after"


#================================================================#
#================================================================#

import fdb
import configparser
import time
import threading
import signal

#================================================================#
#================================================================#

def my_sleep(wait):
    end = time.time() + float(wait)
    while RUNNING:
        if time.time() < end:
            time.sleep(0.1)
        else:
            break


###########################################################################

def handler(signum, frame):
    
    global RUNNING
    RUNNING = False
    
    print(SYNC_MSG_ST, flush=True)


#================================================================#
#================================================================#

class pr_sync(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.config_name = SYNC_CONFIG
        self.sync_func = SYNC_FUNC_NAME
        
        #Load configuration from file
        #self._load_params(self.config_name)
        
        #Load hard coded configuration
        #self._defualt_params()
        
        #Load configuration from file.In case of failure fallback to hard coded values
        try:
            self._load_params(self.config_name)
            
        except Exception:
            self._defualt_params()


    ###########################################################################

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_con()


    ###########################################################################

    def run(self):
        
        self.fail_count = 0
        self.failed = False
        
        while RUNNING:
            try:
                self._con_db()
                
            except Exception:
                if not self.failed:
                    print(SYNC_MSG_EC, flush=True)
                    self.failed = True
                    
                    my_sleep(self.con_interval)
                    
            else:
                self.fail_count = 0
                self.failed = False
                
                while RUNNING and self.fail_count <= self.recon_after:
                    try:
                        self._sync()
                        
                    except Exception:
                        self.recon_after += 1
                        
                        if not self.failed:
                            print(SYNC_MSG_ES, flush=True)
                            self.failed = True
                            
                        my_sleep(self.interval)
                            
                    else:
                        self.fail_count = 0
                        self.failed = False
                        
                        my_sleep(self.interval)
                        
            finally:
                self.close_con()


    ###########################################################################

    def _defualt_params(self):
        self.db_host = SYNC_DEF_HOST
        self.db_port = SYNC_DEF_PORT
        self.db_path = SYNC_DEF_PATH
        
        self.db_user = SYNC_DEF_USER
        self.db_sync_pw = SYNC_DEF_PW
        
        self.db_sql_dialect = SYNC_DEF_SQL_DIALECT
        self.db_charset = SYNC_DEF_CHARSET
        
        self.interval = SYNC_DEF_INTER
        self.con_interval = SYNC_DEF_CON_INTER
        
        self.recon_after = SYNC_DEF_RECON_AF


    ###########################################################################

    def _load_params(self, f_name):
        try:
            f1 = open(f_name, "r")
            
            config = configparser.ConfigParser()
            config.read_file(f1)
            
            self.db_host = config[SYNC_CFG_SECT][SYNC_CFG_HOST]
            self.db_port = config[SYNC_CFG_SECT].getint(SYNC_CFG_PORT)
            self.db_path = config[SYNC_CFG_SECT][SYNC_CFG_PATH]
            
            self.db_user = config[SYNC_CFG_SECT][SYNC_CFG_USER]
            self.db_pw = config[SYNC_CFG_SECT][SYNC_CFG_PW]
            
            self.db_sql_dialect = config[SYNC_CFG_SECT].getint(SYNC_CFG_SQL_DIALECT)
            self.db_charset = config[SYNC_CFG_SECT][SYNC_CFG_CHARSET]
            
            self.interval = config[SYNC_CFG_SECT].getfloat(SYNC_CFG_INTER)
            self.con_interval = config[SYNC_CFG_SECT].getfloat(SYNC_CFG_CON_INTER)
            
            self.recon_after = config[SYNC_CFG_SECT].getint(SYNC_CFG_RECON_AF)
            
        except Exception:
            print(SYNC_MSG_EF, flush=True)
            raise Exception
            
        finally:
            try:
                f1.close()
                
            except Exception:
                    pass


    ###########################################################################

    def _con_db(self):
        self.connection1 = fdb.connect(host = self.db_host,
                                       port = self.db_port,
                                       database = self.db_path,
                                       user = self.db_user,
                                       password = self.db_pw,
                                       charset = self.db_charset,
                                       sql_dialect = self.db_sql_dialect)
        
        self.cursor1 = self.connection1.cursor()


    ###########################################################################

    def _sync(self):
        self.cursor1.callproc(self.sync_func)
        self.connection1.commit()


    ###########################################################################

    def close_con(self):
        try:
            self.cursor1.close()
            self.connection1.close()
            
        except Exception:
            pass


#================================================================#
#================================================================#

RUNNING = True

if __name__ == '__main__':
    signal.signal(signal.SIGHUP, handler)
    
    try:
        thread1 = pr_sync()
        thread1.start()
        thread1.join()
        
    except Exception:
        print(SYNC_MSG_ER, flush=True)
        
    finally:
        thread1.close_con()
