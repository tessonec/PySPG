/***************************************************************************
                          main.cpp  -  description
                             -------------------
    begin                : Mon May 12 2003
    copyright            : (C) 2003 by Claudio Juan Tessone
    email                : tessonec@imedea.uib.es
 ***************************************************************************/


#include "base.h"


#include<iostream>
#include<cmath>

#include <dranxor.h>

using namespace std;

int main(int argc, char *argv[])
{
  using namespace CTGlobal;

  initialize_program( argc,  argv );

  double X = 0;
  double S = 0;
  
  for(long i=0;i<  simulation_timesteps;i++){
    double pos_change = sqrt( D ) * rt_rand_gaussian() +  drift ; 
    X+=pos_change;
    S += pos_change*pos_change; 
  }
  
  
  std::cout << X << "\t";
  std::cout << S << std::endl;
  return EXIT_SUCCESS;

}


