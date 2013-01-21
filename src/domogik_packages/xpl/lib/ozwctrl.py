# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}$

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Support Z-wave technology

Implements
==========

-Zwave

@author: Nico <nico84dev@gmail.com> 
@author: bibi21000 aka Sébastien GALLET <bibi21000@gmail.com>
@copyright: (C) 2007-2012 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import binascii
import libopenzwave
from libopenzwave import PyManager
from ozwnode import ZWaveNode
from ozwdefs import *
import time 
from time import sleep

class OZwaveCtrlException(OZwaveException):
    """"Zwave Controller exception  class"""
            
    def __init__(self, value):
        OZwaveException.__init__(self, value)
        self.msg = "OZwave Controller exception:"
        
class ZWaveController(ZWaveNode):
    '''
    The controller manager.

    Allows to retrieve informations about the library, statistics, ...
    Also used to send commands to the controller

    Commands :

        - Driver::ControllerCommand_AddController - Add a new secondary controller to the Z-Wave network.
        - Driver::ControllerCommand_AddDevice - Add a new device (but not a controller) to the Z-Wave network.
        - Driver::ControllerCommand_CreateNewPrimary (Not yet implemented)
        - Driver::ControllerCommand_ReceiveConfiguration -
        - Driver::ControllerCommand_RemoveController - remove a controller from the Z-Wave network.
        - Driver::ControllerCommand_RemoveDevice - remove a device (but not a controller) from the Z-Wave network.
        - Driver::ControllerCommand_RemoveFailedNode - move a node to the controller's list of failed nodes.  The node must actually
        have failed or have been disabled since the command will fail if it responds.  A node must be in the controller's failed nodes list
        for ControllerCommand_ReplaceFailedNode to work.
        - Driver::ControllerCommand_HasNodeFailed - Check whether a node is in the controller's failed nodes list.
        - Driver::ControllerCommand_ReplaceFailedNode - replace a failed device with another. If the node is not in
        the controller's failed nodes list, or the node responds, this command will fail.
        - Driver:: ControllerCommand_TransferPrimaryRole    (Not yet implemented) - Add a new controller to the network and
        make it the primary.  The existing primary will become a secondary controller.
        - Driver::ControllerCommand_RequestNetworkUpdate - Update the controller with network information from the SUC/SIS.
        - Driver::ControllerCommand_RequestNodeNeighborUpdate - Get a node to rebuild its neighbour list.  This method also does ControllerCommand_RequestNodeNeighbors afterwards.
        - Driver::ControllerCommand_AssignReturnRoute - Assign a network return route to a device.
        - Driver::ControllerCommand_DeleteAllReturnRoutes - Delete all network return routes from a device.
        - Driver::ControllerCommand_CreateButton - Create a handheld button id.
        - Driver::ControllerCommand_DeleteButton - Delete a handheld button id.

    Callbacks :

        - Driver::ControllerState_Waiting, the controller is waiting for a user action.  A notice should be displayed
        to the user at this point, telling them what to do next.
        For the add, remove, replace and transfer primary role commands, the user needs to be told to press the
        inclusion button on the device that  is going to be added or removed.  For ControllerCommand_ReceiveConfiguration,
        they must set their other controller to send its data, and for ControllerCommand_CreateNewPrimary, set the other
        controller to learn new data.
        - Driver::ControllerState_InProgress - the controller is in the process of adding or removing the chosen node.  It is now too late to cancel the command.
        - Driver::ControllerState_Complete - the controller has finished adding or removing the node, and the command is complete.
        - Driver::ControllerState_Failed - will be sent if the command fails for any reason.

    '''
    SIGNAL_CTRL_NORMAL = 'Normal'                   # No command in progress.  
    SIGNAL_CTRL_STARTING = 'Starting'             # The command is starting.  
    SIGNAL_CTRL_CANCEL = 'Cancel'                   # The command was cancelled.
    SIGNAL_CTRL_ERROR = 'Error'                       # Command invocation had error(s) and was aborted 
    SIGNAL_CTRL_WAITING = 'Waiting'                # Controller is waiting for a user action.  
    SIGNAL_CTRL_SLEEPING = 'Sleeping'              # Controller command is on a sleep queue wait for device.  
    SIGNAL_CTRL_INPROGRESS = 'InProgress'       # The controller is communicating with the other device to carry out the command.  
    SIGNAL_CTRL_COMPLETED = 'Completed'         # The command has completed successfully.  
    SIGNAL_CTRL_FAILED = 'Failed'                     # The command has failed.  
    SIGNAL_CTRL_NODEOK = 'NodeOK'                   # Used only with ControllerCommand_HasNodeFailed to indicate that the controller thinks the node is OK.  
    SIGNAL_CTRL_NODEFAILED = 'NodeFailed'       # Used only with ControllerCommand_HasNodeFailed to indicate that the controller thinks the node has failed.

    SIGNAL_CONTROLLER = 'Message'

    CMD_NONE = 0
    CMD_ADDDEVICE = 1
    CMD_CREATENEWPRIMARY = 2
    CMD_RECEIVECONFIGURATION = 3
    CMD_REMOVEDEVICE = 4
    CMD_REMOVEFAILEDNODE = 5
    CMD_HASNODEFAILED = 6
    CMD_REPLACEFAILEDNODE = 7
    CMD_TRANSFERPRIMARYROLE = 8
    CMD_REQUESTNETWORKUPDATE = 9
    CMD_REQUESTNODENEIGHBORUPDATE = 10
    CMD_ASSIGNRETURNROUTE = 11
    CMD_DELETEALLRETURNROUTES = 12
    CMD_SENDNODEINFORMATION = 13
    CMD_REPLICATIONSEND = 14
    CMD_CREATEBUTTON = 15
    CMD_DELETEBUTTON = 16
    
    #Liste des commandes implémentées et disponible pour l'UI
    AVAILABLECMDS = ['AddDevice', 'CreateNewPrimary', 'ReceiveConfiguration', 'RemoveDevice', 'RemoveFailedNode', 'HasNodeFailed', 
                 'ReplaceFailedNode', 'TransferPrimaryRole', 'RequestNetworkUpdate', 'RequestNodeNeighborUpdate', 'AssignReturnRoute', 
                 'DeleteAllReturnRoutes', 'SendNodeInformation', 'ReplicationSend', 'CreateButton', 'DeleteButton']
  #  AVAILABLECMDS = ['None','AddDevice', 'CreateNewPrimary', 'ReceiveConfiguration', 'RemoveDevice', 'RemoveFailedNode', 'HasNodeFailed', 
  #               'ReplaceFailedNode', 'TransferPrimaryRole', 'RequestNetworkUpdate', 'RequestNodeNeighborUpdate', 'AssignReturnRoute', 
  #               'DeleteAllReturnRoutes', 'SendNodeInformation', 'ReplicationSend', 'CreateButton', 'DeleteButton']
                  

    def __init__(self,  ozwmanager,  homeId, nodeId,  isPrimaryCtrl=False):
        '''
        Innitialise un controlleur.

        @param ozwmanager: pointeur sur l'instance du manager
        @param homeid: ID du réseaux home/controleur
        @param nodeid: ID du node
        '''
        if nodeId == None:
            nodeId = 1
        ZWaveNode.__init__(self, ozwmanager,  homeId, nodeId)
        self._isPrimaryCtrl = isPrimaryCtrl
        print 'creation du ctrl'
        self._lastCtrlState = {'update' : time.time(),  'state': self.SIGNAL_CTRL_NORMAL, 'error_msg' : 'None.', 'message': 'No command in progress.', 'error': 0}
        print "fait"
    # On accède aux attributs uniquement depuis les property
    isPrimaryCtrl = property(lambda self: self._isPrimaryCtrl)

    def __str__(self):
        """
        The string representation of the node.
        :rtype: str
        """
        if self.isPrimaryCtrl : typeCtrl = "the primary"
        else : typeCtrl = "a secondary"
        return 'homeId: [{0}]  nodeId: [{1}] product: {2}  name: {3} is it {4} controller'.format(self._homeId, self._nodeId, self._product, self._name, typeCtrl)

    def getLastState(self):
        """Retourne le dernier etat connus du controlleur et issue du callback des message action"""
        return self._lastCtrlState
        
    
    def stats(self):
        """
        Retrieve statistics from driver.

        Statistics:

            * s_SOFCnt                         : Number of SOF bytes received
            * s_ACKWaiting                     : Number of unsolicited messages while waiting for an ACK
            * s_readAborts                     : Number of times read were aborted due to timeouts
            * s_badChecksum                    : Number of bad checksums
            * s_readCnt                        : Number of messages successfully read
            * s_writeCnt                       : Number of messages successfully sent
            * s_CANCnt                         : Number of CAN bytes received
            * s_NAKCnt                         : Number of NAK bytes received
            * s_ACKCnt                         : Number of ACK bytes received
            * s_OOFCnt                         : Number of bytes out of framing
            * s_dropped                        : Number of messages dropped & not delivered
            * s_retries                        : Number of messages retransmitted
            * s_controllerReadCnt              : Number of controller messages read
            * s_controllerWriteCnt             : Number of controller messages sent

        :return: Statistics of the controller
        :rtype: dict()

        """
        return self._manager.getDriverStatistics(self.homeId)

    def _updateCapabilities(self):
        """
        Surchage de la méthode hérité de ZWaveNode : Mise à jour des capabilities set du node
        Capabilities = ['Primary Controller', 'Secondary Controller', 'Static Update Controller','Bridge Controller' ,'Routing', 'Listening', 'Beaming', 'Security', 'FLiRS']
        """
        nodecaps = set()
        if self._manager.isNodeRoutingDevice(self._homeId, self._nodeId): nodecaps.add('Routing')
        if self._manager.isNodeListeningDevice(self._homeId, self._nodeId): nodecaps.add('Listening')
        if self._manager.isNodeBeamingDevice(self._homeId, self._nodeId): nodecaps.add('Beaming')
        if self._manager.isNodeSecurityDevice(self._homeId, self._nodeId): nodecaps.add('Security')
        if self._manager.isNodeFrequentListeningDevice(self._homeId, self._nodeId): nodecaps.add('FLiRS')
        if self.isPrimaryCtrl: 
            nodecaps.add('Primary Controller')
            if self._manager.isStaticUpdateController(self._homeId): nodecaps.add('Static Update Controller')
            if self._manager.isBridgeController(self._homeId): nodecaps.add('Bridge Controller')
        else : nodecaps.add('Secondary Controller')
        self._capabilities = nodecaps
        self._ozwmanager._log.debug('Node [%d] capabilities are: %s', self._nodeId, self._capabilities)
        
    def handle_Action(self,  action):
        """Gestion des action du controlleur et des messages de retour"""    
        retval = action
        retval['error'] = ''
        if action['cmd'] == 'Stop action' :
            if self.cancel_command() :
                retval['cmdstate'] ='not running'
                retval['error'] = ''
                retval['message'] = 'User have stop command.'
            else :
                retval['cmdstate'] ='not running'
                retval['error'] = 'Fail to stop controller commande'
                if self._lastCtrlState['state'] == self.SIGNAL_CTRL_NORMAL : 
                    retval['message'] = 'User have try stop command. But no action processing.'
                else : retval['message'] = 'User have try stop command. ' + self._lastCtrlState['message'] 
        elif action['cmd'] == 'Start action' :
            if action['action'] == 'RequestNetworkUpdate' :
                if self.begin_command_request_network_update() :
                    retval['cmdstate'] ='running'
                    retval['message'] ='Waiting during refresh, be patient....'
                else :
                    retval['cmdstate'] ='not running'
                    retval['error'] = 'not started'
                    retval['message'] = 'check your controller.'
            if action['action'] =='RequestNodeNeighborUpdate':
                if action['nodeid'] == 0 :
                    self._log.error('No action.nodeid for controleur command, quit')
                    print ('ERROR : No action.nodeid for controleur command, quit')
                    node = None
                else :
                    node = self._ozwmanager._getNode(self.homeId, action['nodeid'])
                if node :
                    if self.begin_command_request_node_neigbhor_update(action['nodeid']) :
                        retval['cmdstate'] ='running'
                        retval['message'] ='Waiting during refresh, be patient....'
                    else :
                        retval['cmdstate'] ='not running'
                        retval['error'] = 'not started'
                        retval['message'] = 'check your controller.'
                else :
                    retval['cmdstate'] ='not running'
                    retval['error'] = 'Unknown node : ' + action['nodeid']
                    retval['message'] = 'check input options.'
            else :
                retval['cmdstate'] ='TODO'
                retval['message'] ='Command will be root soon as possible, be patient....'
        elif action['cmd'] =='getState':
            print '***********'
            print self.checkActionCtrl() 
            if self.checkActionCtrl() :
                retval['cmdstate']  = 'stop'
                retval.update(self.checkActionCtrl())
            else : retval['cmdstate']  = 'waiting'
        else :
            retval['error'] = 'Unknown cmd : ' + action['cmd']
            retval['cmdstate'] ='Unknown'
            retval['message'] ='Command error'
        return retval
        
    def _getValue(self, valueId):
        """Return l'objet Value correspondant au valueId"""
        retval= None
        for node in self._nodes.values():
            if node._values.has_key(valueId):
                retval = node._values[valueId]
                break
        return retval
        
    def hard_reset(self):
        """
        Hard Reset a PC Z-Wave Controller.
        Resets a controller and erases its network configuration settings.  The
        controller becomes a primary controller ready to add devices to a new network.
        """
        if self.isPrimaryCtrl : 
            self._manager.resetController(self.homeId)
            print('************  Hard Reset du controlleur ***********')
            self._ozwmanager._log.debug('Hard Reset of ZWave controller')
        else:
            self._ozwmanager._log.debug('No Hard Reset on secondary controller')

    def soft_reset(self):
        """
        Soft Reset a PC Z-Wave Controller.
        Resets a controller without erasing its network configuration settings.
        """
        if self.isPrimaryCtrl : 
            self._manager.softResetController(self.homeId)
            print('************  Soft Reset du controlleur ***********')
            self._ozwmanager._log.debug('Soft Reset of ZWave controller')
        else:
            self._ozwmanager._log.debug('No Soft Reset on secondary controller')
    
    def cmdsAvailables(self):
        """
        Return all availables crontroller commands with associate documentations
         :return: list of commands
         :rtype: dict
        """
        retval={}
        for elem in  libopenzwave.PyControllerCommand :
            if elem in self.AVAILABLECMDS : retval[elem] = str(elem.doc)
        return retval
        

    def begin_command_send_node_information(self, node_id):
        """
        Send a node information frame.

        :param node_id: Used only with the ReplaceFailedNode command, to specify the node that is going to be replaced.
        :type node_id: int
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_SENDNODEINFORMATION, self.zwcallback, nodeId=node_id)

    def begin_command_replication_send(self, high_power = False):
        """
        Send information from primary to secondary.

        :param high_power: Usually when adding or removing devices, the controller operates at low power so that the controller must
        be physically close to the device for security reasons.  If _highPower is true, the controller will
        operate at normal power levels instead.  Defaults to false.
        :type high_power: bool
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_REPLICATIONSEND, self.zwcallback, highPower=high_power)

    def begin_command_request_network_update(self):
        """
        Update the controller with network information from the SUC/SIS.

        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_REQUESTNETWORKUPDATE, self.zwcallback)

    def begin_command_add_device(self, high_power = False):
        """
        Add a new device (but not a controller) to the Z-Wave network.

        :param high_power: Used only with the AddDevice, AddController, RemoveDevice and RemoveController commands.
        Usually when adding or removing devices, the controller operates at low power so that the controller must
        be physically close to the device for security reasons.  If _highPower is true, the controller will
        operate at normal power levels instead.  Defaults to false.
        :type high_power: bool
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_ADDDEVICE, self.zwcallback, highPower=high_power)

    def begin_command_remove_device(self, high_power = False):
        """
        Remove a device (but not a controller) from the Z-Wave network.

        :param high_power: Used only with the AddDevice, AddController, RemoveDevice and RemoveController commands.
        Usually when adding or removing devices, the controller operates at low power so that the controller must
        be physically close to the device for security reasons.  If _highPower is true, the controller will
        operate at normal power levels instead.  Defaults to false.
        :type high_power: bool
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_REMOVEDEVICE, self.zwcallback, highPower=high_power)

    def begin_command_remove_failed_node(self, node_id):
        """
        Move a node to the controller's list of failed nodes.  The node must
        actually have failed or have been disabled since the command
        will fail if it responds.  A node must be in the controller's
        failed nodes list for ControllerCommand_ReplaceFailedNode to work.

        :param node_id: Used only with the ReplaceFailedNode command, to specify the node that is going to be replaced.
        :type node_id: int
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_REMOVEFAILEDNODE, self.zwcallback, nodeId=node_id)

    def begin_command_has_node_failed(self, node_id):
        """
        Check whether a node is in the controller's failed nodes list.

        :param node_id: Used only with the ReplaceFailedNode command, to specify the node that is going to be replaced.
        :type node_id: int
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_HASNODEFAILED, self.zwcallback, nodeId=node_id)

    def begin_command_replace_failed_node(self, node_id):
        """
        Replace a failed device with another. If the node is not in
        the controller's failed nodes list, or the node responds, this command will fail.

        :param node_id: Used only with the ReplaceFailedNode command, to specify the node that is going to be replaced.
        :type node_id: int
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_REPLACEFAILEDNODE, self.zwcallback, nodeId=node_id)

    def begin_command_request_node_neigbhor_update(self, node_id):
        """
        Get a node to rebuild its neighbors list.
        This method also does ControllerCommand_RequestNodeNeighbors afterwards.

        :param node_id: Used only with the ReplaceFailedNode command, to specify the node that is going to be replaced.
        :type node_id: int
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_REQUESTNODENEIGHBORUPDATE, self.zwcallback, nodeId=node_id)

    def begin_command_create_new_primary(self):
        """
        Add a new controller to the Z-Wave network. Used when old primary fails. Requires SUC.

        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_CREATENEWPRIMARY, self.zwcallback)

    def begin_command_transfer_primary_role(self, high_power = False):
        """
        Make a different controller the primary.
        The existing primary will become a secondary controller.

        :param high_power: Used only with the AddDevice, AddController, RemoveDevice and RemoveController commands.
        Usually when adding or removing devices, the controller operates at low power so that the controller must
        be physically close to the device for security reasons.  If _highPower is true, the controller will
        operate at normal power levels instead.  Defaults to false.
        :type high_power: bool
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_TRANSFERPRIMARYROLE, self.zwcallback, highPower=high_power)

    def begin_command_receive_configuration(self):
        """
        -

        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_RECEIVECONFIGURATION, self.zwcallback)

    def begin_command_assign_return_route(self, from_node_id, to_node_id):
        """
        Assign a network return route from a node to another one.

        :param from_node_id: The node that we will use the route.
        :type from_node_id: int
        :param to_node_id: The node that we will change the route
        :type to_node_id: int
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_ASSIGNRETURNROUTE, self.zwcallback, nodeId=from_node_id, arg=to_node_id)

    def begin_command_delete_all_return_routes(self, node_id):
        """
        Delete all network return routes from a device.

        :param node_id: Used only with the ReplaceFailedNode command, to specify the node that is going to be replaced.
        :type node_id: int
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_DELETEALLRETURNROUTES, self.zwcallback, nodeId=node_id)

    def begin_command_create_button(self, node_id, arg=0):
        """
        Create a handheld button id

        :param node_id: Used only with the ReplaceFailedNode command, to specify the node that is going to be replaced.
        :type node_id: int
        :param arg:
        :type arg: int
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_CREATEBUTTON, self.zwcallback, nodeId=node_id, arg=arg)

    def begin_command_delete_button(self, node_id, arg=0):
        """
        Delete a handheld button id.

        :param node_id: Used only with the ReplaceFailedNode command, to specify the node that is going to be replaced.
        :type node_id: int
        :param arg:
        :type arg: int
        :return: True if the command was accepted and has started.
        :rtype: bool

        """
        return self._manager.beginControllerCommand(self.homeId, \
            self.CMD_DELETEBUTTON, self.zwcallback, nodeId=node_id, arg=arg)

    def cancel_command(self):
        """
        Cancels any in-progress command running on a controller.

        """
        self._manager.cancelControllerCommand(self.homeId)
        
    def checkActionCtrl(self):
        
        if self._lastCtrlState['state'] in [self.SIGNAL_CTRL_NORMAL,  self.SIGNAL_CTRL_CANCEL,  self.SIGNAL_CTRL_ERROR,
                                                      self.SIGNAL_CTRL_COMPLETED, self.SIGNAL_CTRL_FAILED] :
            return self._lastCtrlState
        else : return None


    def zwcallback(self, args):
        """
        The Callback Handler used when sendig commands to the controller.

        To do : add node in signal when necessary

        :param args: A dict containing informations about the state of the controller
        :type args: dict()

        """
        self._ozwmanager._log.debug('Controller state change : %s' % (args))
        self._lastCtrlState = args
        self._lastCtrlState["update"]= time.time()
        state = args['state']
        message = args['message']
        if state == self.SIGNAL_CTRL_WAITING:
            print 'state :', state, ' -- message :', message, ' -- controller', self
        else :
            print 'state :', state, ' -- message :', message, ' -- controller', self
        self._ozwmanager.reportCtrlMsg(self._lastCtrlState)

