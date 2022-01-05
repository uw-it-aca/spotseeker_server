# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

'''
Tells unit test framework to use full assertion failure messages,
i.e. it will include both the standard 'a != b' messages as well
as the custom message.
'''

import unittest
unittest.TestCase.longMessage = True
