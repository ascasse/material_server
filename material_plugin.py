#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Base class for material server plugins.
    On startup, the server looks for classes that extends this one
    and calls load method.
"""


class MaterialPlugin(object):
    """ Base class for material server application plugins """

    def load(self, data):
        """ Load material data from given argument """
        raise NotImplementedError
