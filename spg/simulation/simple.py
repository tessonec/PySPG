from spg.base import MultIteratorParser
import spg.utils as utils
import os.path


import sys


class MultIteratorList(MultIteratorParser):

    def __init__(self, argv):



        full_name, self.path, self.base_name, extension = utils.translate_name(argv[1])


#        sim_name = "%s/%s.spg" % (self.path, self.base_name)

        MultIteratorParser.__init__(self, open(f"{self.base_name}.spg"))

        self.command, ext = os.path.splitext(argv[0])
        print(self.command, self.base_name)


        if not utils.check_params.consistency(self.command, self):
            utils.newline_msg("ERR", "simulation configuration is not consistent.")
            sys.exit(1)

#        print(self.base_name)
        ret = utils.read_input_configuration(f"{self.command}.input")

        self.variable_defaults = {}
        for k in ret.items():
#            if k.var_type != "choice":
#                self.variable_defaults[k] = eval( f"{k.var_type}({default})" )
#            else:
             self.variable_defaults[k] = eval( f"{k.var_type}({k.default})" )

        print(self.variable_defaults)





        self.stdout_contents = utils.read_output_configuration(self.command)



#        print(self.names)
#        print(self.stdout_contents)


    def produce_values(self):
        return [ dict({j:self[j] for j in self.names } ) for i in self ]








