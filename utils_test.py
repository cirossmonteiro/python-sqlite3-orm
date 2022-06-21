from unittest import TestCase

def remove_extra_space(s):
    s = ' '.join(s.split())
    return s

def assertEqualStringQueries(self, first, second, msg=None):
    """
    Compare two query strings
    """
    self.assertEqual(
        remove_extra_space(first),
        remove_extra_space(second),
        msg
    )


# custom assertion
TestCase.assertEqualStringQueries = assertEqualStringQueries