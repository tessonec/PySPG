from spg.base import MultIteratorParser
import spg.utils as utils
import os.path


import sys


class MultIteratorList(MultIteratorParser):
    # In this clase:
    # - self.command     contains the name of the executed file (from which input and stdout are derived)
    # - self.base_name   contains the name of the simulation (iterated) parameters
    # - self.default_parameters is the dict (SPGSettings) of default values of all parameters
    # - self.input_configuration     is the dict (SPGSettings) of the input configuration
    # - self.stdout_configuration    is the dict (SPGSettings) of the output configuration
    # = self.names =     contains all variables in the right order

    def __init__(self, argv):


        full_name, self.path, self.base_name, extension = utils.translate_name(argv[1])

        MultIteratorParser.__init__(self, open(f"{self.base_name}.spg"))

        self.command, ext = os.path.splitext(argv[0])



        if not utils.check_params.consistency(self.command, self):
            utils.newline_msg("ERR", "simulation configuration is not consistent.")
            sys.exit(1)

        self.input_configuration = utils.read_input_configuration(f"{self.command}.input")

        self.default_parameters =utils.SPGSettings()

        for k,v in self.input_configuration.items():

            if v.var_type != "str":
                self.default_parameters[k] = eval(f"{v.var_type}({v.default})")
            else:
                self.default_parameters[k] =  v.default

        self.stdout_configuration = utils.read_output_configuration(self.command)



#        print(self.names)
#        print(self.stdout_contents)


    def generate_ensemble(self, all = False):
        # generates all possible combinations

        ret = [ utils.SPGSettings({j:self[j] for j in self.names } ) for i in self ]

        if all:
            additional_values = { k: self.default_parameters[k]
                                 for k in self.default_parameters
                                 if k not in self.names }
            for _ in ret:
                _.update( additional_values )

        return ret

    def get_csv_header(self, only_varying = True):
        if only_varying:
            return self.varying_parameters() + list(self.stdout_configuration.keys())
        else:
            return self.names + list( self.stdout_configuration.keys() )

    def get_parameters(self, all = False):
        ret =  utils.SPGSettings({j:self[j] for j in self.names } )

        if all:
            additional_values = { k: self.default_parameters[k]
                                 for k in self.default_parameters
                                 if k not in self.names }

            ret.update( additional_values )
        return ret

    def get_row(self, return_values, only_varying = True):
        assert set(return_values.keys()) == set( self.stdout_configuration.keys() )

        ret = return_values.copy()

        if only_varying:
            ret.update( {_:self[_] for _ in self.varying_parameters() }  )
#            return self.varying_parameters() + list(self.stdout_configuration.keys())
        else:
            ret.update({_: self[_] for _ in self.names })
#            return self.names + list( self.stdout_configuration.keys() )

        return ret








