# Author: reiven
# github: https://github.com/DXMarkets/Savoir

import requests
import json
from base64 import b64encode
import logging
import time

log = logging.getLogger('Savoir')
log.setLevel('WARNING')


class Savoir():
    __id_count = 0
    __MAX = 100000
    def __init__(self,
                 rpcuser,
                 rpcpasswd,
                 rpchost,
                 rpcport,
                 chainname,
                 rpc_call=None
                 ):
        self.__rpcuser = rpcuser
        self.__rpcpasswd = rpcpasswd
        self.__rpchost = rpchost
        self.__rpcport = rpcport
        self.__chainname = chainname
        self.__auth_header = ' '.join(
            ['Basic', b64encode(
                ':'.join([rpcuser, rpcpasswd]).encode()).decode()]
        )
        self.__headers = {'Host': self.__rpchost,
                          # 'User-Agent': 'Savoir v0.1',
                          'Authorization': self.__auth_header,
                          'Content-type': 'text/plain'
                          # 'Content-type': 'application/json'
                          }
        self.__rpc_call = rpc_call

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        if self.__rpc_call is not None:
            name = "%s.%s" % (self.__rpc_call, name)
        return Savoir(self.__rpcuser,
                      self.__rpcpasswd,
                      self.__rpchost,
                      self.__rpcport,
                      self.__chainname,
                      name)

    def __call__(self, *args):
        Savoir.__id_count += 1
        postdata = {'chain_name': self.__chainname,
                    # 'version': '1.1',
                    'jsonrpc': '1.0',
                    'params': args,
                    'method': self.__rpc_call,
                    'id': Savoir.__id_count}
        url = ''.join(['http://', self.__rpchost, ':', self.__rpcport])
        encoded = json.dumps(postdata)
        log.info("Request: %s" % encoded)
        r = requests.post(url, data=encoded, headers=self.__headers)
        if r.status_code == 200:
            log.info("Response: %s" % r.json())
            return r.json()
        else:
            log.error("Error! Status code: %s" % r.status_code)
            log.error("Text: %s" % r.text)
            log.error("Json: %s" % r.json())
            return r.json()

    def batch(self, rpc_call, largs):
        m = self.__MAX
        i = 0
        result = []
        while i*m < len(largs):
            encoded = []
            for args in largs[i*m:(i+1)*m]:
                Savoir.__id_count += 1
                postdata = {'chain_name': self.__chainname,
                            # 'version': '1.1',
                            'jsonrpc': '1.0',
                            'params': args,
                            'method': rpc_call,
                            'id': Savoir.__id_count}
                encoded.append(postdata)
            url = ''.join(['http://', self.__rpchost, ':', self.__rpcport])
            r = requests.post(url, data=json.dumps(
                    encoded), headers=self.__headers)
            i += 1
            result += r.json()
        return result
