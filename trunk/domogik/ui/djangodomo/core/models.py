#!/usr/bin/python
#-*- encoding:utf-8 *-*

# Copyright 2008 Domogik project

# This file is part of Domogik.
# Domogik is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Domogik is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Domogik.  If not, see <http://www.gnu.org/licenses/>.

# Author : Marc Schneider <marc@domogik.org>

# $LastChangedBy: mschneider $
# $LastChangedDate: 2009-02-13 09:20:19 +0100 (ven. 13 févr. 2009) $
# $LastChangedRevision: 357 $

from django.db import models

# __unicode__ is to output a representation of the object as a unicode string
# (u"" instead of "" for Python < 3.0)


class Area(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=30)
    area = models.ForeignKey(Area)
    description = models.TextField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name


class DeviceCategory(models.Model):
    """
    Examples : temperature, heating, lighting, music, ...
    """
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Device categories"


class DeviceTechnology(models.Model):
    """
    Examples : x10, plcbus, rfxcom, ...
    """
    TYPETECHNOLOGY_CHOICES = (
            ('cpl', 'cpl'),
            ('wired_bus', 'Wired bus'),
            ('wifi', 'wifi'),
            ('wireless_bus', 'Wireless bus'),
            ('rf', 'RF'),
            ('ir', 'IR'),
    )

    name = models.CharField(max_length=30)
    description = models.TextField(max_length=80, null=True, blank=True)
    type = models.CharField(max_length=30, choices=TYPETECHNOLOGY_CHOICES)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Device technologies"


class Device(models.Model):
    TYPE_CHOICES = (
            ('appliance', 'Appliance'),
            ('lamp', 'Lamp'),
            ('music', 'Music'),
    )

    name = models.CharField(max_length=30)
    serialNb = models.CharField("Serial Nb", max_length=30, null=True,
            blank=True)
    reference = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=30)
    description = models.TextField(max_length=80, null=True, blank=True)
    technology = models.ForeignKey(DeviceTechnology)
    # This is NOT user-defined
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    # This is user-defined
    category = models.ForeignKey(DeviceCategory)
    room = models.ForeignKey(Room)
    canGiveFeedback = models.BooleanField("Can give feedback", default=False)
    isResetable = models.BooleanField("Is resetable", default=False)

    def isLamp(self):
        return self.type.lower() == 'lamp'

    def isAppliance(self):
        return self.type.lower() == 'appliance'

    def canBeSwitchedOnOff(self):
        return self.type.lower() == 'appliance' or self.type.lower() == 'lamp'

    def canHaveInputValue(self):
        # TODO : Add here supported devices
        return self.type.lower() == 'lamp'

    def __unicode__(self):
        return u"%s - %s (%s)" % (self.name, self.address, self.reference)


class DeviceProperty(models.Model):
    VALUETYPE_CHOICES = (
            ('BOOLEAN', 'BOOLEAN'),
            ('ALPHANUM', 'ALPHANUM'),
    )
    VALUE_UNIT_CHOICES = (
            ('%', '%'),
    )

    key = models.CharField(max_length=30)
    value = models.CharField(max_length=80)
    valueType = models.CharField("Value type", max_length=20,
            choices=VALUETYPE_CHOICES)
    valueUnit = models.CharField("Value unit", max_length=30,
            choices=VALUE_UNIT_CHOICES)
    isChangeableByUser = models.BooleanField("Can be changed by user")
    device = models.ForeignKey(Device)

    class Meta:
        unique_together = ("key", "device")
        verbose_name_plural = "Device properties"

    def __unicode__(self):
        return u"%s = %s" % (self.key, self.value)


class DeviceCmdLog(models.Model):
    date = models.DateTimeField()
    value = models.CharField(max_length=80)
    comment = models.CharField(max_length=80, null=True, blank=True)
    isSuccessful = models.BooleanField("Successful")
    device = models.ForeignKey(Device)

    def __unicode__(self):
        return u"%s: %s (success=%s)" % (self.date, self.value,
                self.isSuccessful)


class StateReading(models.Model):
    device = models.ForeignKey(Device)
    value = models.FloatField()
    date = models.DateTimeField()


class ApplicationSetting(models.Model):
    # TODO : make sure there is only one line for this model
    # See : http://groups.google.com/group/django-users/browse_thr
    # ead/thread/d44a9417a81c4860?hl=en
    # Or : http://docs.djangoproject.com/en/dev/ref/mod
    # els/instances/#ref-models-instances
    simulationMode = models.BooleanField("Simulation mode", default=True)
    adminMode = models.BooleanField("Administrator mode", default=True)
    debugMode = models.BooleanField("Debug mode", default=True)


class Music(models.Model):
    STATE_CHOICES = (
            ('play', 'Play'),
            ('pause', 'Pause'),
            ('stop', 'Stop'),
    )
    room = models.ForeignKey(Room)
    title = models.CharField(max_length=150)
    time = models.TimeField()
    current_time = models.TimeField()
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
