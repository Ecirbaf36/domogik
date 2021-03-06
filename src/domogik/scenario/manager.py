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

Plugin purpose
==============

This plugin manages scenarii

Implements
==========


@author: Maxence Dunnewind
@copyright: (C) 2007-2011 Domogik project
@license: GPL(v3)
@organization: Domogik
"""
import pkgutil
import importlib
import inspect
import uuid
import json
import domogik.scenario.tests as s_t
import domogik.scenario.parameters as s_p
import domogik.scenario.actions as s_a
from domogik.common.database import DbHelper
from domogik.scenario.scenario import ScenarioInstance
from exceptions import KeyError


class ScenarioManager:
    """ Manage scenarios : create them, evaluate them, etc ...
        A scenario instance contains a condition, which is a boolean
        combination of many tests,
        and a list of actions
        Each test can be :
         - test on the test of any device
         - test on the time
         - action triggered by user (click on UI for ex)
        The test on devices are managed directly by xpl Listeners
        The test on time will be managed by a TimeManager
        The actions will be managed by an ActionManager
        { 
         "condition" :
            { "AND" : {
                    "OR" : {
                        "one-uuid" : {
                            "param_name_1" : {
                                "token1" : "value",
                                "token2" : "othervalue"
                            },
                            "param_name_2" : {
                                "token3" : "foo"
                            }
                        },
                        "another-uuid" : {
                            "param_name_1" : {
                                "token4" : "bar"
                            }
                        }
                    },
                    "yet-another-uuid" : {
                        "param_name_1" : {
                            "url" : "http://google.fr",
                            "interval" : "5"
                        }
                    }
                }
            },
         "actions" : [
            "uid-for-action" : {
                "param1" : "value1",
                "param2" : "value2"
            },
            "uid-for-action2" : {
                "param3" : "value3"
            }
         ]
        }
    """

    def __init__(self, log):
        """ Create ScenarioManager instance
            @param log : Logger instance
        """
        # Keep list of conditions as name : instance
        self._instances = {}
        # an instance of the logger
        self.log = log
        # load all scenarios from the DB
        self._db = DbHelper()
        self.load_scenarios()

    def load_scenarios(self):
        """ Loads all scenarios from the db
        for each scenario call the create_scenario method
        """
        with self._db.session_scope():
            for scenario in self._db.list_scenario():
                self.create_scenario(scenario.name, scenario.json, scenario.id)

    def shutdown(self):
        """ Callback to shut down all parameters
        """
        for cond in self._conditions.keys():
            self.delete_scenario(cond, db_delete=False)

    def get_parsed_condition(self, name):
        """ Call cond.get_parsed_condition on the cond with name 'name'
        @param name : name of the Condition
        @return {'name':name, 'data': parsed_condition} or raise Exception
        """
        if name not in self._conditions:
            raise KeyError('no key %s in conditions table' % name)
        else:
            parsed = self._conditions[name].get_parsed_condition()
            return {'name': name, 'data': parsed}

    def delete_scenario(self, name, db_delete=True):
        if name not in self._conditions:
            self.log.info(u"Scenario {0} doesn't exist".format(name))
            return {'status': 'ERROR', 'msg': u"Scenario {0} doesn't exist".format(name)}
        else:
            # TODO
            self.log.info(u"Scenario {0} deleted".format(name))

    def create_scenario(self, name, json_input, cid=0):
        """ Create a Scenario from the provided json.
        @param name : A name for the condition instance
        @param json_input : JSON representation of the condition
        The JSON will be parsed to get all the uuids, and test instances will be created.
        The json needs to have 2 keys:
            - condition => the json that will be used to create the condition instance
            - actions => the json that will be used for creating the actions instances
        @Return {'name': name} or raise exception
        """
        try:
            payload = json.loads(json_input)  # quick test to check if json is valid
        except Exception as e:
            self.log.error(u"Creation of a scenario failed, invallid json: {0}".format(json_input))
            self.log.debug(e)
            return {'status': 'NOK', 'msg': 'invallid json'}

        if 'IF' not in payload.keys() \
                or 'DO' not in payload.keys():
            msg = u"the json for the scenario does not contain condition or actions for scenario {0}".format(name)
            self.log.error(msg)
            return {'status': 'NOK', 'msg': msg}

        # create the condition itself
        scen = ScenarioInstance(self.log, cid, name, payload)
        self._instances[cid] = {'name': name, 'json': payload, 'instance': scen } 
        self.log.debug(u"Create scenario instance {0} with payload {1}".format(name, payload['IF']))
        
        # return
        return {'name': name}

    def eval_condition(self, name):
        """ Evaluate a condition calling eval_condition from Condition instance
        @param name : The name of the condition instance
        @return {'name':name, 'result': evaluation result} or raise Exception
        """
        if name not in self._conditions:
            raise KeyError('no key %s in conditions table' % name)
        else:
            res = self._conditions[name].eval_condition()
            return {'name': name, 'result': res}

    def trigger_actions(self, name):
        """ Trigger that will be called when a condition evaluates to True
        """
        if name not in self._conditions_actions \
                or name not in self._conditions:
            raise KeyError('no key %s in one of the _conditions tables table' % name)
        else:
            for action in self._conditions_actions[name]:
                self._actions_mapping[action].do_action( \
                        self._conditions[name], \
                        self._conditions[name].get_mapping() \
                        )

    def list_actions(self):
        """ Return the list of actions
        @return a hash of hashes for the different actions
        { "module1.Action1" : {
            "description" : "some description of the action",
            "parameters" : { "param1" : {
                ... see get_expected_entries for details
            }
        }
        """

        self.log.debug("ScenarioManager : list actions")
        res = {}
        actions = self.__return_list_of_classes(s_a)
        for name, cls in actions:
            self.log.debug("- {0}".format(name))
            inst = cls()
            res[name] = {"parameters": inst.get_expected_entries(),
                         "description": inst.get_description()}
        return res

    def list_tests(self):
        """ Return the list of tests
        @return a hash of hashes for the different tests
        { "module1.Test1" : {
            "description" : "some description of the test",
            "parameters" : { "param1" : {
                ... see list_parameters doc for detail on this part
            }
        }
        """

        self.log.debug("ScenarioManager : list tests")
        res = {}
        tests = self.__return_list_of_classes(s_t)
        for name, cls in tests:
            self.log.debug("- {0}".format(name))
            inst = cls(log = self.log)
            res[name] = []
            for p, i in inst.get_parameters().iteritems():
                for param, info in i['expected'].iteritems():
                    res[name].append({
                            "name": "{0}.{1}".format(p, param),
                            "description": info['description'],
                            "type": info['type'],
                            "values": info['values'],
                            "filters": info['filters'],
                        })
            inst.destroy()
        return res

    def list_conditions(self):
        """ Return the list of conditions as JSON
        """
        ret = []
        for cid, inst in self._instances.iteritems():
            ret.append({'cid': cid, 'name': inst['name'], 'json': inst['json']})
        return ret

    def __return_list_of_classes(self, package):
        """ Return the list of module/classes in a package
        @param package : a reference to the package that need to be explored
        @return a list of tuple ('modulename.Classname', <instance of class>)
        """
        self.log.debug("Get list of classes for package : {0}".format(package))
        res = []
        mods = pkgutil.iter_modules(package.__path__)
        for module in mods:
            self.log.debug("- {0}".format(module))
            imported_mod = importlib.import_module('.' + module[1], package.__name__)
            #get the list of classes in the module
            classes = [m for m in inspect.getmembers(imported_mod) if inspect.isclass(m[1])]
            # Filter in order to keep only the classes that belong to domogik package and are not abstract
            res.extend([(module[1] + "." + c[0], c[1]) for c in filter(
                lambda x: x[1].__module__.startswith("domogik.scenario.") and not x[0].startswith("Abstract"), classes)])
        return res


if __name__ == "__main__":
    import logging
    s = ScenarioManager(logging)
    print "==== list of actions ===="
    print s.list_actions()
    print "==== list of tests ===="
    print s.list_tests()

    print "\n==== Create condition ====\n"
    jsons = """
            {"type":"dom_condition","id":"1","IF":{"type":"textinpage.TextInPageTest","id":"5","url.urlpath":"http://cereal.sinners.be/test","url.interval":"10","text.text":"foo"},"deletable":false, "DO":{} }
                    """
    c = s.create_scenario("name", jsons)
    print "    - condition created : %s" % c
    print "    - list of instances : %s" % s.list_conditions()
