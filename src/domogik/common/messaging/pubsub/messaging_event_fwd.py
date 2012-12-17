#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

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

Module purpose
==============

PUB-SUB forwarder

Implements
==========


@author: Marc SCHNEIDER <marc@mirelsol.org>
@copyright: (C) 2007-2012 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import zmq
from domogik.common.configloader import Loader

def main():
    cfg = Loader('messaging').load()
    cfg_messaging = dict(cfg[1])
    
    try:
        context = zmq.Context(1)
        # Socket facing emitters
        frontend = context.socket(zmq.SUB)
        # Forwarder subscribes to the emitter *pub* port
        frontend.bind("tcp://*:%s" % cfg_messaging['event_pub_port'])
        
        frontend.setsockopt(zmq.SUBSCRIBE, "") # We want to get all messages from emitters
        
        # Socket facing receivers
        backend = context.socket(zmq.PUB)
        # Forwarder publishes to the receiver *sub* port
        backend.bind("tcp://*:%s" % cfg_messaging['event_sub_port'])
        
        print("Forwarding messages...")
        zmq.device(zmq.FORWARDER, frontend, backend)
    except Exception, e:
        print(e)
        print("Bringing down ZMQ device")
    finally:
        pass
        frontend.close()
        backend.close()
        context.term()

if __name__ == "__main__":
    main()
