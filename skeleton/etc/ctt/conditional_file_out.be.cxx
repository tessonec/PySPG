if(store_%ARG% ){
    
    f_%ARG%_out = new std::fstream (store_%ARG%_filename.c_str(),std::ios::out | std::ios::app );
    if( f_%ARG%_out->fail()  ) {
      std::cerr << "< " << argv[0] << " - ERROR > " ;
      std::cerr << "opening file: '" << store_%ARG%_filename ;
      std::cerr << "' for output" << std::endl;
      exit(EXIT_FAILURE);
    }
}
