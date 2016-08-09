'''
Tells unit test framework to use full assertion failure messages,
i.e. it will include both the standard 'a != b' messages as well
as the custom message.
'''

import unittest
unittest.TestCase.longMessage = True
