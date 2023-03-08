# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 12:31:20 2022

@author: Darshan Rathod
"""


import numpy as _np
import pandas as _pd
import time as _time
import pickle as _pickle

from alicat import FlowController as _fc


class mfc(_fc):
    
    def __init__(self,port='COM5',address='A',name='mfc',task_type='mfc'):
        super().__init__(port=port,address=address)
        
        self._info = None
        self._data_units = None
        self.name = name
        self.task_type = task_type.lower()
    
    def __repr__(self):
        return f'mass flow controller'
    
    def __type__(self):
        return 'mass flow controller object'
    

    @property
    def is_closed(self):
        return not(self.open)
    
    def read_n(self,n=1,sleep_time=0):
        d1 = _pd.DataFrame()
        for i in range(n):
            d1 = _pd.concat([d1,_pd.DataFrame(self.get(),index=[i])])
            _time.sleep(sleep_time)
        d1.columns = [self.name+'_'+ky for ky in d1.keys()]
        self.data = d1
        return d1
        
    def read(self,tries=30):
        i = 0
        while i < tries:
            try:
                d1 = self.read_n(n=1)
                return d1
            except:
                pass
            i = i + 1
        return
    
    def set_SLPM(self,slpm=0,tries=30):
        i = 0
        while i < tries:
            try:
                self.set_flow_rate(slpm)
                return
            except:
                pass
            i = i + 1
        return




    @property
    def info(self):
        if self._info is None:
            dict1 = {
                'pressure':'Upstream pressure in PSIA',
                'temperature':'gas temperature in deg C',
                'volumetric_flow':'LPM',
                'mass_flow':'SLPM',
                'setpoint':'set point in SLPM',
                'gas':'selected gas media',
                'control_point':'None',
                }
            return dict1
        else:
            return self._info
        
    @info.setter
    def info(self,dict1):
        self._info = dict1
    
    @property
    def data_units(self):
        if self._data_units is None:
            dict1 = {
                'pressure':'PSIA',
                'temperature':'deg C',
                'volumetric_flow':'LPM',
                'mass_flow':'SLPM',
                'setpoint':'SLPM',
                'gas':'string',
                'control_point':'None',
                }            
            return dict1
        else:
            return self._data_units
    
    @data_units.setter
    def data_units(self,dict1):
        self._data_units = dict1
    