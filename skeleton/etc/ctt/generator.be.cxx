
  std::cerr << "< " << argv[0] << " - MESSAGE > " ;
  std::cerr << "chosen generator '" << %ARG%_gen << "' for %ARG% " << std::endl;
  
  if (%ARG%_gen=="CONSTANT" ){
      gen_%ARG%=new ConstantGenerator(%ARG%);
  } else if (%ARG%_gen=="GAUSSIAN" ){
      gen_%ARG%=new GaussianGenerator(%ARG%,%ARG%_var);
  } else if (%ARG%_gen=="LORENTZ" ){
//      gen_%ARG%=new LorentzianGenerator(%ARG%,%ARG%_var,size);
//  } else if (%ARG%_gen=="UNIFORM" ){
      gen_%ARG%=new LorentzianGenerator(%ARG%,%ARG%_var);
  } else if (%ARG%_gen=="UNIFORM" ){
      gen_%ARG%=new UniformGeneratorByVariance(%ARG%,%ARG%_var);
  } else{
    std:: cerr << "< " << argv[0] << " - ERROR > " ;
    std::cerr << "could not alloc '%ARG%' generator" << std::endl;
    exit(EXIT_FAILURE);
  }

