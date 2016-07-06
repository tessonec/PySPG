#! /usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################################
# :::~ Copyright (C) 2003-2010 by Claudio J. Tessone <claudio.tessone@uzh.ch>
# 
# Modified on: v2.9.2 14 May 2011
# Modified on: v2.9.1 30 May 2010
# Modified on: v2.9   15 Sep 2008
# Created  on: v0.1   09 Jan 2005
# 
# License: Distributed according to GNU/GPL Version 2 
#          (see http://www.gnu.org)
#
###########################################################################





class Iterator:
  """ class that implements a generic iterator for the spg framework
    **the implementation is minimal**. it is limited to known lists 
    of values does not support changes on the fly of the list (!)
  """

  def __init__(self, name = None, data = []):
    """ name: the label to be assigned to this iterator
      data: the set of values can be assigned to this iterator
    """
    self.name  = name
    self.data  = data
    # self.type = "."
    self.reset()
    
  def __iter__(self):
    return self

  def next(self):
    if self.__index == None:
       self.__index = 0
    else:
      self.__index += 1
       
    try:
      self.value = self.data[ self.__index ]
    except:
      raise StopIteration
    
    return self.value

  def reset(self):
    try:
      self.value = self.data[0]
      self.__index = 0
    except:
      self.value = ""
      self.__index = None

  


class IterConstant(Iterator):
  """ class that implements a generic iterator for the spg framework
    **the implementation is minimal**. it is limited to known lists 
    of values does not support changes on the fly of the list (!)
  """

  def __init__(self, name = None, data = None):
    """ name: the label to be assigned to this iterator
      data: the set of values can be assigned to this iterator
    """
    if type(data) == type([]):
        Iterator.__init__(self,name,data)
    else:
        Iterator.__init__(self,name,[data])
    self.name  = name

    self.reset()
    
  def __iter__(self):
    return self

  def next(self):
      raise StopIteration
    
  def reset(self):
    try:
      self.value = self.data[0]
      self.__index = None
    except:
      self.value = ""
      self.__index = None
    



class IterOperator(Iterator):
     """ this subclass generates the values for classes defined according to the rule
      @var_name val_min val_max step
      where @ is the operation defined for the data type. 
      var_name is the variable name
      val_min, val_max the bounds
      step  the step
      the actualization process runs according to actual_value = actual_value @ step
     """
    
     def __init__(self, name, type, limits):
       """ name: of the variable
       type: operator to be used in the operation
       limits: a 3-tuple with minimum, maximum and step values
       """
       self.name = name
       self.type = type
       data = self._parse(type, limits)
       Iterator.__init__(self,name,data)

  
     def _parse(self,it_type,limits):
        self.xmin,self.xmax,self.xstep=limits
        #xmin = eval(xmin)
        #xmax = eval(xmax)
        #xstep = eval(xstep)
        #######################################
        #   Block that raises exception in the case that iteration requested
        #   do not reaches xmax

        assert  abs(self.xmax-self.xmin) >  abs(self.xmax-eval("%s%s%s" %(self.xmin,it_type,self.xstep) ) ) , \
             "on variable '%s': '%s%s%s' does not approach to %s "%(self.name, str(self.xmin),str(it_type),str(self.xstep),str(self.xmax))
        #
        #######################################

        lsTmp=[]
        xact=self.xmin

        while((self.xmin>self.xmax) ^ (xact <= self.xmax) ): # ^ is xor in python !
            lsTmp.append(xact)
            xact=eval("%s%s%s"%(xact,it_type,self.xstep))
       
        return lsTmp

#:::~ ###################################################################
#:::~ ###################################################################


class IterMutable(Iterator):
     """ this subclass generates the values for classes defined according to the rule
      @var_name val_min val_max step
      where @ is the operation defined for the data type. 
      var_name is the variable name
      val_min, val_max the bounds
      step  the step
      the actualization process runs according to actual_value = actual_value @ step
     """
    
     def __init__(self, name, type, limit_commands, external_dict):
       """ name: of the variable
       type: operator to be used in the operation
       limits: a 3-tuple with minimum, maximum and step values
       """
       self.name = name
       self.limit_commands = limit_commands
       self.external_dict = external_dict
       self.type = type
       self.data = None
