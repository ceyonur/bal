"""
Block[Chain] Node classes for Mininet.

BCNodes provide a simple abstraction for interacting with Block[Chains]. Local nodes are simply one or more processes on the local machine.
"""

from mininet.util import quietRun
from mininet.moduledeps import pathCheck

from mininet.node import CPULimitedHost
from mininet.log import debug

import os

class BCNode( CPULimitedHost):
    """A BCNode is a Node that is running (or has execed?) an
       block[chain] application."""

    def __init__( self, name, inNamespace=True,
                  server='', sargs='', sdir='/tmp/bcn',
                  client='', cargs='{command}', cdir=None,
                  ip="127.0.0.1", port='', socket='6000', **params ):
        # Server params
        self.server = server
        self.sargs = sargs
        self.sdir = sdir
        # Client params
        self.client = client
        self.cargs = cargs
        self.cdir = cdir

        self.ip = ip
        self.port = port
        self.socket= socket
        CPULimitedHost.__init__( self, name, inNamespace=inNamespace,
                       ip=ip, **params  )

    def start( self, sim_path ):
        """Start <bcnode> <args> on node.
           Log to /tmp/bc_<name>.log"""
        if self.server:
            pathCheck( self.server )
            cout = self.sdir  + '/bc_' + self.name + '.log'
            if self.sdir is not None:
                try:
                    os.stat(self.sdir)
                except:
                    os.mkdir(self.sdir)
                self.cmd( 'cd ' + self.sdir )
            cmd = self.server
            if self.sargs:
                cmd += " " + self.sargs.format(name=self.name,
                                               IP=self.IP(),
                                               port=self.port,
                                               cdir=self.cdir,
                                               sdir=self.sdir,
                                               socket=self.socket,
                                               simulation_path = sim_path)
            debug( cmd + ' 1>' + cout + ' 2>' + cout + ' &' )
            self.cmd( cmd + ' 1>' + cout + ' 2>' + cout + ' &' )
            self.execed = False

    def stop( self, *args, **kwargs ):
        "Stop node."
        self.cmd( 'kill %' + self.server )
        self.cmd( 'wait %' + self.server )
        super( BCNode, self ).stop( *args, **kwargs )

    def isAvailable( self ):
        "Is executables available?"
        cmd = 'which '
        if self.server:
            cmd += self.server + ' '
        if self.client:
            cmd += self.client
        return quietRun(cmd)


    def call(self, command, silent= False, data=''):
        """Call <client> <cargs> on node."""
        if self.cdir is not None:
            self.cmd( 'cd ' + self.cdir )
        cmd = self.client
        pathCheck( cmd )
        if data:
            method = '''POST -H "Content-Type: application/json" -d '{data}' '''.format(data = data)
        else:
            method = "GET"

        if self.cargs:
            cmd += " " + self.cargs.format(command=command,
                                           method=method,
                                           name=self.name,
                                           IP=self.IP(),
                                           port=self.port,
                                           cdir=self.cdir,
                                           sdir=self.sdir)
        else:
            cmd += " "  + command
        if silent:
            result = self.cmd( cmd )
        else:
            result = self.cmdPrint( cmd )

        debug("command: %s = %s" % (cmd, result))
        return result

class POWNode(BCNode):
    """A POWNode is a BCNode that is running an POWBlockchain."""

    def __init__( self, name, bcclass=None, inNamespace=True,
                  server='blockchain.py',
                  sargs='-p {port} -s {socket} -d 2 -k {sdir}/{IP}pow.pem -n {name} -sp {simulation_path}',
                  sdir='/tmp/bcn',
                  client='curl',
                  cargs="-s -X {method} http://{IP}:{port}/{command}",
                  cdir=None,
                  ip="127.0.0.1", port='5000', **params ):

        BCNode.__init__( self, name, inNamespace=inNamespace,
                         server=server, sargs=sargs, sdir=sdir,
                         client=client, cargs=cargs, cdir=cdir,
                         ip=ip, port=port, **params )

class POSNode(BCNode):
    """A POSNode is a BCNode that is running an POSBlockchain."""

    def __init__( self, name, bcclass=None, inNamespace=True,
                  server='blockchain.py',
                  sargs='-p {port} -s {socket} -v pos -k {sdir}/{IP}pos.pem -n {name} -sp {simulation_path}',
                  sdir='/tmp/bcn',
                  client='curl',
                  cargs="-s -X {method} http://{IP}:{port}/{command}",
                  cdir=None,
                  ip="127.0.0.1", port='5000', socket='6000', **params ):

        BCNode.__init__( self, name, inNamespace=inNamespace,
                         server=server, sargs=sargs, sdir=sdir,
                         client=client, cargs=cargs, cdir=cdir,
                         ip=ip, port=port, **params )
