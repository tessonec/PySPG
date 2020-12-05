from spg.base import MultIteratorParser
import spg.utils as utils


import sys


class MultIteratorList(MultIteratorParser):

    def __init__(self, db_name):
        full_name, self.path, self.base_name, extension = utils.translate_name(db_name)

        self.db_name = "%s/%s.spgql" % (self.path, self.base_name)
        sim_name = "%s/%s.spg" % (self.path, self.base_name)

        MultIteratorParser.__init__(self, open(sim_name))

        if not utils.check_params.consistency(self.command, self):
            utils.newline_msg("ERR", "simulation configuration is not consistent.")
            sys.exit(1)

        self.command
        ret = utils.read_input_configuration(f"{}.input")

        self.variable_defaults = {}
        for k,(family, var_type, default) in ret.items():
            if var_type is not "choice":
                self.variable_defaults[k] = eval( f"{var_type}({default})" )
            else:
                self.variable_defaults[k] = eval( f"{var_type}({default[0]})" )

        print(self.variable_defaults)





        self.stdout_contents = check_params.read_output_configuration(self.command)



#        print(self.names)
#        print(self.stdout_contents)


    def produce_values(self):
        return [ dict({j:self[j] for j in self.names } ) for i in self ]








