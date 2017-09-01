__author__ = 'Patrick Liao'

import os
import re
import time

DEFAULT_SHELL_TIMEOUT = 1000

from tests.testbase.decorators import version

from tests.testbase.testbase import TestBase
from automaton_drivers.shelldriver import ShellDriver
from automaton_drivers.tools import NodeToolParser, NodeToolUtil


class NodetoolSJKTest(TestBase):
    '''
    If the cluster is launched through ctool, you can open the webpage at hostname:8081 to view and check the nodetool sjk
    data from the JMX Management Console
    '''

    @version(min='4.8.0')
    def run_nodetool(self, options, custom_timeout=DEFAULT_SHELL_TIMEOUT):
        with ShellDriver(NodeToolParser()) as driver:
            results = driver.execute(
                "{cmd} {options}".format(cmd=NodeToolUtil().command(), options=options), timeout=custom_timeout
            )
        return results[0].raw

    def sjk_basics_test(self):
        """
        Verify that basic SJK command generally works.
        """

        # plain command
        result = self.run_nodetool('sjk')
        good_output = [
            "ttop", "Thread Top", "Displays threads from JVM process"
        ]
        for output in good_output:
            self.assertIn(output, result, "Error in sjk output: \n%s\n%s " % (result, output))

        # --help command
        result = self.run_nodetool('sjk --help')
        good_output = [
            "ttop", "Thread Top", "Displays threads from JVM process"
        ]
        for output in good_output:
            self.assertIn(output, result, "Error in sjk --help output: \n%s\n%s " % (result, output))

        # --commands command
        result = self.run_nodetool('sjk --commands')
        good_output = [
            "jps", "JPS", "Enhanced version of JDK\'s jps tool"
        ]
        for output in good_output:
            self.assertIn(output, result, "Error in sjk --commands output: \n%s\n%s " % (result, output))

    def sjk_commands_test(self):
        """
        Checking all the nodetool sjk commands work as expected.
        """

        # mxdump command
        result = self.run_nodetool('sjk mxdump -q java.lang:type=GarbageCollector,name=*')
        good_output = [
            "beans", "memoryUsageAfterGc", "java.lang:type=GarbageCollector,name=G1 Old Generation"
        ]
        for output in good_output:
            self.assertIn(output, result, "Error in sjk mxdump output: \n%s\n%s " % (result, output))

        # ttop command
        with ShellDriver() as sh:
            sh.execute("nodetool sjk ttop -n 5 &> ttopOutput.log &")
            time.sleep(10)
            sh.execute('kill $(jps | grep "{nodetool}" | cut -d " " -f 1)'.format(nodetool="NodeTool"))
            f = open("ttopOutput.log", "r")
            result = f.read()
            f.close()

        good_output = [
            "Process summary", "process cpu", "thread count"
        ]
        for output in good_output:
            self.assertIn(output, result, "Error in sjk ttop output: \n%s\n%s " % (result, output))

        # hh command
        result = self.run_nodetool('sjk hh --young --sample-depth 1000ms')
        good_output = [
            "Garbage histogram for last 1s", "Total"
        ]
        for output in good_output:
            self.assertIn(output, result, "Error in sjk hh output: \n%s\n%s " % (result, output))

        # mx command
        result = self.run_nodetool('sjk mx -b com.datastax.bdp:type=analytics,name=SparkPlugin --info')
        good_output = [
            "com.datastax.bdp:type=analytics,name=SparkPlugin", "Active", "reconfigureWorker(TabularData p0)"
        ]
        for output in good_output:
            self.assertIn(output, result, "Error in sjk mx output: \n%s\n%s " % (result, output))

        # jps command
        result = self.run_nodetool('sjk jps')
        good_output_before = [
            "sjk jps"
        ]
        for output in good_output_before:
            self.assertIn(output, result, "Error in sjk jps output before: \n%s\n%s " % (result, output))

        with ShellDriver() as sh:
            sh.execute("nodetool sjk ttop -n 5 &> ttopOutput.log &")
            time.sleep(10)

            result = sh.execute('nodetool sjk jps')
            good_output_mid = [
                "sjk jps", "sjk ttop -n 5"
            ]
            for output in good_output_mid:
                self.assertIn(output, result[0].raw, "Error in sjk jps output mid: \n%s\n%s " % (result, output))

            sh.execute('kill $(jps | grep "{nodetool}" | cut -d " " -f 1)'.format(nodetool="NodeTool"))
            time.sleep(10)

            result = sh.execute('nodetool sjk jps')
            good_output_after = [
                "sjk jps"
            ]
            for output in good_output_after:
                self.assertIn(output, result[0].raw, "Error in sjk jps output after: \n%s\n%s " % (result, output))

                # stcap command

                # stcpy command

                # ssa command
