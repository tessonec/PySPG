from spg.base import MultIteratorParser
import spg.utils as utils

from spg.utils import check_params, import_input_variables



class MultIteratorList(MultIteratorParser):

    def __init__(self, db_name):
        full_name, self.path, self.base_name, extension = utils.translate_name(db_name)

        self.db_name = "%s/%s.spgql" % (self.path, self.base_name)
        sim_name = "%s/%s.spg" % (self.path, self.base_name)

        MultIteratorParser.__init__(self, open(sim_name))

        if not check_params.consistency(self.command, self):
            utils.newline_msg("ERR", "simulation configuration is not consistent.")
            sys.exit(1)



        self.stdout_contents = check_params.contents_in_output(self.command)



#        print(self.names)
#        print(self.stdout_contents)


    def produce_values(self):
        return [ dict({j:self[j] for j in self.names } ) for i in self ]

    def params(self, d):
        return






