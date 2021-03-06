from django.conf import settings

import insanity
import insanity.utils
from insanity.client import TesterClient
from insanity.testrun import TestRun
from insanity.generators.filesystem import URIFileSystemGenerator

from insanity.storage.sqlite import SQLiteStorage
from insanity.log import debug

import gobject

# Custom insanity test client. Extends the
# insanity TesterClient to split the "stop test" and "quit
# testing environment" into two separate methods (stop() and
# quit(), respectively), so there's only one environment
# for the web server, that can run multiple tests.
class Client(TesterClient):
    """
    Custom insanity test client used by the web service.
    """

    __software_name__ = 'Insanity web service'

    def __init__(self, runner):
        self.runner = runner
        self.current_run = None
        super(Client, self).__init__(singlerun=True)

    def stop(self):
        debug("Stopping...")
        if not self._running:
            debug("We were already stopping...")
            return
        self._running = False
        try:
            if self._current:
                self._current.abort()
        except Exception, e:
            debug("Exception while aborting the current test: " + str(e))

    def quit(self):
        """
        Quit the client
        """
        debug("Quitting...")

        if self._running:
            self.stop()

        try:
            self._storage.close(self._exit)
        except:
            self._exit()

    def clearTestRuns(self):
        if self._running:
            self.stop()
        self._testruns = []

    def test_run_start(self, run):
        self.current_run = run
        run.connect('single-test-start', self.single_test_start_cb)
        run.connect('single-test-done', self.single_test_done_cb)

    def test_run_done(self, testrun):
        debug("Test run done")
        self.runner.test_run_done()

    def single_test_start_cb(self, run, test, iteration):
        if iteration == 1:
            debug("Test started: " + repr(test))
            test.connect('check', self.test_check_cb)

    def single_test_done_cb(self, run, test):
        debug("Test done: " + repr(test))

    def test_check_cb(self, test, item, validated):
        run = self.current_run
        run_index = run.getCurrentBatchPosition() - 1
        run_length = run.getCurrentBatchLength()
        test_pct = test.getSuccessPercentage()

        pct = int((100.0 * run_index + test_pct) / run_length)
        self.runner.test_progress_cb(run, test, pct, test_pct)

class Runner(object):

    _singleton = None

    def __init__(self):
        assert Runner._singleton is None, "Please use get_runner()."
        Runner._singleton = self

        self.client = Client(self)
        self._clear_info()

        storage = SQLiteStorage(path=settings.DATABASES['default']['NAME'])
        self.client.setStorage(storage)

    def _clear_info(self):
        self.test_name = None
        self.test_folder = None
        self.current_test = None
        self.current_run = None
        self.current_test_progress = None
        self.current_run_progress = None
        self.current_item = None

    def get_test_names(self):
        tests = [ t.__test_name__ for t in insanity.utils.list_available_tests() ]
        tests.extend(t.__test_name__ for t in insanity.utils.list_available_scenarios())
        return tests

    def start_test(self, test, folder, extra_arguments):
        self.run = TestRun(maxnbtests=1)
        self.test_metadata = insanity.utils.get_test_metadata(test)
        args = {
            'uri': URIFileSystemGenerator(paths=[folder], recursive=True)
        }
        args.update(extra_arguments)

        self.run.addTest(self.test_metadata, arguments=args)
        self.client.addTestRun(self.run)

        self.current_run = self.run
        self.current_run_progress = 0
        self.test_name = test
        self.test_folder = folder
        debug("Running test: " + test)
        self.client.run()

    def stop_test(self):
        debug("Stopping test")
        self.client.stop()

    def test_progress_cb(self, run, test, pct, test_pct):
        self.current_run = run
        self.current_test = test
        self.current_run_progress = pct
        self.current_test_progress = test_pct

    def test_run_done(self):
        debug("Test run done")
        self._clear_info()
        self.client.clearTestRuns()

    def get_progress(self):
        return self.current_run_progress

    def get_test_name(self):
        return self.test_name

    def get_test_folder(self):
        return self.test_folder

    def quit(self):
        self.client.quit()

def get_runner():
    """Get (or create) the Runner singleton."""
    if Runner._singleton is None:
        Runner()
    return Runner._singleton
