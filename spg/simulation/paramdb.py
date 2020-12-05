# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:23:41 2011

@author: Claudio Tessone <claudio.tessone@uzh.ch>

Implementation of the paramaters.dat in the form of a database
"""

import spg.utils as utils
import spg.utils.check_params as check_params

from spg.base import MultIteratorParser, IterConstant
#from base.iterator import *

from spg import database_version

import sys, os.path
import sqlite3 as sql
import csv

from collections import namedtuple

class SPGConflictingValue(Exception):
    """Raised when the DB has a value different from the one that should be set

    Attributes:
        key      -- 
        previous -- value found in the DB
        current  -- value attempted to be set in the DB
    """

    def __init__(self, key, previous, value):
        self.key = key
        self.previous = previous
        self.value = value

        utils.newline_msg("ERR","conflict in %s name (in db '%s', in param '%s')"%(key, previous, value ))


class MultIteratorDBBuilder(MultIteratorParser):
    """Generates a DB file with the representation of the parameters"""

    def __init__(self, db_name, timeout=5):
        full_name, self.path, self.base_name, extension = utils.translate_name(db_name)

        self.db_name = "%s/%s.spgql" % (self.path, self.base_name)
        sim_name = "%s/%s.spg" % (self.path, self.base_name)

        MultIteratorParser.__init__(self, open(sim_name))
        #   print self.data
        # self.path, foo = os.path.split( os.path.abspath(db_name) )
        # self.base_name, foo = os.path.splitext( foo )
        #    print  check_params.consistency(self.command, self)
        if not check_params.consistency(self.command, self):
            utils.newline_msg("ERR", "simulation configuration is not consistent.")
            sys.exit(1)

        all_outputs = check_params.read_output_configuration(self.command)

        self.stdout_contents = dict()
        for k in all_outputs:
            table=k.output_table
            if table not in self.stdout_contents.leys():
                self.stdout_contents[ table ] = k






        self.connection = sql.connect(self.db_name, timeout=timeout, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def check_and_insert_information(self, key, expected_value=None, do_not_compare=False):
        # :::~ Check whether the data found in the database and expected, coincides
        # :::~ if expected_value is None,

        self.cursor.execute("SELECT value FROM information WHERE key = ?", (key,))
        prev_val = self.cursor.fetchone()
        if prev_val is not None:
            prev_val, = prev_val

        if prev_val and expected_value is not None:
            if str(prev_val) != str(expected_value):
                raise SPGConflictingValue(key, prev_val, expected_value)
        else:
            self.cursor.execute("INSERT INTO information (key,value) VALUES (?,?)", (key, expected_value))
        self.connection.commit()

    def init_db(self):
        #:::~ Table with the information related to the database
        self.cursor.execute("CREATE TABLE IF NOT EXISTS information "
                            "(id INTEGER PRIMARY KEY, key CHAR(64), value CHAR(128))"
                            )

        self.check_and_insert_information('version', database_version)
        self.check_and_insert_information('command', self.command)
        self.check_and_insert_information('path', self.path)
        self.check_and_insert_information('base_name', self.base_name)

        #:::~ Table with the defined entities
        self.cursor.execute("CREATE TABLE IF NOT EXISTS entities "
                            "(id INTEGER PRIMARY KEY, name CHAR(64), varies INTEGER)"
                            )

        self.cursor.execute("SELECT COUNT(*) FROM entities ")
        n_items = self.cursor.fetchone()
        if n_items[0] == 0:  # table has not been filled
            for i in self.data:
                varies = 1 if (i.__class__ != IterConstant) else 0
                self.cursor.execute("INSERT INTO entities (name, varies) VALUES (?,?)", (i.name, varies))
        else:
            self.cursor.execute("SELECT name FROM entities ")
            entities = set([i[0] for i in self.cursor])
            s_names = set(self.names)

            if entities != set(self.names):
                utils.newline_msg("ERR", "parameter (was %s, is %s)" % (entities, s_names))
                sys.exit(1)

        self.connection.commit()

        elements = "CREATE TABLE IF NOT EXISTS values_set (id INTEGER PRIMARY KEY,  %s )" % (
            ", ".join(["%s CHAR(64) " % i for i in self.names]))
        # print elements
        self.cursor.execute(elements)

        elements = "INSERT INTO values_set ( %s ) VALUES (%s)" % (
        ", ".join(["%s " % i for i in self.names]), ", ".join("?" for i in self.names))

        # :::~ (CT) Index creation code
        for i in self.data:

            if i.__class__ == IterConstant: continue

            self.cursor.execute("CREATE INDEX IF NOT EXISTS idxvs_%s_id ON values_set (%s) " % (i.name, i.name))

        self.possible_varying_ids = []
        for i in self:
            self.cursor.execute(elements, [
                utils.replace_values(self[j], self, vars_to_skip=set(['spg_uid', 'spg_vsid', 'spg_rep'])) for j in
                self.names])
            self.possible_varying_ids.append(self.cursor.lastrowid)
        self.connection.commit()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS output_tables (id INTEGER PRIMARY KEY, name CHAR(128) , column CHAR(128) )")

        for results_table in list(self.stdout_contents.keys()):
            table_contents = self.stdout_contents[results_table]
            # self.number_of_columns = 0
            # for ic, iv in table_contents:
            #     if iv["type"] == "xy":
            #         self.number_of_columns += 1
            #     if iv["type"] == "xydy":
            #         self.number_of_columns += 2

            results = "CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY, spg_uid INTEGER, spg_vsid INTEGER, spg_rep INTEGER, %s, FOREIGN KEY(spg_uid) REFERENCES run_status(id), FOREIGN KEY(spg_vsid) REFERENCES values_set(id))" % (
            results_table, ", ".join(["%s %s" % (ic, iv["datatype"]) for ic, iv in table_contents]))
            self.cursor.execute(results)
        self.connection.commit()

        for results_table in list(self.stdout_contents.keys()):
            #           self.cursor.execute("INSERT INTO output_tables ( name, column ) VALUES (?, ?)",( results_table, 'spg_runid' ) )
            table_contents = self.stdout_contents[results_table]
            for ic, iv in table_contents:
                self.cursor.execute("INSERT INTO output_tables ( name, column ) VALUES (?, ?)", (results_table, ic))

        self.connection.commit()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS run_status (id INTEGER PRIMARY KEY, spg_vsid INTEGER, spg_rep INTEGER, status CHAR(1), run_time FLOAT, "
            "FOREIGN KEY (spg_vsid) REFERENCES values_set(id) )")
        self.connection.commit()

    def fill_status(self, repeat=1):

        self.check_and_insert_information('repeat', repeat)
        for i_repeat in range(repeat):

            for i_id in self.possible_varying_ids:
                #:::~ status can be either 
                #:::~    'N': not run
                #:::~    'R': running
                #:::~    'D': successfully run (done)
                #:::~    'E': run but with non-zero error code
                self.cursor.execute("INSERT INTO run_status ( spg_vsid, spg_rep, status ) VALUES (?,?,?)",
                                    (i_id, i_repeat, 'N'))

        self.connection.commit()








#    def clean_status(self):
#        """Sets the run_status to None of all the run processes"""
#        self.cursor.execute('UPDATE run_status SET status = "N" WHERE status ="R"')
#        self.connection.commit()
#
#    def clean_all_status(self):
#        """Sets the run_status to None of all the processes"""
#        self.cursor.execute('UPDATE run_status SET status = "N" ')
#        self.connection.commit()


#===============================================================================
#     cursor.execute("CREATE TABLE IF NOT EXISTS revision_history "
#                "( id INTEGER PRIMARY KEY, revision INTEGER, author CHAR(64), date CHAR(64), "
#                "  size INTEGER, number_of_files INTEGER, modified_files INTEGER, "
#                "  affected_lines_previous INTEGER , affected_lines_next INTEGER, "
#                "  removed_lines INTEGER, added_lines INTEGER, "
#                "  affected_bytes_previous INTEGER, affected_bytes_next INTEGER"
#                "   )"
#                )
# 
# 
#     cursor.execute("CREATE TABLE IF NOT EXISTS modified_files "
#                "( id INTEGER PRIMARY KEY, revision INTEGER, file_name CHAR(256))"
#                )
