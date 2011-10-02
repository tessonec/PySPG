#ifndef RT_RANDOM
#define RT_RANDOM

#include <ctime>
#include <cmath>

extern "C" void dran_ini_(long int &iseed);

extern "C" long int i_dran_(long int &n); 

extern "C" double dran_u_(); 

extern "C" double dran_g_();


//:::~ The following are the functions to be used

inline void rt_rand_init(long int iseed) { 
/** initializes the random number generator using 
 * iseed as seed
 */
  long int n2=iseed;
  dran_ini_(n2); 
}

inline void rt_rand_timeinit() { 
/** initializes the random number generator using 
 * the current time as seed
 */
   long int iseed = time(0);
   dran_ini_(iseed); 
}

inline long int rt_rand_int(long int n) { 
/** returns an integer number uniformly distributed between 0 and n-1
 */
   long int n2=n;
   return i_dran_(n2); 
}

inline double rt_rand_uniform() { 
/** returns a double precision number uniformly distributed between 0 and 1
 */
  return dran_u_();   
}

inline double rt_rand_gaussian() { 
/** returns an integer number distributed according to a normal Gaussian distribution
 */
  return dran_g_(); 
}

inline double rt_rand_power_law(double alpha){
/** returns a double number distributed according to a power law with exponent -alpha
 */
  double random = dran_u_();
  return pow(random,-1./alpha);
 
}

#endif