#       Iterator.__init__(self,name,data)

  
     def _parse(self,it_type,limits):
        self.xmin,self.xmax,self.xstep=limits
        #xmin = eval(xmin)
        #xmax = eval(xmax)
        #xstep = eval(xstep)
        #######################################
        #   Block that raises exception in the case that iteration requested
        #   do not reaches xmax

        assert  abs(self.xmax-self.xmin) >  abs(self.xmax-eval("%s%s%s" %(self.xmin,it_type,self.xstep) ) ) , \
             "on variable '%s': '%s%s%s' does not approach to %s "%(self.name, str(self.xmin),str(it_type),str(self.xstep),str(self.xmax))
        #
        #######################################

        lsTmp=[]
        xact=self.xmin

        while((self.xmin>self.xmax) ^ (xact <= self.xmax) ): # ^ is xor in python !
            lsTmp.append(xact)
            xact=eval("%s%s%s"%(xact,it_type,self.xstep))
       
        return lsTmp


     def reset(self):
         self._parse()
         super(IterMutable, self).reset()
#:  

#:::~ ###################################################################
#:::~ ###################################################################



#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################
#:::~ ###################################################################

class MultIterator:
  """ class that implements a generic multiterator for the spg framework.
    the values are supossed to be accessed **only** through the 
    operator[]
  """

  def __init__(self):
    self.data = []
    self.__dict = {}
    self.names = [] #ordered items
    self.__is_reset = True
    
  def add(self, spg_it):
    """ raises an AssertionError if the key is duplicated      
    """
    assert spg_it.name not in self.names , "duplicate key '%s'"%spg_it.name 
    
    assert self.__is_reset, "multiterator already initiated"
    
    self.names.append( spg_it.name )
    self.data.append( spg_it )
    self.__dict[ spg_it.name ] = spg_it.value

  def __iter__(self):
    return self

  def reset(self):
    for i in self.__dict:
      i.reset()
      self.__dict[ i.name ] = i.value
    self.__is_reset = True


  def next(self):
    if self.__is_reset:
      self.__is_reset = False
      return self.__dict

    index = len(self.data)-1
    
    while index >= 0:
      try:
        self.data[index].next()
        self.__dict[self.data[index].name] = self.data[index].value
        return self.__dict
      except StopIteration:
        self.data[index].reset()
        self.__dict[self.data[index].name] = self.data[index].value 
        index -= 1
    raise StopIteration

  def __getitem__(self, name):
      """ the values of the multiterator are supposed to be accessed 
      only by the operator[] (or by the returned value of next()
      """
#      print name, self.names
#      if name == "id":
#          return self.current_iteration_id


      assert name in self.names , "the requested variable '%s' was not found in the multiterator"%name
      return self.__dict[name]

  def get_dict(self):
      return self.__dict.copy()
      
  def items(self):
      return self.names

  def varying_items(self):
      return [i.name for i in self.data if i.__class__ != IterConstant  ]

  def constant_items(self):
      return [i.name for i in self.data if i.__class__ == IterConstant ]

  def reorder(self,new_order):
    """ the ordered list of spgiterator's names can be reshuffled with this
    """
    assert set(self.names) == set(new_order), "the origin and destination set of variables differ"
    
    self.names = new_order
    
  def position_of(self,var):
    """returns the position in the ordered list of a given variable"""
    assert var in self.names, "the requested variable was not found in the multiterator"
    
    return self.names.index(var)
    

if __name__=="__main__":

    mu = MultIterator()
    mu.add(IterOperator(name = "a",type = "*", limits = (1,8,2) ) )
    mu.add(IterOperator(name = "b", type = "+", limits = (0,2,0.5) ) )
    mu.add(IterConstant(name = "const", data = "3"))
    mu.add(IterConstant(name = "konst", data = [3]))
    mu.add(Iterator(name = "c", data=[0,-1]))
#    mu.add(SPGIterator(name = "b", data=[2,4,8]))
    for i in mu:
      print i
#    m2 = SPGIterator(name = "a", data=[1,2,4,8])
