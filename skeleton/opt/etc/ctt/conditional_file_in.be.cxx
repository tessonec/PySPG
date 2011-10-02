if(load_%ARG% ){
    f_%ARG%_in = new std::fstream (load_%ARG%_filename.c_str(),std::ios::in);
    if( f_%ARG%_in->fail()  ) {
      std::cerr << "< " << argv[0] << " - ERROR > " ;
      std::cerr << "opening file: '" << load_%ARG%_filename ;
      std::cerr << "' for input"<< std::endl;
      exit(EXIT_FAILURE);
    }
}

