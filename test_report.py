# Python code to demonstrate working of unittest
import report
import unittest


class Testconnection(unittest.TestCase):

    def setUp(self):
        pass

    # Returns True if the string contains 4 a.
    def test_get_commit_url(self):
        url = report._get_commits_url('a', 'b', 'c', 'd', 'e')
        self.assertEqual(url, 'a/repos/b/c/commits?per_page=e&sha=d')

    def test_connect_github_error(self):
        status, response = report._connect_github(
            'https://github.com/ranodm', '')
        self.assertEqual(status, None)
        self.assertEqual(response, {})

    def test_connect_github(self):
        status, response = report._connect_github(
            'https://api.github.com/repos/srinivasreddykesari/yarnball/commits?per_page=1&sha=feature-bucket-info', '')
        self.assertEqual(status, 200)
        self.assertNotEqual(response, {})

    def test_get_branch_commits(self):
        status, response = report.get_branch_commits("https://api.github.com",
                                                     "srinivasreddykesari", "yarnball", "feature-bucket-info", 1, '')
        self.assertEqual(status, True)
        self.assertNotEqual(response, {})   


if __name__ == '__main__':
    unittest.main()
