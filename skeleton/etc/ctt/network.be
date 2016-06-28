choice:string:%ARG%_network:"NONE","1D","2D","3D","4D","SW1D","SW2D","FULL","SCALE_FREE","BARABASI","RANDOM":network topoogy for %ARG%
val:unsigned:%ARG%_k_1d:1:(networks 1D) number of neighbors at each side
val:unsigned:%ARG%_k_ba:1:(network BA) number of links attached each time step
val:double:%ARG%_p_sw:0.:(network SW) rewiring probability
flag:%ARG%_non_fixed_sw:(network SW) sets whether the random links are added or not
val:double:%ARG%_alpha_sf:2.:(network SF) power-law exponent
val:double:%ARG%_p_random:2.:(network RND) probability of establishing a link
flag:scramble_%ARG%_network:sets whether it is needed to scramble the network
val:double:%ARG%_p_scramble:1:probability of rewiring while scrambling
flag:store_%ARG%_network:sets whether to store the network %ARG%
val:string:store_%ARG%_network_filename:"%ARG%.out.net":file name to store the network %ARG% in
flag:load_%ARG%_network:sets whether to load the network %ARG%
val:string:load_%ARG%_network_filename:"%ARG%.in.net":file name to load the network %ARG% from
