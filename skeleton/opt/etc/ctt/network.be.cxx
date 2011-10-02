 if(load_%ARG%_network){
      std::cerr << "< " << argv[0] << " - MESSAGE > " ;
      std::cerr << "loading: '%ARG%' network" << std::endl ;
      std::fstream fnet(load_%ARG%_network_filename.c_str(),std::ios::in);

      if(!fnet.fail()){
        %ARG%_net = NetworkGen::network_load(size, &fnet );
      } else {
        std::cerr << "< " << argv[0] << " - ERROR > " ;
        std::cerr << "opening file: '" << load_%ARG%_network_filename ;
        std::cerr << "' for input"<< std::endl;
        exit(EXIT_FAILURE);
      }
 } else {
  if(%ARG%_network=="FULL"){
    %ARG%_net= NetworkGen::FullyConnected(size);
  }
  if(%ARG%_network=="1D"){
    %ARG%_net= NetworkGen::Regular1D(size,%ARG%_k_1d);
  }
  if(%ARG%_network=="2D"){
    lint lado = (long int)(rint(sqrt(size)));
    std::cerr << "< " << argv[0] << " - MESSAGE > " ;
    std::cerr << "using: '" << lado << "' as lateral size for the square" << std::endl ;

    %ARG%_net= NetworkGen::Regular2D(size,(int)(sqrt((double)size)));
  }
  if(%ARG%_network=="3D"){
    lint lado = (long int)(rint( pow((double)size,1./3.) ));
    std:: cerr << "< " << argv[0] << " - MESSAGE > " ;
    std::cerr << "using '" << lado << "' as lateral size for the cube" << std::endl;
    %ARG%_net= NetworkGen::Regular3D(size,lado ) ;
  }
  if(%ARG%_network=="4D"){
    lint lado = (long int)(rint( pow((double)size,1./4.) ));
    std:: cerr << "< " << argv[0] << " - MESSAGE > " ;
    std::cerr << "using '" << lado << "' as lateral size for the hyper-cube" << std::endl;
    %ARG%_net= NetworkGen::Regular4D(size,lado ) ;
  }
  if(%ARG%_network=="BARABASI"){
    %ARG%_net= NetworkGen::BarabasiAlbert(size,%ARG%_k_ba);
  }
  if(%ARG%_network=="SW1D" ){
    %ARG%_net= NetworkGen::SmallWorld1D(size,%ARG%_k_1d,%ARG%_p_sw,!%ARG%_non_fixed_sw);
  }
  if(%ARG%_network=="SW2D"  ){
    lint lado = (long int)(rint(sqrt(size)));
    std::cerr << "< " << argv[0] << " - MESSAGE > " ;
    std::cerr << "using: '" << lado << "' as lateral size" << std::endl ;
    %ARG%_net= NetworkGen::SmallWorld2D(lado ,%ARG%_p_sw,!%ARG%_non_fixed_sw);
  }
  if(%ARG%_network=="SCALE_FREE"  ){
      %ARG%_net= NetworkGen::ScaleFree(size,%ARG%_alpha_sf);
  }
  if(%ARG%_network=="RANDOM"  ){
      %ARG%_net= NetworkGen::FullyRandom(size,%ARG%_p_random);
  }
 }

  if(scramble_%ARG%_network)
    NetworkGen::scrambleNetwork(%ARG%_net,%ARG%_p_scramble);
  if(store_%ARG%_network) {
    std::fstream fnet(store_%ARG%_network_filename.c_str(),std::ios::out);
    if(!fnet.fail()){
        NetworkGen::network_dump(%ARG%_net, &fnet);
    } else {
        std::cerr << "< " << argv[0] << " - ERROR > " ;
        std::cerr << "opening file: '" << load_%ARG%_network_filename ;
        std::cerr << "' for output"<< std::endl;
        exit(EXIT_FAILURE);
      }
  }
